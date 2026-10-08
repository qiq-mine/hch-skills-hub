---
name: exam4ksb-extract
description: "Extract exam questions from Examener (考试宝) — browser-console script (lightweight, no install) or Playwright automation (headless batch). 5 obfuscated font maps decoded offline, auto-pagination, dedup by title hash, JSON+Markdown export"
---

# 考试宝题目提取（exam4ksb-extract）

> **合规声明**：本技能仅限用于你**自有或已获明确授权**的题库场景。使用前请确认已阅读并遵守目标站点的服务条款（ToS）与版权要求；不得用于抓取他人享有版权的商业题库内容。由此产生的法律风险由使用者自行承担。
>
> **Compliance notice**: This skill may only be used with question banks you **own or are explicitly authorized** to collect. Please review and comply with the target site's Terms of Service and copyright requirements before use.

两种执行模式，共用同一套抽取逻辑：**5 套混淆字体映射离线解码**、自动翻页（"下一题"按钮 → 回退 `ArrowRight`）、按题目标题哈希去重、导出 JSON + Markdown。支持单选/多选/判断/填空/简答。

| | 模式 A：控制台脚本 | 模式 B：Playwright 自动化 |
|---|---|---|
| 适用 | 已登录浏览器快速抓取 | 无人值守批量采集 |
| 环境 | 零安装，F12 粘贴即跑 | `pip install playwright && playwright install chromium` |
| 入口 | `examener_extractor.js` | `examener_collect.py` |
| 截图/日志 | — | 末页截图 `examener_screenshot.png` + `examener_session.log` |

## 模式 A：浏览器控制台脚本

1. 打开 Chrome / Edge，访问目标考试宝练习/考试页面。
2. `F12` 打开开发者工具 → Console 标签页。
3. 复制 [`examener_extractor.js`](./examener_extractor.js) 完整代码，粘贴回车运行。
4. 脚本自动：检测题目字体并解码 → 提取题型/题干/选项/答案/解析 → 自动翻页 → 完成后下载 `examener_<timestamp>.json` 和 `.md`，数据暂存 `window.__ksb_data`。

脚本顶部可调参数：`SAMPLE_LIMIT`（按题型抽样，0=全量）、`DELAY_MS`（翻页延迟，默认 600）、`MAX_QUESTIONS`（默认 500）。

## 模式 B：Playwright 自动化采集

```bash
cd exam4ksb-extract

python examener_collect.py --url "https://example.examener.com/exam/xxx" \
  --output ./data \
  --max 200
```

| Flag | Default | 说明 |
|------|---------|------|
| `--url` | (required) | 考试宝题目页 URL |
| `--output` | `./examener_output` | 输出目录 |
| `--max` | `500` | 最大采集题数 |
| `--delay` | `0.8` | 翻页间隔（秒） |
| `--headless` | `true` | 无头模式 |
| `--sample` / `--type-limit` | `0` | 按题型抽样（0=不限） |

输出：`examener_questions.json`（结构化数组）、`examener_questions.md`（可读版）、末页截图、session 日志。

## 字体映射表（两处内嵌，更新时同步）

- `examener_extractor.js`：JS 版 5 套 `FONT_MAPS`（key 如 `k1cc4fe8…`），Console 粘贴场景必须自包含。
- `examener_collect.py`：Python 版 `FONT_MAPS`（同 5 个 key，文件顶部）。
- 网站更新字体导致乱码时，两处同步更新（后续可抽成单一数据源）。

## 输出示例

JSON（`examener_*.json`）：
```json
[
  {
    "type": "单选题",
    "title": "下列关于云计算特性的描述中，错误的是？",
    "options": {"A": "按需自助服务", "B": "广泛的网络访问", "C": "资源池化", "D": "独占物理资源不可共享"},
    "answer": "D",
    "analysis": "云计算具有资源池化与多租户共享特性。"
  }
]
```

Markdown（`examener_*.md`）：`# 考试宝题目提取结果` + 提取时间/来源/题数，每题含题干、选项、答案、解析。

## 排查

| 现象 | 原因 | 解决 |
|------|------|------|
| 解码乱码 | 网站更新了混淆字体哈希 | 检查 `@font-face` 字体名，同步更新两处 `FONT_MAPS` |
| 无法自动翻页 | 下一题按钮选择器变更 | 脚本会回退 `ArrowRight` 键；或微调 `findNextButton` 选择器 |
| 提前停止 | 到末题 / 弹窗拦截 | 检查会员弹窗或结束提示 |
| `playwright: command not found` | 未安装 | `pip install playwright && playwright install chromium` |
| 题目选择器失效 | 页面改版（注意 `div.qusetion-title` 的拼写） | 检查页面 HTML，两种拼写都兼容 |

## 待补充（Backlog）

- [ ] 动态字体探测：站点更新字体哈希时，一键提取新 `@font-face` 并生成字形映射表。
- [ ] 多平台适配：目前针对 Examener 结构，后续补充其他刷题平台解析器。
- [ ] 登录态持久化：支持 Cookie / `storage_state.json`，免密采需要登录的题库。

---
*2026-10-08：由 `get-exam4ksb-list` 与 `run-exam4ksb-collect` 合并为 `exam4ksb-extract`（同一 job 的两种执行模式；`tff/` 字体文件未被任何代码引用，未迁移，可从 git 历史找回）。*
