# pstack 技能与工程原则目录 (Skills & Principles Index)

本目录汇集了 **pstack** 严谨软件工程套件中的全部 **47** 个专业技能（Skills）与工程原则（Principles），原生适配 **Google Antigravity**、**DeepSeek Harness (DSH)** 与 **Claude Code**。

---

## 目录索引

- [1. 核心调度与环境初始化](#1-核心调度与环境初始化)
- [2. 核心研发与对抗审查技能](#2-核心研发与对抗审查技能)
- [3. 探索、上下文与技术写作](#3-探索上下文与技术写作)
- [4. 23 个核心工程原则 (Principles)](#4-23-个核心工程原则-principles)
- [5. 在各智能体中的使用方式](#5-在各智能体中的使用方式)

---

## 1. 核心调度与环境初始化

| 技能 | 目录 | 核心用途与触发场景 |
|------|------|-------------------|
| **[`poteto-mode`](./poteto-mode/SKILL.md)** | `poteto-mode/` | **pstack 严谨工程主循环与任务调度总入口**。自动识别并映射到 23 个研发剧本（如 `bug-fix`, `feature`, `refactoring`, `perf`, `autonomous-run` 等），驱动子智能体分工协作与自愈。 |
| **[`setup-pstack`](./setup-pstack/SKILL.md)** | `setup-pstack/` | **模型角色映射与推理预算初始化**。自动探测宿主环境中的可用模型（如 Antigravity Pro/Flash 或 DSH R1/V3），配置高难度判断模型、快速机械执行模型及推理深度。 |

---

## 2. 核心研发与对抗审查技能

| 技能 | 目录 | 核心用途与触发场景 |
|------|------|-------------------|
| **[`architect`](./architect/SKILL.md)** | `architect/` | **架构与接口设计**：在编写代码前先行定义数据结构、类型签名与模块边界；生成架构决策记录 (ADR)。 |
| **[`arena`](./arena/SKILL.md)** | `arena/` | **方案竞技场**：并发派生多个独立候选方案分支，通过独立裁判模型对比评估，将败者中最强构件嫁接到胜者代码中。 |
| **[`swarm`](./swarm/SKILL.md)** | `swarm/` | **蜂群并行执行**：并发调度 N 个轻量工作者执行覆盖矩阵扫描、竞争性探索或独立子任务，归纳输出单份可审计报告。 |
| **[`interrogate`](./interrogate/SKILL.md)** | `interrogate/` | **多模型对抗质询**：派出多个独立审查子智能体，从边界条件、安全、可维护性等独立角度严苛审查代码，杜绝盲点。 |
| **[`tdd`](./tdd/SKILL.md)** | `tdd/` | **测试驱动开发**：精准编写失败测试用例证明缺陷或需求，编写最小实现直至通过，禁止编写未经调用的死代码。 |
| **[`create-verification-skill`](./create-verification-skill/SKILL.md)** | `create-verification-skill/` | **自动化验证技能生成**：为当前项目编写专属的行为级自动化验证脚本与功能地图，驱动应用像真实用户那样运行。 |
| **[`maintain-verification-skill`](./maintain-verification-skill/SKILL.md)** | `maintain-verification-skill/` | **验证技能维护与纠偏**：周期性多路源码审阅与真实会话驱动，修正过时或漂移的验证逻辑。 |
| **[`blast-radius`](./blast-radius/SKILL.md)** | `blast-radius/` | **爆炸半径评估**：在变更合并前深入分析潜在波及面，通过实际代码执行与调用链验证安全性，而非仅依靠静态推测。 |
| **[`figure-it-out`](./figure-it-out/SKILL.md)** | `figure-it-out/` | **复杂大任务策略制定**：面对大型重构、系统迁移或缺乏现成剧本的复杂工作时，构建假设驱动验证循环。 |
| **[`reflect`](./reflect/SKILL.md)** | `reflect/` | **计划复盘与多重视角把关**：派生三位平行评审者对当前会话中的计划与产出进行对抗性审阅，沉淀为技能改进。 |

---

## 3. 探索、上下文与技术写作

| 技能 | 目录 | 核心用途与触发场景 |
|------|------|-------------------|
| **[`how`](./how/SKILL.md)** | `how/` | **子系统与运行时机制走查**：梳理调用链、生命周期、分层归属与模块协作机制。 |
| **[`why`](./why/SKILL.md)** | `why/` | **历史决策深度考古**：跨 Git 历史、PR 讨论、设计文档、Sentry/Datadog 监控追溯决策背后的动机与权衡。 |
| **[`teach`](./teach/SKILL.md)** | `teach/` | **深入浅出的系统教学**：结合 `how` 与 `why` 产出通俗易懂的系统教学说明，帮助人类彻底理解。 |
| **[`recall`](./recall/SKILL.md)** | `recall/` | **上下文快速重构**：从近期对话历史、运行现场与日志中瞬间重建工作状态，快速接续中断的任务。 |
| **[`show-me-your-work`](./show-me-your-work/SKILL.md)** | `show-me-your-work/` | **决策证据链记录**：生成和维护 `decisions.tsv`，结构化记录每一步重大决策的动机、证据和结果。 |
| **[`unslop`](./unslop/SKILL.md)** | `unslop/` | **去 AI 啰嗦腔**：严格剔除所有 AI 常见的陈词滥调、长破折号连接词、空泛套话，确保输出纯粹干练。 |
| **[`no-comments`](./no-comments/SKILL.md)** | `no-comments/` | **代码去多余注释**：剔除代码中的过程自叙、死代码以及掩饰设计缺陷的补丁注释，保持代码自解释性。 |
| **[`technical-writing`](./technical-writing/SKILL.md)** | `technical-writing/` | **技术文档写作规范**：遵循 Diátaxis 四象限架构与 Google Developer Style 指南，产出专业严密的文档。 |
| **[`typescript-best-practices`](./typescript-best-practices/SKILL.md)** | `typescript-best-practices/` | **TypeScript 严格最佳实践**：掌握品牌类型、不可变状态、严格类型收窄与防腐层设计。 |
| **[`make-bot-ui`](./make-bot-ui/SKILL.md)** | `make-bot-ui/` | **Bot 控制面板生成**：为自动化 Bot 快速生成 Webhook 控制前端，支持 Tailscale 安全暴露。 |
| **[`bro`](./bro/SKILL.md)** | `bro/` | **大白话重述**：将上一条充满专业黑话的技术信息转化为最直白纯粹的人话。 |
| **[`automate-me`](./automate-me/SKILL.md)** | `automate-me/` | **个人习惯技能化**：根据真实工作流记录与偏好，提炼生成个性化的专属模式技能。 |

---

## 4. 23 个核心工程原则 (Principles)

每个原则均独立成一个可供智能体在编码和审查时随时加载遵循的技能约束：

### 核心思维原则 (Core Posture)
1. **[`principle-laziness-protocol`](./principle-laziness-protocol/SKILL.md)** — **极简主义协议**：偏好删除代码而非增加抽象；寻找解决问题的最小改动，严禁过度工程。
2. **[`principle-foundational-thinking`](./principle-foundational-thinking/SKILL.md)** — **基础性思考**：写业务逻辑前先梳理核心数据结构，数据结构对了，下游代码自然水到渠成。
3. **[`principle-redesign-from-first-principles`](./principle-redesign-from-first-principles/SKILL.md)** — **第一性原理重构**：引入新需求时，按“该需求第一天就存在”进行统一设计，杜绝层层补丁。
4. **[`principle-attack-the-premise`](./principle-attack-the-premise/SKILL.md)** — **攻击前提假设**：当基于同一前提的两次修复均告失败时，必须先质疑前提本身，而不是继续在错误假设上修修补补。
5. **[`principle-subtract-before-you-add`](./principle-subtract-before-you-add/SKILL.md)** — **先做减法再做加法**：重构或新增逻辑前，先清理陈旧死代码、废弃校验与桩函数。
6. **[`principle-minimize-reader-load`](./principle-minimize-reader-load/SKILL.md)** — **最小化阅读负荷**：折叠单次调用的无意义包装层，缩小可变作用域，降低读者心智负担。
7. **[`principle-outcome-oriented-execution`](./principle-outcome-oriented-execution/SKILL.md)** — **目标导向交付**：直奔目标架构，绝不编写临时拼凑但需丢弃的妥协兼容层。
8. **[`principle-experience-first`](./principle-experience-first/SKILL.md)** — **体验优先**：产品与体验权衡时，宁要少量精致打磨的功能，不要粗制滥造的堆砌。
9. **[`principle-exhaust-the-design-space`](./principle-exhaust-the-design-space/SKILL.md)** — **穷尽设计空间**：面对重大未知架构或全新交互，构建 2~3 组并行原型并列对比后再作定夺。
10. **[`principle-build-the-lever`](./principle-build-the-lever/SKILL.md)** — **打造杠杆工具**：对于批量修改或迁移，优先编写工具/脚本/codemod，让工具成为可重现审查的凭证。

### 架构与类型纪律 (Architecture & Domain)
11. **[`principle-model-the-domain`](./principle-model-the-domain/SKILL.md)** — **领域结构建模**：将业务逻辑固化在数据结构和状态机中，严禁在各处散落条件分支。
12. **[`principle-boundary-discipline`](./principle-boundary-discipline/SKILL.md)** — **边界防御纪律**：在系统边界（网络、CLI、配置）集中严格校验，内部逻辑完全信任纯函数。
13. **[`principle-type-system-discipline`](./principle-type-system-discipline/SKILL.md)** — **类型系统严谨性**：使非法状态不可表达，语义原语使用品牌类型，严禁向编译器说谎（如无脑断言）。
14. **[`principle-make-operations-idempotent`](./principle-make-operations-idempotent/SKILL.md)** — **操作幂等性设计**：脚本与处理循环必须能够在多次重试、崩溃恢复后收敛到确定的最终状态。
15. **[`principle-migrate-callers-then-delete-legacy-apis`](./principle-migrate-callers-then-delete-legacy-apis/SKILL.md)** — **彻底迁移并清理旧 API**：引入新内部 API 时，在同一批次内完成调用方迁移并彻底删除旧接口。
16. **[`principle-separate-before-serializing-shared-state`](./principle-separate-before-serializing-shared-state/SKILL.md)** — **消除共享优先于串行化**：在并发场景中，优先消除对共享状态的依赖，而非单纯加锁串行化。

### 验证与排错原则 (Verification & Quality)
17. **[`principle-prove-it-works`](./principle-prove-it-works/SKILL.md)** — **证明它确实有效**：根据真实运行时产物（实际执行、日志、抓包或 diff）证明成功，绝不接受“应该没问题”的口头保证。
18. **[`principle-fix-root-causes`](./principle-fix-root-causes/SKILL.md)** — **根因排查与修复**：遇到缺陷先稳定复现，连续追问根因，严禁使用空值判断（null check）掩盖系统崩溃。
19. **[`principle-sequence-verifiable-units`](./principle-sequence-verifiable-units/SKILL.md)** — **可独立验证的步骤编排**：将复杂任务拆分成每一步都可独立检验的最小交付单元。
20. **[`principle-test-behavior-not-implementation`](./principle-test-behavior-not-implementation/SKILL.md)** — **测试实际行为而非内部实现**：从用户或调用方视角发起测试，断言实际观测到的结果，杜绝无意义的桩函数模拟。

### 协作与上下文防护 (Meta & Context)
21. **[`principle-guard-the-context-window`](./principle-guard-the-context-window/SKILL.md)** — **守护上下文窗口**：海量输出与长篇日志通过子智能体隔离处理，主对话线程只保留关键决策摘要。
22. **[`principle-never-block-on-the-human`](./principle-never-block-on-the-human/SKILL.md)** — **可逆操作绝不阻塞人类**：可逆操作直接执行、呈现结果并保留回滚机制；仅在不可逆操作时请求人工确认。
23. **[`principle-encode-lessons-in-structure`](./principle-encode-lessons-in-structure/SKILL.md)** — **经验结构化沉淀**：当同一问题出现两次，将其转化为自动化 Lint 规则、脚本校验或技能约定，而非单纯口头嘱咐。

---

## 5. 在各智能体中的使用方式

### 在 Google Antigravity 中
- 技能已通过 `.agents/skills.json` 自动注册。
- 在对话中键入 `/<技能名>` 即可直接调用（例如 `/poteto-mode`、`/architect`、`/interrogate`）。
- 子智能体在执行任务时，会根据任务类型自主挂载相关的 `principle-*` 进行约束。

### 在 DeepSeek Harness (DSH) 中
- 本目录可直接作为 DSH 技能池挂载。
- 任务启动时，DSH 编排引擎读取对应 `SKILL.md` 指令，并为不同子角色（架构、审查、执行）分发专属原则。

### 在 Claude Code 中
- 直接在对话中通过 `/<skill-name>` 调用对应技能。
