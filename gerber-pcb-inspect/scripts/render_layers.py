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
from pathlib import Path

from _common import collect_inputs, identify, suppress_pygerber_warnings

ROLE_SCHEME = {
    "Top Copper": "COPPER", "Bottom Copper": "COPPER",
    "Top Solder Mask": "SOLDER_MASK", "Bottom Solder Mask": "SOLDER_MASK",
    "Top Silkscreen": "SILK", "Bottom Silkscreen": "SILK",
    "Top Paste": "PASTE_MASK", "Bottom Paste": "PASTE_MASK",
}


def render_one(path: Path, out_path: Path, dpi: int, role: str) -> dict:
    from pygerber.gerberx3.api import (
        ColorScheme, Rasterized2DLayer, Rasterized2DLayerParams,
    )
    scheme_name = ROLE_SCHEME.get(role, "DEFAULT_GRAYSCALE")
    scheme = getattr(ColorScheme, scheme_name)
    with suppress_pygerber_warnings():
        layer = Rasterized2DLayer(Rasterized2DLayerParams(
            source_path=str(path), dpi=dpi, colors=scheme))
        result = layer.render()
        result.save(str(out_path))
        props = result.get_properties()
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


def _unique_png_path(outdir: Path, filename: str, used: set[str]) -> Path:
    candidate = f"{filename}.png"
    idx = 2
    while candidate in used:
        candidate = f"{filename}.{idx}.png"
        idx += 1
    used.add(candidate)
    return outdir / candidate


def main() -> int:
    ap = argparse.ArgumentParser(description="批量渲染 Gerber 各层为 PNG")
    ap.add_argument("target", help="Gerber 目录、zip 或单个文件")
    ap.add_argument("outdir", help="PNG 输出目录")
    ap.add_argument("--dpi", type=int, default=200, help="渲染 dpi（默认 200）")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = {"source": str(args.target), "dpi": args.dpi, "layers": []}
    used_pngs: set[str] = set()
    with collect_inputs(Path(args.target), prefix="gerber-render-") as files:
        for f in files:
            kind, role = identify(f)
            if kind != "gerber":
                continue
            png = _unique_png_path(outdir, f.name, used_pngs)
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
