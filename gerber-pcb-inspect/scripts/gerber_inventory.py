#!/usr/bin/env python3
"""Gerber 层清点：识别每层角色、扫描孔径定义、统计 flash/draw、取外框尺寸。

用法：
    python gerber_inventory.py <gerber 目录或 zip 或单个文件> [--out summary.json]

只读，不改原文件。pygerber 不可用时 bbox 记 null 并继续（其余统计不依赖它）。
标准库 + pygerber(可选)。输出 JSON 到 stdout 或 --out。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

# 扩展名 -> 层角色（大小写不敏感；KiCad/Altium/Eagle 常见命名）
# 键为“规范化后缀”：取文件名去掉数字后的大写后缀，或 KiCad 式 .F_Cu.gtl 这类取最后一段
EXT_ROLE = {
    "GTL": "Top Copper", "GBL": "Bottom Copper",
    "G1": "Inner Copper 1", "G2": "Inner Copper 2", "G3": "Inner Copper 3",
    "G4": "Inner Copper 4", "G5": "Inner Copper 5", "G6": "Inner Copper 6",
    "GTS": "Top Solder Mask", "GBS": "Bottom Solder Mask",
    "GTO": "Top Silkscreen", "GBO": "Bottom Silkscreen",
    "GTP": "Top Paste", "GBP": "Bottom Paste",
    "GM1": "Board Outline", "GML": "Board Outline",
    "GKO": "Keep-Out / Outline", "GM3": "Mechanical",
    "GPT": "Top Padmaster", "GPB": "Bottom Padmaster",
}
# KiCad 命名：.F_Cu.gtl / .B_Cu.gbl / .F_Mask.gts / .F_SilkS.gto / .Edge_Cuts.gm1
KICAD_ROLE = {
    "F_CU": "Top Copper", "B_CU": "Bottom Copper",
    "IN1_CU": "Inner Copper 1", "IN2_CU": "Inner Copper 2",
    "F_MASK": "Top Solder Mask", "B_MASK": "Bottom Solder Mask",
    "F_SILKS": "Top Silkscreen", "B_SILKS": "Bottom Silkscreen",
    "F_PASTE": "Top Paste", "B_PASTE": "Bottom Paste",
    "EDGE_CUTS": "Board Outline",
}
DRILL_EXTS = {"DRL", "TXT", "XNC", "EXC"}
NETLIST_EXTS = {"IPC", "IPCD", "NET"}

ADD_RE = re.compile(r"%ADD(\d+)([CROP]),([^%*]*)\*%")
FS_RE = re.compile(r"%FS([LT])([AI])X(\d)(\d)Y(\d)(\d)\*%")
MO_RE = re.compile(r"%MO(MM|IN)\*%")
TF_RE = re.compile(r"%TF\.FileFunction,([^%*]*)\*%")
D03_RE = re.compile(r"D03\*")
D01_RE = re.compile(r"D01\*")


def identify(path: Path) -> tuple[str, str]:
    """返回 (kind, role)：kind ∈ gerber|drill|netlist|unknown。"""
    stem = path.stem.upper()
    suffix = path.suffix.lstrip(".").upper()
    if suffix in DRILL_EXTS:
        return "drill", "Drill (Excellon)"
    if suffix in NETLIST_EXTS:
        return "netlist", "IPC Netlist"
    if suffix in ("GBR", "GER", "ART", "PHO"):
        return "gerber", "Gerber (generic)"
    # KiCad: 角色藏在倒数第二段，如 .F_Cu.gtl -> F_CU
    parts = path.name.upper().split(".")
    if len(parts) >= 3 and parts[-1] in ("GTL", "GBL", "GTS", "GBS", "GTO", "GBO",
                                         "GTP", "GBP", "GM1", "GML"):
        kicad = parts[-2]
        if kicad in KICAD_ROLE:
            return "gerber", KICAD_ROLE[kicad]
    role = EXT_ROLE.get(suffix)
    if role:
        return "gerber", role
    # 内层 G<n> / 机械层 GM<n>
    if re.fullmatch(r"G\d+", suffix):
        return "gerber", f"Inner Copper {suffix[1:]}"
    if re.fullmatch(r"GM\d+", suffix):
        return "gerber", f"Mechanical {suffix}"
    return "unknown", "Unknown"


def scan_gerber(text: str) -> dict:
    fs = FS_RE.search(text)
    mo = MO_RE.search(text)
    tf = TF_RE.search(text)
    apertures = []
    for m in ADD_RE.finditer(text):
        code, shape, params = m.groups()
        apertures.append({"code": f"D{code}", "shape": shape, "params": params})
    return {
        "format": (f"{fs.group(1)}{fs.group(2)} X{fs.group(3)}.{fs.group(4)} "
                   f"Y{fs.group(5)}.{fs.group(6)}") if fs else None,
        "units": mo.group(1) if mo else None,
        "file_function_x2": tf.group(1) if tf else None,
        "apertures": apertures,
        "aperture_count": len(apertures),
        "flash_count_D03": len(D03_RE.findall(text)),
        "draw_count_D01": len(D01_RE.findall(text)),
    }


def bbox_pygerber(path: Path) -> dict | None:
    """用 pygerber 取外框（mm）。失败返回 None，不中断。"""
    try:
        import logging
        from pygerber.gerberx3.api import (
            ColorScheme, Rasterized2DLayer, Rasterized2DLayerParams,
        )
        # 细线在低 dpi 下会刷屏 "zero surface" 警告，渲染期间只压到 ERROR
        _log = logging.getLogger()
        _old = _log.level
        _log.setLevel(logging.ERROR)
        try:
            layer = Rasterized2DLayer(Rasterized2DLayerParams(
                source_path=str(path), dpi=150, colors=ColorScheme.DEFAULT_GRAYSCALE))
            props = layer.render().get_properties()
        finally:
            _log.setLevel(_old)
        bb = props.gerber_bounding_box
        return {
            "min_x_mm": float(bb.min_x.value), "min_y_mm": float(bb.min_y.value),
            "max_x_mm": float(bb.max_x.value), "max_y_mm": float(bb.max_y.value),
            "width_mm": round(float(bb.max_x.value) - float(bb.min_x.value), 3),
            "height_mm": round(float(bb.max_y.value) - float(bb.min_y.value), 3),
        }
    except Exception as e:  # noqa: BLE001 - 任何解析失败都只记 null
        return {"error": f"{type(e).__name__}: {e}"}


def collect_inputs(target: Path) -> list[Path]:
    if target.is_file() and target.suffix.lower() == ".zip":
        tmp = Path("/tmp/gerber-inventory-unzip")
        with zipfile.ZipFile(target) as z:
            z.extractall(tmp)
        return sorted(p for p in tmp.rglob("*") if p.is_file())
    if target.is_file():
        return [target]
    return sorted(p for p in target.rglob("*") if p.is_file())


def main() -> int:
    ap = argparse.ArgumentParser(description="Gerber 层清点")
    ap.add_argument("target", help="Gerber 目录、zip 或单个文件")
    ap.add_argument("--out", help="写 JSON 到此文件（默认 stdout）")
    args = ap.parse_args()

    files = collect_inputs(Path(args.target))
    layers, drills, netlists, unknown = [], [], [], []
    for f in files:
        kind, role = identify(f)
        entry = {"file": f.name, "role": role, "size_bytes": f.stat().st_size}
        if kind == "gerber":
            text = f.read_text(errors="replace")
            entry.update(scan_gerber(text))
            entry["bbox_mm"] = bbox_pygerber(f)
            entry["lines"] = text.count("\n") + 1
            layers.append(entry)
        elif kind == "drill":
            drills.append(entry)
        elif kind == "netlist":
            netlists.append(entry)
        else:
            unknown.append(entry)
    result = {
        "source": str(args.target),
        "layers": layers, "drill_files": drills,
        "netlists": netlists, "unrecognized": unknown,
        "layer_count": len(layers),
    }
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
