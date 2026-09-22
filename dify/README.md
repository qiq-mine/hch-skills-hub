# Dify 全栈软件工程规范与代码审查套件 (Dify Engineering Skills Suite)

> 衍生自全球顶级开源 LLM 应用开发平台 [langgenius/dify](https://github.com/langgenius/dify) 官方工程规范。  
> 适配平台：**Google Antigravity**、**DeepSeek Harness (DSH)** 与 **Claude Code**。

---

## 概述

Dify 是目前全球最受欢迎的开源 LLM 应用与 Agent 编排框架之一。为了支撑海量高并发业务、复杂多租户隔离、丰富的工作流节点以及高度可扩展的设计系统，Dify 沉淀了一整套严密的软件工程标准与自动化审查技能。

本套件将 Dify 官方在 `.agents/skills` 中的工程实践完整重构与迁移，提供了覆盖全栈开发生命周期的 5 大核心专业技能：

1. **`backend-code-review`**：Python / Flask / SQLAlchemy 后端分层与高并发审查
2. **`frontend-code-review`**：React / Next.js / TypeScript 前端架构与可访问性审查
3. **`how-to-write-component`**：生产级 React 组件设计规范与状态所有权指南
4. **`frontend-testing`**：Vitest & React Testing Library (RTL) 行为测试优先规范
5. **`e2e-cucumber-playwright`**：Cucumber BDD (Gherkin) + Playwright 端到端测试体系

所有引用的规范文档（共 15 篇权威指南）已完整本地化内置于 `docs/` 目录中，确保所有链接百分百可达，离线与沙箱环境零故障运行。

---

## 核心技能详解

### 1. 后端工程审查 (`backend-code-review`)
- **入口**：`/backend-code-review`
- **目标技术栈**：Python 3.11+ / Flask / FastAPI / SQLAlchemy 2.0 / Alembic / PostgreSQL / MySQL
- **专属规则包**：
  - **架构分层 (`architecture-rule.md`)**：Controller 仅负责参数解析与响应返回；严格单向依赖 (Controller → Service → Core/Domain)；`libs/` 保持业务无关通用性。
  - **数据模型与迁移 (`db-schema-rule.md`)**：禁止在 Model `@property` 中发起跨表查询（防 N+1 爆炸）；强制包含 `tenant_id` 租户隔离字段；排查冗余索引；保障 PostgreSQL 与 MySQL 双向方言可移植性。
  - **存储库抽象 (`repositories-rule.md`)**：强制复用 Repository，防止服务层散落 ad-hoc 查询；复杂多表联查下沉存储库。
  - **SQLAlchemy 事务与并发 (`sqlalchemy-rule.md`)**：显式 Session/事务边界；SQLAlchemy Core 表达式优于原生 SQL；写入路径并发安全（乐观锁版本号、Redis 分布式锁、`SELECT FOR UPDATE`）。

### 2. 前端工程审查 (`frontend-code-review`)
- **入口**：`/frontend-code-review`
- **目标技术栈**：React 19 / Next.js / TypeScript 5+ / Tailwind CSS v4 / TanStack Query / Dify UI / Base UI
- **专属规则包**：
  - **无障碍访问 (`accessibility-ui.md`)**：可访问名称计算、按钮与链接语义隔离、Focus Trap、键盘导航。
  - **设计系统基元 (`dify-ui.md`)**：Dify UI / Base UI 设计规范、浮层契约 (`overlays.md`)、表单契约 (`forms.md`)。
  - **组件架构与数据流 (`component-architecture.md`)**：容器与展示解耦、Props 最小化、状态下沉。
  - **数据请求契约 (`data-query-contracts.md`)**：TanStack Query 结构化 Key、乐观更新与精确缓存失效。
  - **运行时稳定不变量 (`dify-invariants.md`)**：Workflow 节点与 RAG Pipe 上下文隔离保护。
  - **性能与测试 (`performance.md` & `testing.md`)**：消灭无效重渲染、避免瀑布式请求、补齐回归测试。
  - **代码与样式质量 (`code-quality.md`)**：严格类型安全、Tailwind v4 标准类名。

### 3. 组件设计规范 (`how-to-write-component`)
- **入口**：`/how-to-write-component`
- **目标技术栈**：React / Next.js / TypeScript
- **决策维度**：
  - **边界所有权 (`ownership.md`)**：单一职责、状态存放层级判定、避免 Prop Drilling。
  - **状态生命周期 (`state.md`)**：本地状态 (`useState`)、跨组件状态 (Jotai/Zustand)、表单草稿状态、URL 查询参数状态分级。
  - **交互与次级浮层 (`interactions.md`)**：模态框、抽屉、气泡卡片与下拉菜单无障碍交互。
  - **运行时生命周期 (`runtime.md`)**：严防 `useEffect` 滥用、避免数据同步派生 Effect、注销事件监听。
  - **Tailwind 现代规范**：采用 v4 标准类名（如 `w-105`, `px-2.25`, `bg-linear-to-b`, `field-sizing-content`）。

### 4. 前端行为测试 (`frontend-testing`)
- **入口**：`/frontend-testing`
- **目标技术栈**：Vitest / React Testing Library (RTL) / Mock Service Worker (MSW)
- **核心标准**：
  - **测试行为而非实现 (Behavior over Implementation)**：黑盒用户视角测试，组件内部重构不导致用例失败。
  - **无障碍查询选择器**：`getByRole` > `getByLabelText` > `getByPlaceholderText` > `getByText`（严禁使用 CSS 类名或 DOM 路径定位）。
  - **真实交互模拟**：始终使用 `@testing-library/user-event` 替代底层 `fireEvent`。
  - **Mock 纪律**：仅在网络层 (MSW) 与浏览器特定 API 处 Mock，严禁 Mock 内部组件或 internal hooks。

### 5. 端到端自动化测试 (`e2e-cucumber-playwright`)
- **入口**：`/e2e-cucumber-playwright`
- **目标技术栈**：Cucumber.js (BDD/Gherkin) / Playwright / TypeScript
- **核心标准**：
  - **双引擎分工**：Cucumber 管理业务场景描述与 Hook 生命周期；Playwright 提供高保真无头浏览器驱动。
  - **声明式 Gherkin**：描述业务目标而非流水账点击动作；高度复用 Steps。
  - **Web-first 异步断言**：依赖 Playwright 内置 Auto-waiting，彻底杜绝任意 `sleep`。

---

## 缺陷分级标准 (Severity Matrix)

审查模式统一采用 P0 至 P3 工业级缺陷分级：

| 级别 | 严重度 | 判定准则 |
|------|-------|---------|
| **P0** | 阻断级 | 安全漏洞、租户隔离穿透、数据损毁、全系统级宕机或关键主流程不可用 |
| **P1** | 严重级 | 用户可见的功能回归、越权风险、破坏公共契约、React 水合崩溃 |
| **P2** | 重要级 | 可复现的逻辑缺陷、性能劣化（如 N+1 查询/大树频繁重渲染）、事务失控、A11y 障碍 |
| **P3** | 建议级 | 轻微的代码整洁、微小可优化点（仅在全量深度审计时输出） |

---

## 本地化权威文档索引 (`docs/`)

| 文档名称 | 内容简述 |
|---------|---------|
| [`authoring.md`](./docs/authoring.md) | Dify UI 基元组件公共 API 架构设计指南 |
| [`styling.md`](./docs/styling.md) | 样式设计系统、设计 Tokens 与 Tailwind CSS 规范 |
| [`overlays.md`](./docs/overlays.md) | 对话框、抽屉、气泡浮层与下拉菜单规范 |
| [`forms.md`](./docs/forms.md) | 表单控件、校验状态与字段语义契约 |
| [`selection.md`](./docs/selection.md) | 单选、多选、下拉与受控组件规范 |
| [`accessible-names-and-descriptions.md`](./docs/accessible-names-and-descriptions.md) | 无障碍计算名称与描述权威标准 |
| [`testing.md`](./docs/testing.md) | 基元组件库单元测试与 Storybook 指南 |
| [`test.md`](./docs/test.md) | Web 前端完整测试边界、环境与 CI 指南 |
| [`lint.md`](./docs/lint.md) | 前端代码静态检查与规范约束 |
| [`landmarks.md`](./docs/landmarks.md) | Web 页面语义地标结构标准 |
| [`truncated-text-disclosure.md`](./docs/truncated-text-disclosure.md) | 文本截断与展开浮层模式规范 |
| [`api-agents.md`](./docs/api-agents.md) | 后端 API 系统架构总约 |
| [`web-agents.md`](./docs/web-agents.md) | Web 前端系统架构总约 |
| [`dify-ui-agents.md`](./docs/dify-ui-agents.md) | Dify UI 模块架构总约 |
| [`e2e-agents.md`](./docs/e2e-agents.md) | 端到端自动化架构总约 |

---

## 使用方式

### 在 Google Antigravity 中使用
本套件已在根目录 `.agents/skills.json` 与 `.agents/plugins.json` 中完成注册。在会话中可直接通过以下方式调用：
- `/dify` — 查看套件总览并规划全栈开发任务
- `/backend-code-review` — 审查后端变更
- `/frontend-code-review` — 审查前端变更
- `/how-to-write-component` — 寻求组件设计与重构指引
- `/frontend-testing` — 编写前端行为单元测试
- `/e2e-cucumber-playwright` — 编写与审查端到端测试

### 在 DeepSeek Harness (DSH) 中使用
- 将 `dify` 目录挂载为 DSH 技能包，智能体根据审查对象或开发需求自动分发对应规则包。

### 在 Claude Code 中使用
- 键入 `/<skill-name>` 即可激活相应能力。
