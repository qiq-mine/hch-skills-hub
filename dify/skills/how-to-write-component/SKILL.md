---
name: how-to-write-component
description: "Dify React/TypeScript 组件设计与编码规范技能。指导组件分层与所有权划分 (ownership)、状态生命周期分级 (state/Jotai/URL)、数据获取与缓存变异 (data/TanStack Query)、用户交互与浮层契约 (interactions/overlays)、运行时优化 (runtime/effects) 以及 Tailwind CSS v4 标准用法。Triggers: how-to-write-component, /how-to-write-component, 写组件, 组件设计, React组件规范, 前端组件架构."
---

# How To Write A Component (Dify 组件设计规范)

面向 React / Next.js / TypeScript 体系的组件设计与架构指导技能。在设计、重构或开发组件时，协助做出关于组件边界、数据流、状态层级、次级界面（模态框/抽屉/下拉菜单）以及运行时性能的正确决策。

## 架构决策路由 (Topic Routing)

根据当前面临的开发决策，查阅对应参考文档：

| 决策领域 | 核心参考文档 | 关键指引与原则 |
|---------|------------|---------------|
| **组件边界与所有权** | [`references/ownership.md`](references/ownership.md) | 区分容器（Container/Feature）与纯展示（Presentation）；Props 接口精准化，避免 Prop Drilling，明确单一责任主体 |
| **设计系统基元开发** | [`authoring.md`](../../docs/authoring.md) 与 [`styling.md`](../../docs/styling.md) | `@langgenius/dify-ui` 基元规范、组合模式 (Compound Components)、Base UI 包装原则、无障碍焦点与类名合并 |
| **状态生命周期与分层** | [`references/state.md`](references/state.md) | 状态分层机制：本地状态 (`useState`)、跨组件状态 (Jotai/Zustand)、表单草稿 ([表单契约](../../docs/forms.md))、路由与 URL 状态 (`useSearchParams`)、持久化隔离 |
| **数据获取与服务端契约** | [`references/data.md`](references/data.md) | TanStack Query 结构化调用、Nullable 字段防御、Mutations 乐观更新与精确缓存失效、SSR 水合一致性、工作区租户隔离 |
| **交互事件与浮层表面** | [`references/interactions.md`](references/interactions.md) | 快捷键与键盘导航、焦点恢复与陷阱、对话框/气泡/下拉等次级浮层规范 ([浮层规范](../../docs/overlays.md)) |
| **运行时生命周期与性能** | [`references/runtime.md`](references/runtime.md) | 严控 `useEffect`（绝不用 Effect 同步本可由计算派生的状态）、事件监听自动注销、昂贵计算 memo 化、渲染开销优化 |

## Tailwind CSS 规范建议

遵循现代 Tailwind CSS 最佳实践：
- 优先采用标准类名，避免任意值方括号写法（如 `w-105` 优于 `w-[420px]`，`px-2.25` 优于 `px-[9px]`）。
- 渐变色推荐 `bg-linear-to-b`，长词断行采用 `wrap-break-word`。
- 表单与多行输入采用 `field-sizing-content`。

## 验证与测试规范

在完成组件编写后，根据归属层级执行相应验证：
- 业务页面组件：查阅 [`web/docs/test.md`](../../docs/test.md) 与 [`web/docs/lint.md`](../../docs/lint.md) 进行单元测试与静态审查。
- 设计系统基元组件：查阅 [`packages/dify-ui/docs/testing.md`](../../docs/testing.md) 编写组件用例与 Storybook 场景。
