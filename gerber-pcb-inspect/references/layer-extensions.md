# 层与文件扩展名对照

识别逻辑统一在 `scripts/_common.py`（`identify()`）中维护，供 `gerber_inventory.py` 与 `render_layers.py` 共用。扩展名大小写不敏感。

## Altium / 通用 RS-274X

| 扩展名 | 角色 |
|--------|------|
| .GTL | Top Copper（顶层铜） |
| .GBL | Bottom Copper（底层铜） |
| .G1 ~ .G6 | Inner Copper（内层铜，数字为层序） |
| .GTS | Top Solder Mask（顶层阻焊） |
| .GBS | Bottom Solder Mask（底层阻焊） |
| .GTO | Top Silkscreen（顶层丝印） |
| .GBO | Bottom Silkscreen（底层丝印） |
| .GTP | Top Paste（顶层钢网） |
| .GBP | Bottom Paste（底层钢网） |
| .GM1 / .GML | Board Outline（板框；拼版时为整块拼版外框） |
| .GKO | Keep-Out / Outline |
| .GM3 | Mechanical（机械层，常放 V-CUT 线） |

## KiCad 命名

KiCad 导出的文件名是 `<板名>-<层>.g<xx>`，角色藏在倒数第二段：

| 片段 | 角色 |
|------|------|
| F_Cu / B_Cu | Top / Bottom Copper |
| In1_Cu / In2_Cu | Inner Copper |
| F_Mask / B_Mask | Top / Bottom Solder Mask |
| F_SilkS / B_SilkS | Top / Bottom Silkscreen |
| F_Paste / B_Paste | Top / Bottom Paste |
| Edge_Cuts | Board Outline |

## 钻孔与网表

| 扩展名 | 角色 | 备注 |
|--------|------|------|
| .drl / .txt / .xnc | Drill（Excellon） | PTH/NPTH 靠文件名区分，如 `*_PTH.drl` / `*_NPTH.drl`，文件内容本身不区分 |
| .ipc | IPC Netlist | 板厂飞针/电气测试用；本 skill 只清点，不解析网表 |

## 拼版相关文件（不一定在 Gerber zip 里）

- V-CUT：有的厂要求单独给一层 Gerber 或 DXF，有的画在 .GM1/.GM3 里——先看机械层有没有长直线，再问板厂要 V-CUT 图。
- 拼版说明（txt/pdf/邮件正文）：板厚、铜厚、拼板数量、V-CUT 方向、表面处理、工艺边宽度。没有这份说明时，拼版检查只能给“文件层面”的结论。
- ODB++（.tgz）或 IPC-2581 是 Gerber 的替代交付格式，本 skill 不解析；收到这两种格式时先转 Gerber 或改用对应工具。
