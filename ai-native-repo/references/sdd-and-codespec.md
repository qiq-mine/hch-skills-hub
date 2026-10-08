# SDD Five Phases & CodeSpec (AI Native Repo)

## SDD：AR → 代码交付（适用：功能级、跨模块需求）

CLI 持有状态，`state.json` 为唯一真相源。Agent 只产内容，不推进状态；
状态推进必须有人确认（`sdd approve`）；`sdd advance` 被门禁卡住时必须
报错缺谁的确认，不得跳过。

| 阶段 | 产出物 | Agent 职责 | 人确认（门禁） | CLI |
|---|---|---|---|---|
| 1 需求澄清 | `01-*.md`（RQ-*） | 访谈式提炼、列边界与非目标、起草验收标准初稿 | G1：需求边界、非目标 | `sdd init`（建五文档骨架） |
| 2 功能规格 | `02-*.md`（FR-*/AC-*） | 写"做什么不写怎么做"，每条 FR 配 AC | G2：范围、验收标准 | `sdd approve`（记录确认） |
| 3 实现设计 | `03-*.md`（D-*，链 ADR） | 模块划分、数据模型、API 契约（引用 `spec/`） | G3：架构决策、技术选型 | `sdd advance`（门禁通过后推进） |
| 4 任务拆解 | `04-*.md`（T-* ↔ FR-*） | 拆到 0.5–2 天粒度，标依赖与并行度 | G4：拆解粒度、并行策略 | `sdd advance`（门禁通过后推进） |
| 5 一致性验证 | `05-*.md` | 机械检查：FR 全有 AC、AC 全有 T、T 全有测试映射；无孤儿需求、无野任务 | G5：报告确认（可转自动+抽查） | `sdd verify`（跑一致性检查） |

- 追溯链：RQ-* → FR-*/AC-* → D-* → T-* → commit → test。断链即打回上一阶段。
- 文档落点：`spec/sdd/<feature>/` 下五份文档 + `state.json`。
- `sdd task claim|complete` 用于验证通过后的实现阶段（状态机 `verified → implementing`），不属于五文档阶段。
- 常用：`sdd status`（看阶段/状态）。

## CodeSpec：代码级契约驱动（适用：模块内、接口密集的实现）

spec 与代码同生命周期，**spec 即测试**。

1. **契约编写**：agent 从 `02-functional-spec.md` 生成 `*.codespec.yaml`（接口签名、前后置条件、不变量、可执行验收用例）；人确认接口形状。
2. **桩生成**：CLI 从 CodeSpec 生成类型定义 + 测试桩（codegen 沉淀到 `tools/`）。
3. **实现**：agent 填实现，**不得改契约**；契约要改必须回流到 CodeSpec + 人确认。
4. **契约验证**：CLI 跑 contract tests + property tests；AC-* 映射到用例；失败即打回。
5. **回归归档**：CodeSpec 随代码版本化，成为活文档；下次改接口先改 CodeSpec。

**与五阶段的关系**：CodeSpec 是第 3→4 阶段的下钻——`03-design.md` 引用
CodeSpec 文件；T-* 任务的验收标准即"对应 CodeSpec 的 contract tests 全绿"。
大功能走五阶段，模块内实现走 CodeSpec。
