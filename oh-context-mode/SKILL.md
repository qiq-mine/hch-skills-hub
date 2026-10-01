---
name: oh-context-mode
description: >
  智能体上下文窗口防爆与降本优化技能（节省高达 98% Context）。
  核心遵循“Think in Code”范式：智能体不是数据处理器，而是代码生成器。
  在面对大规模输出、海量日志、大型 JSON、大量文件扫描、测试日志、Playwright 浏览器快照或 API 调试时，
  严禁直接把原始数据 dump 到上下文；强制通过本地脚本沙箱执行、文件暂存与 SQLite FTS5/BM25 检索，仅向上下文返回提炼后的摘要。
  当用户提到 "context-mode", "oh-context-mode", "优化上下文", "节省token", "上下文超限", "大文件分析", "分析大量日志", "浏览器快照优化" 时触发。
metadata:
  version: 1.0.0
  source: "https://github.com/mksglu/context-mode"
---

# oh-context-mode: 上下文防爆与代码计算范式 (Think in Code)

每当智能体调用工具把数百 KB 的原始日志、DOM 树或 JSON 灌入上下文窗口时，不仅会消耗大量 Token，更会导致模型发生**上下文漂移、注意力稀释与关键历史遗忘**。

> **核心信条**：Stop treating the LLM as a data processor, treat it as a code generator.（不要把大模型当数据处理器，把它当代码生成器）。

---

## 一、核心原则：Think in Code

当需要对海量数据进行统计、过滤或分析时：
* ❌ **错误做法**：连续读取 50 个文件或 `cat large.log`，将 700 KB 原始文本塞满上下文。
* ✅ **正确做法**：编写一段轻量 Python 或 Node.js 脚本在本地运行，由脚本完成遍历、计算与筛选，仅向上下文输出 3 行总结性结论（消耗 < 1 KB）。

### 对比示例：统计代码库行数与异常
```bash
# ❌ 错误（消耗 300K+ Tokens）：直接遍历并读取所有 .ts 源码到上下文
# ✅ 正确（消耗 50 Tokens）：写脚本在本地执行并仅输出最终聚合结果
python3 -c "
import os, glob
ts_files = glob.glob('src/**/*.ts', recursive=True)
total_lines = sum(len(open(f, errors='ignore').readlines()) for f in ts_files)
print(f'Total TS files: {len(ts_files)}, Total lines: {total_lines}')
"
```

---

## 二、命令白名单与沙箱路由纪律

### 1. 允许直接执行的终端白名单 (仅限产出极小确定性输出的命令)
* **文件操作**：`mkdir`, `mv`, `cp`, `rm`, `touch`, `chmod`
* **Git 写入**：`git add`, `git commit`, `git checkout`, `git branch` (注: `git diff` / `git log` 如过长需分页限制)
* **路径与基础**：`pwd`, `which`, `echo`
* **依赖安装**：`npm install`, `pip install`

### 2. 严禁直接输出至上下文的高危操作
* ❌ `cat large_file.json` 或读取超过 100 行的文件。
* ❌ `curl -s https://api.endpoint` 返回未过滤的大型 JSON。
* ❌ `npm test` 或全量 CI 日志全量打印。
* ❌ `kubectl get pods -A -o yaml` 或 `docker logs` 打印全部日志。
* ❌ Playwright / Puppeteer 截取完整 DOM 树或未指定文件输出的 Snapshot。

**应对法则**：任何产生不可控或超过 20 行输出的操作，必须重定向至临时文件，或使用 `jq` / Python 脚本过滤后再呈现！

---

## 三、浏览器快照 (Playwright/Browser) 优化流水线

浏览器 Accessibility Tree 快照单次高达 10K ~ 135K tokens。连续两次操作就会打爆窗口。

### 黄金流水线：快照存盘 → 本地检索/脚本提取 → 精简呈现

| 路径 | 上下文消耗 | 是否合格 |
| :--- | :---: | :---: |
| 直接在上下文中展开 `browser_snapshot()` | **135,000 tokens** | ❌ 严禁 |
| `browser_snapshot(filename="/tmp/snap.md")` → 上下文直接读盘 | **135,000 tokens** | ❌ 严禁 |
| `browser_snapshot(filename)` → 脚本提取目标元素 → 仅输出目标选择器 | **~250 bytes** | ✅ **推荐 (省 99%)** |

#### 快速提取脚本模板
```javascript
// /tmp/extract_buttons.js
const fs = require('fs');
const content = fs.readFileSync('/tmp/snap.md', 'utf8');
const buttons = [...content.matchAll(/- button "([^"]+)"/g)].map(m => m[1]);
const inputs = [...content.matchAll(/- (textbox|searchbox) "([^"]+)"/g)].map(m => m[2]);
console.log(`Found ${buttons.length} buttons, ${inputs.length} inputs`);
console.log('Actionable elements:', { buttons: buttons.slice(0, 10), inputs });
```

---

## 四、本地 SQLite FTS5 / BM25 知识检索范式

面对多文档或历史日志检索时，智能体应利用本地 SQLite 全文检索数据库（FTS5），而非把文档粘在 Prompt 中反复重传：

```python
# 初始化并构建局部高密度全文索引
import sqlite3

conn = sqlite3.connect('/tmp/ctx_index.db')
conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS docs USING fts5(filepath, content);")
# 仅插入路径与文本，后续通过 BM25 相关性搜索
# SELECT snippet(docs, 1, '<b>', '</b>', '...', 10) FROM docs WHERE docs MATCH 'error connection timeout' ORDER BY rank LIMIT 5;
```

---

## 五、常用数据处理脚本模板

### 1. 快速提取长日志中的 Error 堆栈
```bash
python3 -c "
import sys, re
errors = []
with open('debug.log') as f:
    for line in f:
        if any(k in line.lower() for k in ['error', 'exception', 'fatal', 'panic']):
            errors.append(line.strip())
print(f'Total errors: {len(errors)}')
for e in errors[-5:]:
    print('  >', e)
"
```

### 2. 精简过滤 GitHub PR / Issue API 响应
```bash
gh pr list --json number,title,author,state --jq '.[] | "#\(.number) [\(.state)] \(.title) (@\(.author.login))"'
```

### 3. 测试输出错误提炼
```bash
npm test 2>&1 | tee /tmp/test_output.log | grep -E "(FAIL|●|Error:)" -A 2
echo "Test Exit Code: $?"
```

---

## 六、反模式自查清单 (Anti-Patterns)

1. **绝对禁止**：在主对话中用 `cat` 或直接返回未分片的 50KB+ 文件。
2. **绝对禁止**：对未知大小的 API 响应直接发起 `curl` 并不加 `head/grep/jq` 过滤。
3. **避免过度截断**：`head -n 20` 常常丢失关键错误信息，推荐使用脚本**先统计全貌、再提取前后关键切片**。
4. **会话减负**：一旦完成了某项大任务排查，及时清理或归档临时生成的大型 scratch 文件，避免磁盘与索引污染。
