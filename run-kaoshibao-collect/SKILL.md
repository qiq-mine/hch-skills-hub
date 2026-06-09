---
name: run-kaoshibao-collect
description: Collect exam questions from kaoshibao website via browser automation — handles 5 font obfuscation maps, auto-paginates, exports JSON+Markdown
---

# 考试宝题目采集（浏览器自动化）

Automatically extract exam questions from the 考试宝 (kaoshibao) website
using browser automation. Handles **5 custom font obfuscation maps** that
the site uses to prevent copying — decodes them automatically, paginates
through all questions, and exports structured data.

**Driver:** `kaoshibao_collect.py`

## Prerequisites

```bash
pip install playwright

# Install Playwright system browsers
playwright install chromium
```

## How it works

The driver opens the kaoshibao question page via Playwright, injects the
extraction + font deobfuscation logic, then:

```
Navigate to page → Inject 5 font maps → Extract current question
    → Click "下一题" / press ArrowRight → Extract next question
    → Repeat until no more questions → Save JSON + Markdown
```

The original 5 font obfuscation maps are embedded in the driver so
decoding works entirely offline — no external font API needed.

## Run (agent path)

```bash
cd <project-root>/run-kaoshibao-collect

python kaoshibao_collect.py --url "https://example.kaoshibao.com/exam/xxx" \
  --output ./data \
  --max 200
```

**CLI options:**

| Flag | Default | Description |
|------|---------|-------------|
| `--url` | (required) | Kaoshibao exam/question URL |
| `--output` | `./kaoshibao_output` | Output directory |
| `--max` | `500` | Max number of questions to collect |
| `--delay` | `0.8` | Delay between page turns (seconds) |
| `--headless` | `true` | Run browser in headless mode |
| `--sample` | `0` | Sample limit per type (0=unlimited) |
| `--type-limit` | `0` | Sample per question type (0=unlimited) |

**Output files:**

```
kaoshibao_output/
├── kaoshibao_questions.json        # Structured JSON array
├── kaoshibao_questions.md          # Readable Markdown
├── kaoshibao_screenshot.png        # Screenshot of last page
└── kaoshibao_session.log           # Run log
```

**Example JSON output:**

```json
[
  {
    "type": "单选题",
    "title": "中国的首都是哪里？",
    "options": {"A": "北京", "B": "上海", "C": "广州", "D": "深圳"},
    "answer": "A",
    "analysis": "北京是中国的政治文化中心"
  }
]
```

## Run (human path)

For direct browser Console usage (no automation needed), the original
script at `get-kaoshibao-list/kaoshibao_extractor.js` can be pasted into
the browser's F12 Console on the kaoshibao page.

## Gotchas

- **Font maps must match the site's version** — the 5 embedded maps cover
  the known font hash keys (`k1cc4fe88...`, `k4e047354...`, etc.). If the
  site updates its fonts, the decoded text will be garbled.
- **The site uses `div.qusetion-title`** (note the typo — "qusetion" not
  "question"). The driver checks both spellings.
- **Page turn is done via finding a "下一题" button first**, falling back
  to `ArrowRight` keyboard event if no button is found.
- **Duplicates are tracked by question title hash** — if the same title
  appears twice (e.g. loop back to first question), extraction stops.
- **5 consecutive blank pages** triggers auto-stop to avoid infinite loops.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `playwright: command not found` | Run `pip install playwright && playwright install chromium` |
| All question titles are garbled | The font maps may be outdated — update `FONT_MAPS` in driver |
| "No questions found on page" | URL may not be a question page — verify in browser manually |
| Browser times out | Add `--headless false` to see what's happening; ensure page loads |
| Only 1 question extracted | The "下一题" button selector may have changed — check page HTML |
| Empty options parsed | The `.options-w` / `.option` selectors may differ from expected |

## References

- Original extraction script: `get-kaoshibao-list/kaoshibao_extractor.js`
