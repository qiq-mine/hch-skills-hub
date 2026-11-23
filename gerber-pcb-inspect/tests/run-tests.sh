#!/usr/bin/env bash
# 回归测试：在 tests/fixtures 上跑三脚本并断言关键值。
# 用法：bash tests/run-tests.sh [python]（默认用当前 venv，没有则用 python3）
set -euo pipefail
PY="${1:-python3}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FX="$ROOT/tests/fixtures"
OUT="$(mktemp -d)"

"$PY" "$ROOT/scripts/gerber_inventory.py" "$FX" --out "$OUT/summary.json"
"$PY" - "$OUT/summary.json" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
by = {l["file"]: l for l in d["layers"]}
assert by["sample.gtl"]["role"] == "Top Copper", by["sample.gtl"]
assert by["sample.gtl"]["aperture_count"] == 3
assert by["sample.gtl"]["flash_count_D03"] == 5
assert by["sample.gtl"]["bbox_mm"]["width_mm"] == 4.0
assert by["sample.gm1"]["role"] == "Board Outline"
assert by["sample.gm1"]["bbox_mm"]["width_mm"] == 40.1
assert by["test-kicad.F_Cu.gtl"]["role"] == "Top Copper"
assert [x["file"] for x in d["drill_files"]] == ["sample.drl"]
print("inventory OK")
EOF

"$PY" "$ROOT/scripts/drill_parse.py" "$FX/sample.drl" --out "$OUT/holes.json"
"$PY" - "$OUT/holes.json" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["total_holes"] == 3, d
assert d["tools"] == {"T1": 0.8, "T2": 1.0}, d
assert d["warnings"] == [], d
print("drill OK")
EOF

"$PY" "$ROOT/scripts/render_layers.py" "$FX" "$OUT/png" --dpi 200 > "$OUT/manifest.json"
"$PY" - "$OUT/png/manifest.json" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
names = sorted(l.get("png", "") for l in d["layers"])
assert names == ["sample.gbs.png", "sample.gm1.png", "sample.gtl.png",
                 "test-kicad.F_Cu.gtl.png"], names
assert all("error" not in l for l in d["layers"]), d
print("render OK")
EOF

echo "ALL TESTS PASSED ($OUT)"
