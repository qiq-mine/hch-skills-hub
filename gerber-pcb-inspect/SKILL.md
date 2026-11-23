---
name: gerber-pcb-inspect
description: "Parse RS-274X Gerber + Excellon drill files into structured data and per-layer renders so an agent can answer questions about a PCB panel: layer inventory, pad/hole counts, outline size, V-CUT, stamp holes and fiducials. Text first, image second, never guess numbers from raw coordinates."
---

# Gerber PCB Inspect

## Purpose
把一版 Gerber（单板或拼版）变成 Agent 能可靠回答的事实：每层是什么、有多少焊盘和孔、外框多大、拼版工艺内容齐不齐。原则：**数字只认脚本输出的 JSON，图只用来看形状；原文坐标不直接喂模型**。

## Workflow

### 1. 收料
输入是 Gerber zip、目录或单个文件。先确认输入完整：缺外形层（.GM1/.GKO）或缺钻孔文件时先说缺了什么，再继续。原文件只读，输出一律写到独立目录。

### 2. 清点各层
```bash
python scripts/gerber_inventory.py <zip|目录|文件> --out summary.json [--no-bbox]
```
输出每层的角色（按扩展名识别，见 `references/layer-extensions.md`）、格式（FS/MO）、X2 FileFunction、孔径定义（D-code、形状、尺寸）、flash（D03）与 draw（D01）计数、外框尺寸（mm）。单层解析失败只记 `bbox_mm.error`，单层 > 50MB 默认跳过外框计算。

### 3. 解析钻孔
```bash
python scripts/drill_parse.py <file.drl> --out holes.json [--summary-only]
```
输出单位、零省略方式、工具表（孔径）、每工具孔数、全部孔位（可用 `--summary-only` 省略明细）、外框（含 `bbox_mm`）。PTH/NPTH 文件本身不区分，靠文件名区分（见 `references/layer-extensions.md`）。钻孔循环（G81/G82/G83）、槽孔（G85）、重复指令（R）不在脚本范围内，遇到记 `warnings` 并明说。

### 4. 渲染各层
```bash
python scripts/render_layers.py <zip|目录> <输出目录> [--dpi 200] [--layers 关键词]
```
每层一张 PNG + `manifest.json`（角色、外框、像素）。配色按层角色选。线宽 < 0.2mm 的层（常见于外形层）用 `--dpi 300` 以上，否则细线在图上可能看不见——此时以 manifest 里的外框数字为准，不以图为准。

### 5. 拼版检查
按 `references/panel-checks.md` 逐项过：外框是否为拼版外框、V-CUT、邮票孔、定位孔/工艺边、Mark 点。每一项都是启发式，给结论时带置信度（高/中/低）并写出依据来自哪个文件或哪张 PNG。

### 6. 回答问题
结论分三档，写清楚是哪一档：
- **确定**：来自 summary.json / holes.json 的数字（层数、孔径、孔数、外框尺寸）。
- **图上所见**：来自 PNG 的形状判断，注明 PNG 文件名；尺寸只能说“图上看约”，不报精确数。
- **无法确定**：缺文件、格式不支持、图上看不清——明说缺什么，不编。

## Output Contract
- 每次运行交付：`summary.json`（层清点）+ `holes.json`（钻孔，如有）+ 各层 PNG + `manifest.json` + 一份 findings 清单（结论、档位、依据）。
- 不改原文件；不报没有依据的尺寸；不把“图上看着对”说成通过检查。

## Operating Rules
1. 数字只认脚本输出的 JSON，不手算坐标、不目测报尺寸、不把渲染像素换算成 mm 当测量值。
2. 视觉结论只说图里看到的，标出 PNG 文件名；看不清就说看不清。
3. RS-274D（老格式、无内嵌孔径，需 .apr 文件）不在本 skill 范围内，遇到先报不支持，不硬解。
4. 不做 DRC 保证：间距、线宽、阻焊开窗的精确判定必须走 EDA/CAM 软件复核；本 skill 只做清点与形状核查。
5. 大文件先抽样：单层 > 50MB 或总行数 > 200 万行时，先清点、只渲染需要的层，不整文件喂模型。
6. 环境：Python 3.10+，`pip install -r scripts/requirements.txt`（pygerber==2.4.3）。注意：`gerber`（gerber-tools）已不在 PyPI，不要再用它。
7. 维护：改动走分支 + PR，Robin 合并（与 ai-native-repo 的直推 master 例外不同）。
