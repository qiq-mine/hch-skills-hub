---
name: frontend-code-review
description: "Dify 前端代码审查技能。面向 React/Next.js/TypeScript 与 Dify UI/Tailwind CSS 体系，审查可访问性 (a11y)、UI 契约、组件架构、状态管理、TanStack Query 数据请求、运行时不变量与性能开销。支持 Git diff、特定文件或提交审查。分级输出 P0-P3 缺陷。Triggers: frontend-code-review, /frontend-code-review, 前端审查, 前端代码审查, React代码审查, 组件审查."
---

# Frontend Code Review (Dify 前端工程审查)

面向现代 React / Next.js / TypeScript 前端体系的高质量代码审查技能。基于 Dify 前端架构标准，针对 Web 界面、设计系统基元组件（Dify UI / Base UI）及数据交互层进行深度质量检查。

## 审查原则：Evidence First (证据优先)

1. **确立审查边界**：从用户请求的目标文件、Git 变更 diff 或分支比对提取受审代码。
2. **理解所有权契约**：查阅改动行所在模块的行为归属与最近的架构约定。
3. **追踪状态与边界**：在影响正确性时追踪公共组件消费者、数据请求契约、全局状态流转或 SSR 渲染环境。
4. **证据闭环**：仅上报能证明的实际缺陷、违反明确约定、无障碍阻断或显著性能隐患。团队既定规范即契约，应明确其范围与例外，严禁编造虚假的用户影响。

## 规则路由 (Rule Routing)

根据改动内容自动匹配专属审查规则包：

| 关注领域 | 规则包路径 | 核心审查要点 |
|---------|-----------|-------------|
| DOM 语义、焦点、键盘导航与 A11y | [`references/accessibility-ui.md`](references/accessibility-ui.md) | 可访问名称计算、按钮/链接语义、Focus Trap、ARIA 属性、键盘交互 ([参考指南](../../docs/accessible-names-and-descriptions.md)) |
| 设计系统基元与 UI 契约 | [`references/dify-ui.md`](references/dify-ui.md) | `@langgenius/dify-ui` 基元规范、Tokens 遵循、Overlays 浮层契约 ([规范文档](../../docs/overlays.md))、表单语义 ([表单规范](../../docs/forms.md)) |
| 组件架构、状态生命周期与边界 | [`references/component-architecture.md`](references/component-architecture.md) | 容器与展示解耦、Props 契约最小化、状态下沉、Effect 避免过度使用、模块循环依赖 |
| 数据获取、TanStack Query 与缓存 | [`references/data-query-contracts.md`](references/data-query-contracts.md) | Query Key 结构化、Mutations 乐观更新与精确失效、SSR/水合隔离、跨租户数据隔离 |
| 运行时稳定不变量 | [`references/dify-invariants.md`](references/dify-invariants.md) | Workflow 节点与 RAG Pipe 渲染上下文隔离、Provider 上下文挂载安全 |
| 性能、渲染开销与包体积 | [`references/performance.md`](references/performance.md) | 避免大树无效重渲染、昂贵计算 memo 化、组件按需动态导入、瀑布式请求消除 |
| 测试覆盖与回归验证 | [`references/testing.md`](references/testing.md) | 关键用户行为覆盖、禁止 mock 内部实现、测试选择器稳定性 ([测试策略](../../docs/test.md)) |
| TypeScript 与样式编码质量 | [`references/code-quality.md`](references/code-quality.md) | 杜绝 `any` / 盲目断言、Tailwind v4 标准类名 ([样式指南](../../docs/styling.md))、命名与导出一致性 |

## 严重级别与输出规范 (Severity & Output)

- **P0 (阻断级)**：安全/隐私泄露、数据丢失、生产环境白屏/崩溃、无障碍阻断关键主流程。
- **P1 (严重级)**：用户可见的交互回归、API 或鉴权契约破损、React 水合失败 (Hydration Error)、核心交互失效。
- **P2 (重要级)**：具体的可维护性/性能/测试/可访问性缺陷，或明确违反项目核心设计规范。
- **P3 (建议级)**：轻微的代码整洁、冗余微调建议；仅在要求全面深度审计时输出。

### 输出格式

每个审查项明确呈现：
1. **[级别] 文件路径:行号**
2. **违反规则与缺陷说明**
3. **受影响场景与潜在风险**
4. **具体修正方案与代码示范**

如无发现问题，简短回答 `No issues found.` 并标明未覆盖的客观验证环境（如真机/浏览器视口差异）。
