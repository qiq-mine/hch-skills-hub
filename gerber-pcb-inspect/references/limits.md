# 边界与已知限制

## 格式边界
- **只支持 RS-274X**（内嵌孔径的现代 Gerber）。RS-274D（老格式，孔径在外部 .apr 文件里）不支持，遇到先报不支持。
- Gerber X2 属性（`%TF.FileFunction%` 等）只做记录（summary.json 的 `file_function_x2`），不参与判定。
- 钻孔只支持 Excellon 确定性子集：M48 头、METRIC/INCH、TZ/LZ、绝对坐标。**不支持**：钻孔循环 G81/G82/G83、槽孔 G85、重复指令 R、增量坐标 G91。遇到记入 `warnings`，不中断。
- ODB++（.tgz）、IPC-2581 不解析。

## 解析库边界（2026-11-23 实测）
- `gerber`（gerber-tools）**已不在 PyPI**，不要再用；本 skill 只用 `pygerber==2.4.3`。
- pygerber 2.4.3 没有 Excellon 解析模块，钻孔解析是本 skill 自带的子集解析器（`scripts/drill_parse.py`），不是第三方库。
- pygerber 的 `Offset` 取值用 `.value`（Decimal），不要直接 `float()`。
- 渲染时细线（<0.2mm）在低 dpi 下会刷屏 "zero surface" 警告，脚本已在渲染期间压到 ERROR 级；警告本身无害。
- 外形层细线在 PNG 上可能看不见：以 manifest.json 的 bbox 数字为准，不以图为准；必要时 `--dpi 300` 以上重渲。

## AI 能力边界
- 数字问题只看 JSON，不手算坐标；像素换算成 mm 当测量值是错的。
- 视觉模型看 PNG 只能判断形状与明显异常（缺层、错位、缺口），不能做 DRC 级判定。
- 大文件先抽样：单层 > 50MB 或总行数 > 200 万行时，先清点、只渲染需要的层。

## 交付边界
- 本 skill 的结论不是制板放行依据；间距、线宽、阻焊开窗的精确判定走 EDA/CAM 软件复核。
- 拼版检查里任何一项置信度为“低”时，结论写“需拼版说明或板厂确认”，不猜。
