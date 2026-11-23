# Changelog

## v0.1.0 — 2026-11-23
- 初始版：Gerber 层清点（`scripts/gerber_inventory.py`）、Excellon 钻孔子集解析（`scripts/drill_parse.py`）、各层批量渲染（`scripts/render_layers.py`）。
- 参考文档：层扩展名对照（Altium/KiCad）、拼版检查启发式、边界与限制。
- 测试夹具：`tests/fixtures/`（顶层铜/底层阻焊/板框/钻孔各一），三脚本在夹具上实测通过。
- 工具链结论（2026-11-23 实测）：`gerber`（gerber-tools）已不在 PyPI，改用 `pygerber==2.4.3`；pygerber 无 Excellon 模块，钻孔解析自写子集解析器。
