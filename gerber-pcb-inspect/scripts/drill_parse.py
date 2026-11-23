#!/usr/bin/env python3
"""Excellon 钻孔文件解析（确定性子集）：工具定义、孔位、孔径统计、外框。

支持：M48 头 / METRIC|INCH / TZ|LZ / 00.000 格式声明 / T<n>C<d> 工具定义 /
绝对坐标 X/Y（带小数点或按格式隐含小数点）/ 单轴重复 / G05 / M30 结束。
不支持：G81/G82/G83 钻孔循环、槽孔（G85）、重复指令 R、增量坐标（G91）。
遇到不支持的指令记入 warnings，不中断。

用法：
    python drill_parse.py <file.drl> [--out holes.json]
输出 JSON 到 stdout 或 --out。纯标准库。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TOOL_RE = re.compile(r"^T(\d+)(?:[FS][\d.]+)*C([\d.]+)")
SELECT_RE = re.compile(r"^T(\d+)\s*$")
COORD_RE = re.compile(r"^X(-?[\d.]+)?Y(-?[\d.]+)?")
HEADER_FMT_RE = re.compile(r"^(METRIC|INCH),?\s*(LZ|TZ)?,?\s*(\d+)\.(\d+)?")


def parse_coord(raw: str, int_digits: int, dec_digits: int, zero_sup: str) -> float:
    """隐含小数点坐标 -> 实际值（mm 或 inch，按文件单位）。带小数点则直接解析。"""
    if "." in raw:
        return float(raw)
    negative = raw.startswith("-")
    digits = raw.lstrip("-")
    if zero_sup == "TZ":  # 尾零省略：右对齐补零到 dec 位
        digits = digits.ljust(int_digits + dec_digits, "0")
    else:  # LZ：首零省略，左对齐补零
        digits = digits.rjust(int_digits + dec_digits, "0")
    value = float(digits[:int_digits] + "." + digits[int_digits:])
    return -value if negative else value


def parse_drill(path: Path) -> dict:
    text = path.read_text(errors="replace")
    units = "INCH"
    zero_sup = "LZ"
    int_digits, dec_digits = 2, 4
    tools: dict[str, float] = {}
    holes: list[dict] = []
    warnings: list[str] = []
    in_body = False
    current_tool: str | None = None
    last_x = last_y = 0.0

    for lineno, raw_line in enumerate(text.splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith(";"):
            continue
        if line == "%":
            in_body = True
            continue
        if line in ("M30", "M02", "M00"):
            break
        if not in_body:
            m = HEADER_FMT_RE.match(line)
            if m:
                units = m.group(1)
                zero_sup = m.group(2) or "LZ"
                int_digits = int(m.group(3))
                dec_digits = int(m.group(4) or "0")
                continue
            m = TOOL_RE.match(line)
            if m:
                tools[m.group(1)] = float(m.group(2))
                continue
            if line == "M48":
                continue
            warnings.append(f"L{lineno}: header 未识别: {line[:60]}")
            continue
        # body
        if line in ("G05", "G90", "G00"):
            continue
        if line.startswith("G") and line not in ("G05", "G90"):
            warnings.append(f"L{lineno}: 不支持的 G 指令（可能为钻孔循环/槽孔）: {line[:60]}")
            continue
        m = SELECT_RE.match(line)
        if m:
            current_tool = m.group(1)
            if current_tool not in tools:
                warnings.append(f"L{lineno}: 选了未定义的工具 T{current_tool}")
            continue
        m = COORD_RE.match(line)
        if m:
            xs, ys = m.groups()
            if xs is not None:
                last_x = parse_coord(xs, int_digits, dec_digits, zero_sup)
            if ys is not None:
                last_y = parse_coord(ys, int_digits, dec_digits, zero_sup)
            holes.append({"tool": current_tool, "x": round(last_x, 4),
                          "y": round(last_y, 4)})
            continue
        if line.startswith("R"):
            warnings.append(f"L{lineno}: 不支持重复指令 R: {line[:60]}")
            continue
        warnings.append(f"L{lineno}: 未识别: {line[:60]}")

    per_tool: dict[str, dict] = {}
    for h in holes:
        t = h["tool"] or "?"
        per_tool.setdefault(t, {"count": 0, "diameter": tools.get(t)})
        per_tool[t]["count"] += 1
    xs = [h["x"] for h in holes]
    ys = [h["y"] for h in holes]
    return {
        "file": path.name, "units": units,
        "zero_suppression": zero_sup, "format": f"{int_digits}.{dec_digits}",
        "tools": {f"T{k}": v for k, v in tools.items()},
        "total_holes": len(holes),
        "per_tool": per_tool,
        "bbox": {"min_x": min(xs), "min_y": min(ys),
                 "max_x": max(xs), "max_y": max(ys)} if holes else None,
        "holes": holes,
        "warnings": warnings,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Excellon 钻孔解析")
    ap.add_argument("drill_file", help="钻孔文件（.drl/.txt/.xnc）")
    ap.add_argument("--out", help="写 JSON 到此文件（默认 stdout）")
    args = ap.parse_args()
    result = parse_drill(Path(args.drill_file))
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
