---
name: dify
description: "Dify 全栈软件工程规范与代码审查技能套件（面向生产级 LLM 应用开发）。深度适配 Google Antigravity、DeepSeek Harness (DSH) 与 Claude Code。涵盖 Python/Flask/SQLAlchemy 后端审查、React/Next.js/TypeScript 前端审查、组件架构设计、Vitest/RTL 前端测试与 Cucumber/Playwright 端到端自动化测试。Triggers: dify, /dify, dify code review, dify component, dify testing, dify e2e, dify全栈工程."
license: Apache-2.0
metadata:
  author: langgenius
  homepage: https://github.com/langgenius/dify
  version: "1.0.0"
---

# Dify — 全栈软件工程规范与代码审查技能套件

> 原作：Dify 官方团队 ([langgenius/dify](https://github.com/langgenius/dify)) | 适配：Google Antigravity & DeepSeek Harness (DSH)

Dify 是一套支撑全球顶尖开源 LLM 应用开发平台的技术工程规范。其核心理念是 **"Evidence First & Boundary Discipline"** —— 强调在现代复杂全栈体系中，通过严密的分层架构、可观测的行为契约、多租户严格隔离、可访问性基元标准以及自动化测试梯队，保障生产级系统的稳定演进与高质量交付。

---

## 套件技能全景

```
                                          ┌── [后端审查] backend-code-review
                                          │     ├─ 架构分层 / 租户隔离 / 仓库抽象
                                          │     └─ 显式事务 / 并发锁 / PG/MySQL 兼容
                                          │
                                          ├── [前端审查] frontend-code-review
                                          │     ├─ A11y 无障碍 / Dify UI 契约 / 数据状态
                                          │     └─ 运行时不变量 / 重渲染性能 / 测试覆盖
                                          │
目标任务 ──▶ /dify (或直接调用对应子技能) ──┼── [组件编写] how-to-write-component
                                          │     ├─ 容器与展示解耦 / 状态生命周期分级
                                          │     └─ 浮层契约 / Effect 严管 / Tailwind v4
                                          │
                                          ├── [前端测试] frontend-testing
                                          │     └─ Vitest + RTL / 行为测试优先 / 系统边界 Mock
                                          │
                                          └── [端到端测试] e2e-cucumber-playwright
                                                └─ Cucumber BDD + Playwright / Web-first 断言
```

---

## 包含技能一览

### 1. 后端工程审查 ([`backend-code-review`](./skills/backend-code-review/SKILL.md))
- **定位**：面向 Python / Flask / FastAPI / SQLAlchemy 后端代码的高质量审查。
- **审查维度**：
  - **分层边界**：Controller 保持极简，业务逻辑下沉 Service/Domain，`libs/` 保持业务无关。
  - **数据模型与迁移**：强制 `tenant_id` 租户字段、禁止在 `@property` 中发起跨表查询、消灭冗余前缀索引、PostgreSQL/MySQL 双向兼容。
  - **存储库抽象**：强制复用 Repository 接口，禁止业务层直接使用 ad-hoc SQLAlchemy 查询。
  - **SQLAlchemy 与并发**：显式会话事务边界、SQLAlchemy 表达式替代原生 SQL、并发防护（乐观锁、Redis 分布式锁、`with_for_update`）。

### 2. 前端工程审查 ([`frontend-code-review`](./skills/frontend-code-review/SKILL.md))
- **定位**：面向 React / Next.js / TypeScript 前端应用与 UI 库的代码审查。
- **审查维度**：
  - **无障碍访问 (A11y)**：可访问名称计算、按钮/链接语义、Focus Trap、键盘导航。
  - **设计系统基元**：Dify UI / Base UI 设计契约、Tokens 引用、Overlays 浮层与表单规范。
  - **组件架构与数据流**：Props 最小化、状态下沉、TanStack Query 结构化请求与乐观更新。
  - **运行时稳定不变量**：Workflow 节点与 RAG Pipe 独立挂载上下文防护。
  - **性能与测试**：消除大树无效重渲染、避免请求瀑布、补全回归用例。

### 3. 组件设计与编写规范 ([`how-to-write-component`](./skills/how-to-write-component/SKILL.md))
- **定位**：编写或重构 React/TypeScript 组件时的架构指南。
- **核心指导**：
  - **组件边界**：容器组件 (Container) 与展示组件 (Presentation) 清晰解耦。
  - **状态生命周期**：局部状态 (`useState`)、跨组件状态 (Jotai)、表单草稿状态、URL 查询参数状态分级。
  - **次级交互表面**：对话框 (Dialog)、气泡卡片 (Popover)、下拉菜单 (Dropdown) 的标准接入。
  - **Tailwind CSS 现代化用法**：推荐 Tailwind v4 规范类名（如 `w-105`, `px-2.25`, `wrap-break-word`）。

### 4. 前端测试规范 ([`frontend-testing`](./skills/frontend-testing/SKILL.md))
- **定位**：使用 Vitest 与 React Testing Library (RTL) 进行行为级测试。
- **核心指引**：
  - **行为测试优先**：以真实用户可观察的界面变化与无障碍状态为断言目标，不测组件内部 state。
  - **查询优先级**：`getByRole` > `getByLabelText` > `getByPlaceholderText` > `getByText`。
  - **交互模拟与 Mock 边界**：基于 `user-event` 进行事件派发；仅在网络层 (MSW) 与浏览器特有 API 处进行 Mock，严禁 Mock 内部子组件。

### 5. 端到端自动化测试 ([`e2e-cucumber-playwright`](./skills/e2e-cucumber-playwright/SKILL.md))
- **定位**：基于 Cucumber BDD (Gherkin) 与 Playwright 的全链路集成测试。
- **核心指导**：
  - **双引擎分工**：Cucumber 管理业务场景语言与 Hook 生命周期；Playwright 负责高保真浏览器执行与 Web-first 异步断言。
  - **场景设计**：聚焦关键用户旅程 (Critical User Journeys)，高复用步骤定义，消灭硬编码 DOM 选择器与任意 sleep。

---

## 缺陷分级标准 (Severity Grading)

全套件统一实行 P0 至 P3 的工业级缺陷分级：

| 级别 | 严重度 | 定义与触发场景 |
|------|-------|----------------|
| **P0** | 阻断级 | 安全漏洞、敏感数据泄露、租户隔离穿透、数据损坏或丢失、线上白屏/崩溃 |
| **P1** | 严重级 | 核心业务流程受阻、用户可见的功能回归、未授权访问、破坏公共 API 契约、水合严重失败 |
| **P2** | 重要级 | 可复现的逻辑缺陷、性能劣化（如 N+1 查询/大树无效渲染）、未受控事务、A11y 阻断、违反项目既定工程契约 |
| **P3** | 建议级 | 轻度可读性微调、局部代码异味建议（通常仅在明确要求全量审计时输出） |

---

## 权威规范与参考文档索引

所有规则引用的权威文档均已内嵌并本地化保存在 [`docs/`](./docs/) 目录中，确保无网络依赖与相对路径 100% 可达：

- **设计系统与组件规范**：
  - [`authoring.md`](./docs/authoring.md) — Dify UI 公共 API 设计契约
  - [`styling.md`](./docs/styling.md) — 样式设计系统与 Tailwind 规范
  - [`overlays.md`](./docs/overlays.md) — 模态框、浮层与弹出菜单契约
  - [`forms.md`](./docs/forms.md) — 表单控件与字段校验语义
  - [`selection.md`](./docs/selection.md) — 选择器与受控组件规范
  - [`accessible-names-and-descriptions.md`](./docs/accessible-names-and-descriptions.md) — 无障碍名称与描述标准
- **测试与工程流水线**：
  - [`testing.md`](./docs/testing.md) — 基元组件库测试标准
  - [`test.md`](./docs/test.md) — Web 前端完整测试规范与边界
  - [`lint.md`](./docs/lint.md) — ESLint / Prettier / 静态检查规范
  - [`landmarks.md`](./docs/landmarks.md) — Web 页面结构地标与语义规范
- **各子系统 Agent 协议**：
  - [`api-agents.md`](./docs/api-agents.md) — 后端 Python/Flask 架构总约
  - [`web-agents.md`](./docs/web-agents.md) — 前端 Next.js 架构总约
  - [`dify-ui-agents.md`](./docs/dify-ui-agents.md) — Dify UI 模块总约
  - [`e2e-agents.md`](./docs/e2e-agents.md) — 端到端自动化架构总约

---

## 快速使用方式

### 在 Google Antigravity 中使用
- 直接通过斜杠命令调用指定技能：
  - 审查后端变更：`/backend-code-review [可指定文件或diff]`
  - 审查前端变更：`/frontend-code-review [可指定组件]`
  - 指导编写组件：`/how-to-write-component [要开发的组件需求]`
  - 编写前端单测：`/frontend-testing [待测组件]`
  - 编写 E2E 用例：`/e2e-cucumber-playwright [业务场景需求]`
  - 全套件总览：`/dify`

### 在 DeepSeek Harness (DSH) 中使用
- 智能体会自动根据审查目标（如 Python 后端文件或 React 前端文件）加载对应的 `SKILL.md` 与参考规则包，输出结构化 P0~P3 评审报告。

### 在 Claude Code 中使用
- 直接键入 `/<skill-name>` 即可激活相应规范流程。
