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
from pathlib import Path

from _common import collect_inputs, identify, suppress_pygerber_warnings

ADD_RE = re.compile(r"%ADD(\d+)([CROP]),([^%*]*)\*%")
FS_RE = re.compile(r"%FS([LT])([AI])X(\d)(\d)Y(\d)(\d)\*%")
MO_RE = re.compile(r"%MO(MM|IN)\*%")
TF_RE = re.compile(r"%TF\.FileFunction,([^%*]*)\*%")
D03_RE = re.compile(r"D03\*")
D01_RE = re.compile(r"D01\*")


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
    """用 pygerber 取外框（mm）。失败返回 {"error": ...}，不中断。"""
    try:
        from pygerber.gerberx3.api import (
            ColorScheme, Rasterized2DLayer, Rasterized2DLayerParams,
        )
        with suppress_pygerber_warnings():
            layer = Rasterized2DLayer(Rasterized2DLayerParams(
                source_path=str(path), dpi=150, colors=ColorScheme.DEFAULT_GRAYSCALE))
            props = layer.render().get_properties()
        bb = props.gerber_bounding_box
        return {
            "min_x_mm": float(bb.min_x.value), "min_y_mm": float(bb.min_y.value),
            "max_x_mm": float(bb.max_x.value), "max_y_mm": float(bb.max_y.value),
            "width_mm": round(float(bb.max_x.value) - float(bb.min_x.value), 3),
            "height_mm": round(float(bb.max_y.value) - float(bb.min_y.value), 3),
        }
    except Exception as e:  # noqa: BLE001 - 任何解析失败都只记 error
        return {"error": f"{type(e).__name__}: {e}"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Gerber 层清点")
    ap.add_argument("target", help="Gerber 目录、zip 或单个文件")
    ap.add_argument("--out", help="写 JSON 到此文件（默认 stdout）")
    ap.add_argument("--no-bbox", action="store_true", help="跳过 pygerber 外框计算")
    ap.add_argument("--max-bbox-mb", type=float, default=50.0,
                    help="超过此大小（MB）的单层跳过外框计算（默认 50）")
    args = ap.parse_args()

    max_bytes = int(args.max_bbox_mb * 1024 * 1024)
    layers, drills, netlists, unknown = [], [], [], []
    with collect_inputs(Path(args.target), prefix="gerber-inventory-") as files:
        for f in files:
            kind, role = identify(f)
            size_bytes = f.stat().st_size
            entry = {"file": f.name, "role": role, "size_bytes": size_bytes}
            if kind == "gerber":
                text = f.read_text(errors="replace")
                entry.update(scan_gerber(text))
                if args.no_bbox:
                    entry["bbox_mm"] = None
                elif size_bytes > max_bytes:
                    entry["bbox_mm"] = {"skipped": f"size > {args.max_bbox_mb}MB"}
                else:
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
