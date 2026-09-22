---
name: e2e-cucumber-playwright
description: "Dify 端到端 (E2E) 自动化测试技能。基于 Cucumber BDD (Gherkin) 与 Playwright 浏览器自动化框架，指导测试用例编写、步骤定义 (Step Definitions)、World 状态管理、场景标签划分、稳健选择器设计 (Locators)、智能自动等待与多租户测试上下文隔离。Triggers: e2e-cucumber-playwright, /e2e-cucumber-playwright, e2e, 端到端测试, cucumber, playwright, dify-e2e."
---

# E2E Cucumber & Playwright (Dify 端到端测试)

面向复杂 Web 应用的端到端 (E2E) 行为驱动自动化测试技能。采用 **Cucumber (BDD/Gherkin)** 管理业务场景与执行生命周期，结合 **Playwright** 进行高保真跨浏览器自动化、状态断言与追踪录制。

## 体系架构与责任划分

- **Cucumber**：负责场景语义编排 (`.feature` 文件)、Hook 生命周期、场景标签 (`@tags`)、执行流程与测试报告。
- **Playwright**：提供浏览器 Context、页面实例、Locators、用户行为模拟、页面级断言 (`expect(locator)`)、网络拦截与 Tracing 记录。
- **配置与契约路由**：完整套件生命周期契约、标签分类与清理规则遵循 [`e2e/AGENTS.md`](../../docs/e2e-agents.md)。

> **注意**：两者的超时机制完全独立。从 `@playwright/test` 导入断言不会将 Playwright 原生测试运行器的重试或 fixtures 机制自动应用到 Cucumber 运行器中。

## 专题指引路由 (Topic Routing)

| 关注领域 | 规则与参考 | 核心要求 |
|---------|-----------|---------|
| **Playwright 定位与等待** | [`references/playwright-best-practices.md`](references/playwright-best-practices.md) | 优先使用面向用户的无障碍选择器 (`getByRole`, `getByLabel`)、依赖 Playwright 内置 Auto-waiting、杜绝硬等待、断言使用异步 Web-first assertions |
| **Cucumber 场景与步骤设计** | [`references/cucumber-best-practices.md`](references/cucumber-best-practices.md) | 声明式业务描述优于机械性操作描述、步骤高复用、避免在 Gherkin 中暴露 DOM 细节、World 实例管理临时会话状态 |

## E2E 实施与维护工作流

1. **守卫 E2E 边界**：仅为跨越前后端/数据持久化边界的**核心用户旅程 (Critical User Journey)** 编写 E2E 测试；凡是单元测试或集成测试能低成本证实的逻辑，坚决不在 E2E 中重复堆叠。
2. **基于真实产品默认状态**：从真实产品角色与默认设置开始测试；Setup 阶段可准备必要前提数据，但切忌为使测试通过而制造脱离生产实际的畸形数据。
3. **步骤复用优先**：在新增步骤前，充分检索现有步骤定义文件；当语义与行为一致时直接复用，避免产生同义不同词的冗余 steps。
4. **测试选择器与断言置于公共边界**：浏览器动作与可见断言必须紧贴用户界面；数据库数据准备、API 数据生成和 teardown 清理应通过辅助函数或专属 hooks 驱动。
5. **最小范围执行验证**：调试或修改时，仅运行带有最小特定标签的场景（如 `cucumber-js --tags @current`）；只有在改动共享 hook 或核心 support 代码时才执行全量套件。

## 审查与排错规范

在审查或排错 E2E 测试时：
- **消灭不稳定源 (Flakiness)**：排查任意 `sleep()`、时间差竞争、未受控的动画过渡、依赖外部不稳定网络服务等问题。
- **架构防漂移**：防止在 steps 中直接散落脆弱的 XPath/CSS 选择器，统一封装至 Page Objects 或语义化 Locators。
- **报告验证证据**：说明验证过的具体业务行为，以及任何因外部依赖环境造成的验证空缺。
