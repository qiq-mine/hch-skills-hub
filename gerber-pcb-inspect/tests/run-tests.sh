#!/usr/bin/env bash
# 回归测试：在 tests/fixtures 上跑三脚本并断言关键值。
# 用法：bash tests/run-tests.sh [python]（默认用 python3）
set -euo pipefail
PY="${1:-python3}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FX="$ROOT/tests/fixtures"
OUT="$(mktemp -d)"
trap 'rm -rf "$OUT"' EXIT

HAS_PYGERBER=0
if "$PY" -c "import pygerber" >/dev/null 2>&1; then
  HAS_PYGERBER=1
fi

"$PY" "$ROOT/scripts/gerber_inventory.py" "$FX" --out "$OUT/summary.json"
"$PY" - "$OUT/summary.json" "$HAS_PYGERBER" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
has_pygerber = sys.argv[2] == "1"
by = {l["file"]: l for l in d["layers"]}
assert by["sample.gtl"]["role"] == "Top Copper", by["sample.gtl"]
assert by["sample.gtl"]["aperture_count"] == 3
assert by["sample.gtl"]["flash_count_D03"] == 5
assert by["sample.gm1"]["role"] == "Board Outline"
assert by["test-kicad.F_Cu.gtl"]["role"] == "Top Copper"
assert by["kicad-board-F_Cu.gbr"]["role"] == "Top Copper", by["kicad-board-F_Cu.gbr"]
assert sorted(x["file"] for x in d["drill_files"]) == ["sample-inch-lz.drl", "sample.drl"]
if has_pygerber:
    assert by["sample.gtl"]["bbox_mm"]["width_mm"] == 4.0, by["sample.gtl"]
    assert by["sample.gm1"]["bbox_mm"]["width_mm"] == 40.1, by["sample.gm1"]
print("inventory OK")
EOF

# 验证 --no-bbox 与 zip 隔离（含 __MACOSX 过滤）
"$PY" - "$FX" "$OUT/a.zip" "$OUT/b.zip" <<'EOF'
import sys, zipfile
from pathlib import Path
fx = Path(sys.argv[1])
with zipfile.ZipFile(sys.argv[2], "w") as z:
    z.write(fx / "sample.gtl", "sample.gtl")
    z.writestr("__MACOSX/._sample.gtl", b"junk")
with zipfile.ZipFile(sys.argv[3], "w") as z:
    z.write(fx / "sample.gm1", "sample.gm1")
EOF
"$PY" "$ROOT/scripts/gerber_inventory.py" "$OUT/a.zip" --no-bbox --out "$OUT/zip_a.json"
"$PY" "$ROOT/scripts/gerber_inventory.py" "$OUT/b.zip" --no-bbox --out "$OUT/zip_b.json"
"$PY" - "$OUT/zip_a.json" "$OUT/zip_b.json" <<'EOF'
import json, sys
a = json.load(open(sys.argv[1]))
b = json.load(open(sys.argv[2]))
assert [l["file"] for l in a["layers"]] == ["sample.gtl"], a
assert [l["file"] for l in b["layers"]] == ["sample.gm1"], b
assert a["layers"][0]["bbox_mm"] is None
print("zip & --no-bbox OK")
EOF

"$PY" "$ROOT/scripts/drill_parse.py" "$FX/sample.drl" --out "$OUT/holes.json"
"$PY" "$ROOT/scripts/drill_parse.py" "$FX/sample-inch-lz.drl" --summary-only --out "$OUT/holes_inch.json"
"$PY" - "$OUT/holes.json" "$OUT/holes_inch.json" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["total_holes"] == 3, d
assert d["tools"] == {"T1": 0.8, "T2": 1.0}, d
assert d["bbox_mm"]["width_mm"] == 10.0, d
assert d["warnings"] == [], d

di = json.load(open(sys.argv[2]))
assert di["units"] == "INCH", di
assert di["total_holes"] == 2, di
assert di["per_tool"] == {"1": {"count": 2, "diameter": 0.0394}}, di
assert di["bbox_mm"]["width_mm"] == 25.4, di
assert di["warnings"] == [], di
assert di.get("holes_omitted") is True and "holes" not in di, di
print("drill OK")
EOF

if [ "$HAS_PYGERBER" -eq 1 ]; then
  "$PY" "$ROOT/scripts/render_layers.py" "$FX" "$OUT/png" --dpi 200 > /dev/null
  "$PY" - "$OUT/png/manifest.json" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
names = sorted(l.get("png", "") for l in d["layers"])
assert names == [
    "kicad-board-F_Cu.gbr.png",
    "sample.gbs.png",
    "sample.gm1.png",
    "sample.gtl.png",
    "test-kicad.F_Cu.gtl.png",
], names
assert all("error" not in l for l in d["layers"]), d
print("render OK")
EOF
else
  echo "[SKIP] pygerber not installed; skipped bbox_mm and render_layers checks"
fi

echo "ALL TESTS PASSED"
