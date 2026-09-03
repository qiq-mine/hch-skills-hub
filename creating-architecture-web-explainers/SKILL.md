---
name: creating-architecture-web-explainers
description: Use when turning a technical stack, system architecture, lifecycle, call chain, data flow, deployment flow, or technology comparison into an interactive Chinese web explainer, an editable Archscribe diagram, or a hybrid of both.
---

# Creating Architecture Web Explainers

## Core principle

先建立可解释的内容模型，再选择视觉和交互。目标是让读者能回答“系统如何运作、为什么这样设计、边界在哪里”，而不是把架构图换成装饰性网页。

## Frame the brief

先确认受众、要回答的核心问题、部署场景，以及现有品牌或页面约束；已知信息不重复追问。对任何机制或生命周期，按此顺序建模：先写谁或什么启动它、能力如何变得可发现；再写每个阶段进入下一阶段的转换条件、触发事件或判断；最后写由此产生的状态变化。梳理内容时读取 [content model](references/content-model.md)：把原始材料归入概念、关系、流程、权衡、结论五类，并以证据标注不确定处。

以 Skill 为例：host 先向模型提供已安装 Skill 的 `name`、`description`、`path` 轻量列表；用户可用 `@`/`$` 显式点名，或由任务语义与 `description` 匹配而隐式选择，选中后才读取完整 `SKILL.md`。不要表述为 Skill 自己持续扫描，也不要笼统归因于 system prompt。

## Choose the artifact mode

先依据读者要解决的问题选择产物，不要因为工具可用就强行叠加：

| 模式 | 何时选择 | 主要职责 |
| --- | --- | --- |
| Web only | 重点是概念、比较、长文解释或逐步教学 | 页面承担完整叙事与交互 |
| Archscribe only | 重点是全局拓扑、分支、回环、演示动画或可编辑交付 | 图承担结构与路径说明 |
| Hybrid | 同时需要“先看全貌”与“逐步理解”，或既要 HCH.HUB 展示又要可编辑架构图 | Archscribe 提供总览，Web 提供解释与深挖 |

Hybrid 模式必须先建立一份共享内容模型，再派生图和页面；读取 [Archscribe integration](references/archscribe-integration.md)。两边复用稳定阶段 ID、中文术语、顺序和回环含义，禁止各自维护一套流程。

## Choose the narrative and interaction

流程节点必须是读者可独立理解的完整语义阶段，不是视觉分页。一个节点应有输入、状态变化和输出；仅装饰不同的步骤合并。

- 1–3 个完整节点：使用正常纵向滚动。
- 4 个及以上完整节点：使用横向 Slide；一次只呈现一个阶段。
- 其他章节保持纵向滚动，避免将整页强行变成轮播。

横向 Slide 必须提供右下角导航，默认约 60% 不透明度，`hover`/`focus` 为 100%；同时提供当前页/总页码、上一页与下一页按钮、左右方向键和触控滑动。首尾按钮禁用并有明确状态。不要为凑页数机械拆分节点。

## Build

Web 交付为单文件 HTML：语义 HTML、CSS 与 Vanilla JS，零框架、零构建。数据关系足够复杂时才可选用 D3。采用 HCH.HUB 或需要科技感 UI 时读取 [visual system](references/visual-system.md)。起稿时复制 `assets/explainer-starter.html`；不要另造脚手架或假设资产存在。

Hybrid 模式把 Archscribe 放在概念与对比之后、逐步流程之前，作为“完整闭环总览”。正式单文件优先内联生成的 SVG；PoC 阶段可引用 PNG/GIF，但交付前必须说明它尚未满足单文件约束。不要默认使用 `iframe` 嵌入独立页面。

## Verify and hand off

完成后运行 `scripts/validate-explainer.mjs` 的自动校验，并在桌面与移动端做视觉验收：内容可读、焦点可见、触控可用，且尊重 `prefers-reduced-motion`。Archscribe 产物还要执行 spec 校验、渲染验证和边界检查。Hybrid 模式逐项核对：每个图节点至少映射到一个页面章节或 Slide，术语和先后顺序一致，所有失败回环在两边都能解释。交付时说明核心问题、内容模型、产物模式、交互模式，以及尚未证实的假设。

## Quick reference

| 需要回答的问题 | 页面角色 | 适用表现 |
| --- | --- | --- |
| 这是什么 | 概念 | Hero、术语卡 |
| 谁与谁相连 | 关系 | 分层图、连接图 |
| 如何发生 | 流程 | Stage 或 Slide |
| 全局如何连接与回环 | 拓扑总览 | Archscribe 图 |
| 为什么取舍 | 权衡 | 对比卡 |
| 读者应记住什么 | 结论 | 总结区 |

## Common mistakes

- 按组件数量而非完整语义选择滚动或 Slide：先合并、定义节点输入与输出，再计数。
- Slide 只有按钮或页码：补齐键盘、触控、首尾禁用与状态反馈。
- Web 与 Archscribe 分别写内容：改为共享稳定 ID 的单一内容模型，并建立节点到章节或 Slide 的映射。
- 用 `iframe` 直接拼接两个独立页面：优先内联 SVG，统一主题、响应式和可访问性。
- 只覆盖内容模型、跨主题视觉层或自动校验之一：交付前逐项核对三者，并进行双端视觉验收。

## 待补充内容与规划 (TODO / Backlog)

> [!NOTE]
> 核心规范与校验脚本完备，后续建议补充：

- [ ] **D3 复杂网络图模版**：对于超大规模拓扑，补充 D3.js 物理力导向图/层次图单文件示例。
- [ ] **Archscribe 导出自动化**：补充通过 CLI/Puppeteer 自动将 Archscribe 项目导出为标准内联 SVG 的脚本工具。
