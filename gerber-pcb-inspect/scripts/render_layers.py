#!/usr/bin/env python3
"""批量渲染 Gerber 各层为 PNG（供视觉模型看图分析）。

用法：
    python render_layers.py <gerber 目录或 zip> <输出目录> [--dpi 200]

每层一张 PNG，配色按层角色选（铜层 COPPER、阻焊 SOLDER_MASK、丝印 SILK、
钢网 PASTE_MASK、外形/机械 DEFAULT_GRAYSCALE）。同时写 manifest.json
（每层文件、角色、外框 mm、图片像素）。单层渲染失败记 error 并继续。
依赖 pygerber==2.4.3（自带 Pillow）。只读原文件。
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

ROLE_SCHEME = {
    "Top Copper": "COPPER", "Bottom Copper": "COPPER",
    "Top Solder Mask": "SOLDER_MASK", "Bottom Solder Mask": "SOLDER_MASK",
    "Top Silkscreen": "SILK", "Bottom Silkscreen": "SILK",
    "Top Paste": "PASTE_MASK", "Bottom Paste": "PASTE_MASK",
}

# 与 gerber_inventory.py 同一份映射（独立复制，避免跨脚本 import）
EXT_ROLE = {
    "GTL": "Top Copper", "GBL": "Bottom Copper",
    "G1": "Inner Copper 1", "G2": "Inner Copper 2", "G3": "Inner Copper 3",
    "G4": "Inner Copper 4", "G5": "Inner Copper 5", "G6": "Inner Copper 6",
    "GTS": "Top Solder Mask", "GBS": "Bottom Solder Mask",
    "GTO": "Top Silkscreen", "GBO": "Bottom Silkscreen",
    "GTP": "Top Paste", "GBP": "Bottom Paste",
    "GM1": "Board Outline", "GML": "Board Outline",
    "GKO": "Keep-Out / Outline", "GM3": "Mechanical",
}
KICAD_ROLE = {
    "F_CU": "Top Copper", "B_CU": "Bottom Copper",
    "IN1_CU": "Inner Copper 1", "IN2_CU": "Inner Copper 2",
    "F_MASK": "Top Solder Mask", "B_MASK": "Bottom Solder Mask",
    "F_SILKS": "Top Silkscreen", "B_SILKS": "Bottom Silkscreen",
    "F_PASTE": "Top Paste", "B_PASTE": "Bottom Paste",
    "EDGE_CUTS": "Board Outline",
}
GERBER_EXTS = {"GTL", "GBL", "GTS", "GBS", "GTO", "GBO", "GTP", "GBP",
                "GM1", "GML", "GKO", "GM3", "GBR", "GER"}


def identify(path: Path) -> str | None:
    """Gerber 文件返回角色，否则 None。"""
    import re
    suffix = path.suffix.lstrip(".").upper()
    if suffix not in GERBER_EXTS and not re.fullmatch(r"G\d+", suffix) \
            and not re.fullmatch(r"GM\d+", suffix):
        return None
    parts = path.name.upper().split(".")
    if len(parts) >= 3 and parts[-1] in GERBER_EXTS and parts[-2] in KICAD_ROLE:
        return KICAD_ROLE[parts[-2]]
    role = EXT_ROLE.get(suffix)
    if role:
        return role
    if re.fullmatch(r"G\d+", suffix):
        return f"Inner Copper {suffix[1:]}"
    return f"Mechanical {suffix}"


def render_one(path: Path, out_path: Path, dpi: int, role: str) -> dict:
    import logging
    from pygerber.gerberx3.api import (
        ColorScheme, Rasterized2DLayer, Rasterized2DLayerParams,
    )
    scheme_name = ROLE_SCHEME.get(role, "DEFAULT_GRAYSCALE")
    scheme = getattr(ColorScheme, scheme_name)
    # 细线在低 dpi 下会刷屏 "zero surface" 警告，渲染期间只压到 ERROR
    _log = logging.getLogger()
    _old = _log.level
    _log.setLevel(logging.ERROR)
    try:
        layer = Rasterized2DLayer(Rasterized2DLayerParams(
            source_path=str(path), dpi=dpi, colors=scheme))
        result = layer.render()
        result.save(str(out_path))
        props = result.get_properties()
    finally:
        _log.setLevel(_old)
    bb = props.gerber_bounding_box
    from PIL import Image
    with Image.open(out_path) as im:
        px = im.size
    return {
        "role": role,
        "bbox_mm": {"min_x": float(bb.min_x.value), "min_y": float(bb.min_y.value),
                    "max_x": float(bb.max_x.value), "max_y": float(bb.max_y.value)},
        "png": out_path.name, "pixels": list(px), "dpi": dpi,
    }


def collect_inputs(target: Path) -> list[Path]:
    if target.is_file() and target.suffix.lower() == ".zip":
        tmp = Path("/tmp/gerber-render-unzip")
        with zipfile.ZipFile(target) as z:
            z.extractall(tmp)
        return sorted(p for p in tmp.rglob("*") if p.is_file())
    if target.is_file():
        return [target]
    return sorted(p for p in target.rglob("*") if p.is_file())


def main() -> int:
    ap = argparse.ArgumentParser(description="批量渲染 Gerber 各层为 PNG")
    ap.add_argument("target", help="Gerber 目录、zip 或单个文件")
    ap.add_argument("outdir", help="PNG 输出目录")
    ap.add_argument("--dpi", type=int, default=200, help="渲染 dpi（默认 200）")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = {"source": str(args.target), "dpi": args.dpi, "layers": []}
    for f in collect_inputs(Path(args.target)):
        role = identify(f)
        if role is None:
            continue
        png = outdir / (f.name + ".png")  # 用全名防 sample.gtl/sample.gbs 重名覆盖
        try:
            entry = render_one(f, png, args.dpi, role)
            entry["file"] = f.name
        except Exception as e:  # noqa: BLE001 - 单层失败不中断整批
            entry = {"file": f.name, "role": role, "error": f"{type(e).__name__}: {e}"}
        manifest["layers"].append(entry)
    (outdir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
