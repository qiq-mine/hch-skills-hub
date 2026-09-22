---
name: frontend-testing
description: "Dify 前端测试技能。指导使用 Vitest 与 React Testing Library 编写与维护高质量单元及集成测试。涵盖行为测试优先 (Testing Behavior Not Implementation)、选择器优先级规范 (getByRole > getByLabelText > getByText)、用户交互模拟 (userEvent)、外部边界 Mock 纪律 (MSW/浏览器 API)、异步等待处理 (waitFor/findBy) 及低效测试精简。Triggers: frontend-testing, /frontend-testing, 前端测试, React单元测试, Vitest测试, RTL测试."
---

# Frontend Testing (Dify 前端测试规范)

面向现代 React / Next.js / TypeScript 应用的单元测试与组件集成测试指导技能。基于 Vitest 与 React Testing Library (RTL)，坚持“测试用户可观察行为而非实现细节”，编写高置信度、抗重构的健壮测试套件。

## 核心哲学：测试行为而非实现细节 (Behavior Over Implementation)

1. **黑盒用户视角**：测试组件的方式应当与真实用户（或无障碍辅助技术）使用组件的方式完全一致。
2. **抗内部重构**：重构组件内部实现（如将 `useState` 改为 `useReducer`，或拆分子组件）时，测试用例不应因此失败。
3. **断言观察结果**：断言屏幕上的实际渲染内容、无障碍树状态、焦点流转或对外触发的事件契约，而非组件内部 state 变量。

## 选择器优先级规范 (Query Priority)

严格遵循 Testing Library 官方推荐的可访问性查询优先级：

1. **`getByRole`**（最高优先级）：最接近辅助技术与真实用户的查找方式（例如 `getByRole('button', { name: /提交/i })`）。
2. **`getByLabelText`**：表单控件的首选方式（例如 `getByLabelText(/邮箱地址/i)`）。
3. **`getByPlaceholderText`**：无关联 label 时的表单次选。
4. **`getByText`**：非交互式内容（如段落、标题文本、提示信息）。
5. **`getByDisplayValue`**：表单预填充或当前输入值的查找。
6. **`getByTestId`**（最后手段）：仅在文本动态多变或无法通过无障碍属性稳定定位时作为兜底（如 `data-testid="code-editor-canvas"`）。**严禁使用 CSS 类名或 DOM 路径查询**。

## 交互模拟与异步纪律

### 1. 用户交互模拟 (`user-event`)
- **始终优先使用 `@testing-library/user-event`**，而非底层的 `fireEvent`。
- `userEvent` 会完整模拟真实用户的焦点移动、按键事件、光标交互和状态触发：
  ```tsx
  // 推荐
  const user = userEvent.setup();
  await user.type(screen.getByRole('textbox', { name: /搜索/i }), 'Agent');
  await user.click(screen.getByRole('button', { name: /确定/i }));
  ```

### 2. 异步状态与等待 (`waitFor` / `findBy*`)
- **严禁使用任意 `sleep()` 或 `setTimeout()`**。
- 获取异步渲染的元素使用 `await screen.findByRole(...)`。
- 轮询等待状态断言使用 `await waitFor(() => expect(...).toBeInTheDocument())`。
- 保持 `waitFor` 回调内纯粹，仅包含单项断言。

## Mock 边界规范 (Mocking Boundaries)

1. **仅在系统边界 Mock**：
   - 网络 I/O：推荐使用 MSW (Mock Service Worker) 拦截 HTTP 请求，而非 mock 业务内部的数据请求函数。
   - 浏览器环境特有 API：在测试 setup 中 mock `ResizeObserver`、`IntersectionObserver`、`window.matchMedia` 等 jsdom 不支持的接口。
2. **禁止 Mock 内部组件**：不要为了测试父组件而把子组件替换为 dummy mock，这会彻底破坏集成测试的真实信任度。
3. **禁止 Mock 内部 Hooks**：测试组件对 hook 的调用结果，而非 mock hook 本身。

## 包级测试政策路由 (Policy Routing)

- **Web 业务应用测试**：遵循 [`web/docs/test.md`](../../docs/test.md) 中关于执行环境、目录约定及 CI 运行命令的要求。
- **UI 设计系统基元测试**：遵循 [`packages/dify-ui/docs/testing.md`](../../docs/testing.md) 关于 Base UI 行为覆盖与 Storybook 场景规范。

## 测试维护与瘦身

低价值测试（如测试仅仅验证 React 自身能否正确渲染 div、测试无逻辑纯展示的文本）不仅增加维护开销，还会造成虚假安全感。**勇于删除只测试实现细节或脆弱断言的低价值测试，补充关键业务主流程和错误边界测试**。
