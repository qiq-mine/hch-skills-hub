---
name: oh-marketing-growth
description: >
  面向技术产品、AI 应用与开源项目的技术营销与增长工程全流程指南（基于开源 52K stars 项目 marketingskills）。
  打破传统一次性提示词的随意性，将资深 CMO 与增长黑客的方法论沉淀为严谨的工程化流转框架：
  1. 转化率优化 (CRO)：Landing Page 诊断、跳出率归因、转化漏斗修复；
  2. 高转化技术文案 (Copywriting)：清晰优于炫技、核心价值主张 (Value Prop)、PAS/BAB 文案架构；
  3. AI-SEO 与知识引擎优化：Schema 结构化标记、LLM/Perplexity 检索友好度、技术文档 SEO 架构；
  4. 开发者产品发布与冷启动 (Launch Playbook)：GitHub README 爆款工程化排版、Show HN 发布策略；
  5. 增长循环与科学 A/B 测试：指标量化、实验假设设计与最小闭环验证。
  当用户提到 "marketingskills", "oh-marketing-growth", "技术营销", "转化率优化", "CRO", "文案打磨", "AI-SEO", "README排版", "产品发布冷启动" 时触发。
metadata:
  version: 1.0.0
  source: "https://github.com/coreyhaines31/marketingskills"
---

# oh-marketing-growth: 技术产品营销与增长工程流 (Growth Engineering)

很多优秀的工程项目之所以无人问津，并非技术不行，而是缺乏**产品价值主张的清晰传达与系统化的增长飞轮**。
本技能将开源顶流 `marketingskills`（50+ 领域专员 SOP）中对工程师和 AI 团队最具实战价值的方法论提炼为五大工程化模块。

---

## 模块一：转化率优化 (Conversion Rate Optimization - CRO)

### 1. 首屏 5 秒法则 (The 5-Second Test)
访客进入页面 5 秒内，必须无需滚动即能清晰回答三个问题：
* **这是什么？**（清晰的类别定义，绝不用模糊的行话空话）。
* **对我有什么切身好处？**（量化、具象的成果或痛点解除）。
* **下一步我该点哪里？**（单一、突出的主行动点 CTA）。

### 2. CRO 常见反模式排查清单
* ❌ **认知过载**：首屏堆砌 5 个以上的按钮或导航分支。
* ❌ **自嗨型炫技标题**：“赋能全场景智能新范式……”（无具体业务收益）。
* ❌ **弱信任凭据**：缺少真实用户评价、权威 Benchmark 数据或 GitHub Stars 等硬核背据。
* ❌ **过早要求高承诺**：还未展示价值就弹窗要求注册或绑定信用卡。

---

## 二、高转化技术文案框架 (Technical Copywriting)

### 1. 核心价值主张经典公式 (Value Proposition Formula)
> **“我们帮助【明确的目标客群】，在【无需承受典型痛苦/耗时】的前提下，达成【可衡量的具体收益】。”**

* *反面（假大空）*：“新一代革命性多智能体开发利器。”
* *正面（高转化）*：“帮助后端研发团队在无需修改业务代码的前提下，5 分钟内将现有 API 接入支持多智能体协作的沙箱环境。”

### 2. 两大经典文案结构
* **PAS 模型 (Problem - Agitation - Solution)**：
  1. `Problem`：指出当下的真实痛苦（如：你的上下文总是被冗长日志撑爆）。
  2. `Agitation`：揭示该痛苦的严重后果（导致模型幻觉、关键记忆遗忘、成本飙升 40%）。
  3. `Solution`：引出优雅的工程解法（使用沙箱隔离，只返回 3 行结构化摘要）。
* **BAB 模型 (Before - After - Bridge)**：
  * `Before`（改造前的泥潭）→ `After`（改造后的清爽）→ `Bridge`（如何通过你的工具无缝过渡）。

---

## 三、AI-SEO 与新一代搜索引擎优化

在现代互联网中，流量不仅来自 Google/百度，更来自 Perplexity、ChatGPT、Claude 等 AI 问答引擎的直接召回。

### 1. 针对 LLM 检索友好的排版规范 (GEO: Generative Engine Optimization)
* **语义化层级 (H1/H2/H3)**：结构严谨，不要跳级，每个小节首句包含主题关键词。
* **高信息密度对比表**：LLM 极度偏好从 Markdown 表格中抽取对比参数与结论。
* **代码与脚本即插即用**：提供直接可复制运行的命令与最小可复现示例。

### 2. 结构化数据嵌入 (JSON-LD Schema)
在落地页 HTML 或文档中加入标准 Schema 标记：
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "YourToolName",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Linux, macOS, Windows",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "description": "一句话核心价值描述"
}
</script>
```

---

## 四、技术产品发布与冷启动 (Launch Playbook)

### 1. 顶级开源 GitHub README 标准排版
一个能够吸引千星的 README 结构规范：
1. **Header & Badges**：Logo、一句话标题、CI/测试状态徽章、版本徽章、Discord/社区链接。
2. **The Problem**：直观对比图或动图（Before vs After），直戳痛点。
3. **Quickstart**：少于 3 行命令的极速开箱体验（例如 `npm i` → `run`）。
4. **Key Features & Benchmark**：用表格或数字说明为何比同类强（性能对比、资源占用）。
5. **Architecture Diagram**：清晰的架构数据流图（Mermaid 或清晰 SVG）。
6. **Contributing & License**：清晰的协作门槛说明。

### 2. Hacker News / 社区发布法则 (Show HN)
* **拒绝公关营销黑话**：Hacker News 与 Reddit 工程师群体极度反感营销话术。
* **讲事实与技术权衡**：写明“为什么做这个”、“技术架构是怎么选型的”、“牺牲了什么换取了什么”（Trade-offs）。
* **透明发布**：直接开放代码或可体验的无门槛 Demo 链接，严禁必须先填邮箱才能查看内容。

---

## 五、增长循环与实验度量 (Growth Loops)

* **北极星指标定位**：区分虚荣指标（PV、注册量）与北极星指标（如“周活跃创建的自动化流水线数”、“每周通过该工具成功审查的 PR 数量”）。
* **A/B 测试最小闭环**：
  * 一次只变动一个关键变量（主标题、CTA 文案、安装指令）。
  * 制定检验假设：“若将安装指令从多步配置简化为一键脚本，首日运行完成率预期提升 20%”。
  * 持续用真实统计数据验证，而非拍脑袋决策。
