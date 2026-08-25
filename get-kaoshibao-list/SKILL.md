---
name: get-kaoshibao-list
description: Extract exam questions from Kaoshibao (考试宝) web pages via browser console script — handles 5 obfuscated font mappings, auto-paginates, deduplicates, and downloads JSON and Markdown
---

# 考试宝题目提取（浏览器控制台脚本）

通过在浏览器开发者工具（F12）Console 控制台中运行 JavaScript 脚本，自动逐题提取考试宝页面的题目、选项、正确答案和解析。

内置 **5 套混淆字体映射表**，能够在前端自动解码混淆字符，支持翻页、去重并导出 JSON 和 Markdown 文件。

**脚本文件:** [`kaoshibao_extractor.js`](./kaoshibao_extractor.js)

## 适用场景

- 需要在已登录的浏览器中快速抓取考试宝题库
- 无需安装 Python/Playwright 环境，直接在浏览器端运行
- 题目包含混淆字体（如 `k1cc4fe8...`, `k4e04735...` 等），需要离线解混淆
- 支持单选题、多选题、判断题、填空题、简答题

> **提示：** 如需无人工干预的自动化无头浏览器批量采集，推荐使用 [`run-kaoshibao-collect`](../run-kaoshibao-collect/SKILL.md) 技能。

## 使用步骤

1. 打开 Chrome / Edge 等现代浏览器，访问目标考试宝练习/考试页面。
2. 按 `F12` 或 `Ctrl+Shift+I`（Mac: `Cmd+Option+I`）打开开发者工具。
3. 切换到 **Console（控制台）** 标签页。
4. 复制 [`kaoshibao_extractor.js`](./kaoshibao_extractor.js) 的完整代码，粘贴到控制台中并回车运行。
5. 脚本将自动：
   - 检测当前题目字体并解码文本
   - 提取题目类型、题干、选项、正确答案及解析
   - 自动点击“下一题”或模拟右方向键翻页
   - 提取完成后自动下载 `kaoshibao_<timestamp>.json` 和 `kaoshibao_<timestamp>.md` 文件
   - 将提取数据暂存到全局变量 `window.__ksb_data`

## 配置参数

在脚本顶部可按需调整运行参数：

```javascript
// 抽样限制：0 表示不限制（全量提取），正整数表示该题型提取指定数量
var SAMPLE_LIMIT = { '单选题': 0, '多选题': 0, '判断题': 0 };

var DELAY_MS = 600;       // 翻页延迟（毫秒），避免请求过快
var MAX_QUESTIONS = 500;   // 单次最大提取题数
```

## 输出示例

### JSON 输出 (`kaoshibao_*.json`)

```json
[
  {
    "type": "单选题",
    "title": "下列关于云计算特性的描述中，错误的是？",
    "options": {
      "A": "按需自助服务",
      "B": "广泛的网络访问",
      "C": "资源池化",
      "D": "独占物理资源不可共享"
    },
    "answer": "D",
    "analysis": "云计算具有资源池化与多租户共享特性。"
  }
]
```

### Markdown 输出 (`kaoshibao_*.md`)

```markdown
# 考试宝题目提取结果

提取时间：2026/8/25 14:00:00
来源：https://www.kaoshibao.com/exam/...
共 1 道题

---

## 1. （单选题）下列关于云计算特性的描述中，错误的是？

- A. 按需自助服务
- B. 广泛的网络访问
- C. 资源池化
- D. 独占物理资源不可共享

**答案：D**

**解析：**云计算具有资源池化与多租户共享特性。

---
```

## 常见问题与排查

| 现象 | 原因 | 解决方法 |
|------|------|----------|
| 解码后的文本出现乱码 | 网站更新了混淆字体哈希 | 在页面中检查 `@font-face` 的字体名称，更新 `FONT_MAPS` 映射表 |
| 无法自动翻页 | 页面改版导致下一题按钮选择器变更 | 脚本会自动尝试 `ArrowRight` 键；也可手动微调 `findNextButton` 选择器 |
| 提前停止（连续 5 次无新题） | 已到达最后一题或遇到弹窗拦截 | 检查浏览器页面是否出现会员弹窗或结束提示 |

## 相关技能

- [`run-kaoshibao-collect`](../run-kaoshibao-collect/SKILL.md) — 考试宝题目 Playwright 自动化采集技能
