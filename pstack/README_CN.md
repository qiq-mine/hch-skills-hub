# pstack — 严谨 AI 软件工程工作流与技能套件

> 原作者：Lauren Tan ([@poteto](https://x.com/poteto)) | 适配：Google Antigravity、DeepSeek Harness (DSH) 与 Claude Code。
> [English Version](./README.md) | [技能与原则总览](./skills/README.md)

人们越来越深切地感受到：AI 编写了太多缺乏质量保证的“垃圾代码”（Slop Code）。单纯追求代码生成速度和代码行数（LOC）不仅毫无意义，还会带来巨大的技术债务。如果你想走得快，先要走得深（**Go deep first**）。

**pstack 正是为此而生。** 这是一套经过高强度实战检验的结构化技能套件，旨在将 AI 编程智能体打造成一支纪律严密、具备资深工程师素养的研发团队。其目标绝不是堆砌代码行数，而是交付经过真实验证、精炼且高质量的代码。

**pstack 赋予你无所畏惧的并行能力（Fearless Parallelism）。** 当你深入理解并信任单个智能体能够遵循严谨原则产出可靠代码时，你就能放心地进行大规模并发。通过 `/poteto-mode` 驱动多个智能体协同，确保它们全生命周期贯彻严谨的软件工程纪律。

---

## pstack 包含什么？

- **1 个核心调度入口**：[`/poteto-mode`](./skills/poteto-mode/SKILL.md) 与 [`pstack`](./SKILL.md)
- **23 个任务剧本 (Playbooks)**：涵盖缺陷排查、性能调优、新功能开发、重构、运行时取证、发版审查等标准化操作指南
- **23 个工程原则 (Principles)**：硬性工程约束，指导子智能体思考，从源头杜绝 AI 乱象与过度工程
- **11 个核心工作流技能**：`architect`, `arena`, `swarm`, `interrogate`, `how`, `why`, `unslop`, `no-comments`, `tdd`, `show-me-your-work`, `create-verification-skill` 等
- **专属智能体角色**：`poteto-agent`（严谨工程专家）、`comment-sicko`（代码注释审查员）

完整技能列表请参阅：**[skills/README.md](./skills/README.md)**

---

## 运行环境兼容性：Antigravity 与 DeepSeek Harness (DSH)

本版本经过彻底的解耦与现代化重构，完全移除了旧版对 Cursor 专有闭源机制的依赖：

| 能力维度 | Cursor 专有旧版 | Antigravity 原生支持 | DeepSeek Harness (DSH) 原生支持 |
|---|---|---|---|
| **子智能体调度** | `Task(subagent_type: ...)` | `invoke_subagent` (TypeName: `self`/`research`) | DSH Subagent Runner / Task Plugin |
| **高难度判断模型** | `claude-fable-5-1-thinking-max` | `Model: "pro"` (深度推理) | `deepseek-reasoner` (R1 思考模型) |
| **快速机械执行模型**| `grok-4.6-fast-xhigh` | `Model: "flash"` (高吞吐) | `deepseek-chat` (V3 极速编码) |
| **交互式确认提问**| `AskQuestion` | `ask_question` 工具 | 终端命令行交互提示 |
| **配置规则存储** | `~/.cursor/rules/pstack-models.mdc` | `.agents/rules/pstack-models.md` / `GEMINI.md` | `.dsh/rules/` / `AGENTS.md` |
| **会话与轨迹日志** | `~/.cursor/projects/...` | `<appDataDir>/brain/<id>/.../transcript.jsonl` | Session Log 工作目录 |
| **无人值守自治运行**| `/loop` 命令 | `/goal` 命令 / `schedule` 调度工具 | DSH 状态监视自愈循环 |

---

## 快速上手

仅需两步即可开启严谨工程模式：

1. **环境初始化与模型配置**：运行 [`/setup-pstack`](./skills/setup-pstack/SKILL.md)，自动探测当前环境中的可用大模型，设定判断模型与机械执行模型并分配置信度预算。
2. **启动严谨工程主循环**：每当面对需要严密推导和高质量交付的任务时，运行 [`/poteto-mode`](./skills/poteto-mode/SKILL.md)：

```bash
/poteto-mode 该接口在高并发下存在竞态条件。先写测试复现，追查根本原因，再进行根治修复并进行运行时验证。
```

---

## 23 个标准化任务剧本 (Playbooks)

位于 `skills/poteto-mode/playbooks/` 目录下，由 `/poteto-mode` 自动调度：

| 剧本名称 | 核心目标与应用场景 |
|---|---|
| [investigation](./skills/poteto-mode/playbooks/investigation.md) | **只读式探索**：系统如何运作、某项设计为什么这样实现。 |
| [bug fix](./skills/poteto-mode/playbooks/bug-fix.md) | **缺陷修复**：先通过用例稳定复现，追查根因，基于运行时真实产物闭环验证。 |
| [perf](./skills/poteto-mode/playbooks/perf-issue.md) | **性能分析**：测量性能瓶颈，对照基准数据进行针对性提速。 |
| [hillclimb](./skills/poteto-mode/playbooks/hillclimb.md) | **持续爬山优化**：以科学实验方式持续推进某项单一关键指标直至达标。 |
| [runtime forensics](./skills/poteto-mode/playbooks/runtime-forensics.md) | **运行时取证**：利用日志和埋点诊断线上实时症状（内存泄漏、CPU 空转）。 |
| [trace forensics](./skills/poteto-mode/playbooks/trace-forensics.md) | **Profile 链路取证**：分析捕获的性能剖析产物（cpuprofile、trace 等）。 |
| [feature](./skills/poteto-mode/playbooks/feature.md) | **新功能交付**：从核心数据结构定义出发，推演实现与验证。 |
| [refactoring](./skills/poteto-mode/playbooks/refactoring.md) | **保语义重构**：保持外部行为严格不变的前提下优化代码形态。 |
| [prototype](./skills/poteto-mode/playbooks/prototype.md) | **探索性原型**：构建可抛弃的草稿实现，用于通过实际运行消除技术分歧。 |
| [visual parity](./skills/poteto-mode/playbooks/visual-parity.md) | **视觉与 UI 像素级对齐**：验证两套 UI 实现之间的像素级一致性。 |
| [authoring a skill](./skills/poteto-mode/playbooks/authoring-a-skill.md) | **技能编写规范**：遵循标准 YAML 与 Markdown 契约编写或修订 `SKILL.md`。 |
| [eval](./skills/poteto-mode/playbooks/eval.md) | **盲测 A/B 评估**：科学评测特定提示词或技能对智能体行为的实际影响。 |
| [babysit](./skills/poteto-mode/playbooks/babysit.md) | **PR 全流程托管**：持续跟进 PR 直至达到合入状态（处理冲突、评审意见、CI）。 |
| [shipping](./skills/poteto-mode/playbooks/shipping.md) | **发版验收与发布**：独立验证绿灯分支，自底向上平稳合入主干。 |
| [autonomous run](./skills/poteto-mode/playbooks/autonomous-run.md) | **长程自主运行**：驱动复杂多阶段任务不中断地推进至终态。 |
| [orchestrate](./skills/poteto-mode/playbooks/orchestrate.md) | **多智能体舰队协调**：跨多天、跨子系统的多智能体协同编排。 |
| [autopilot-full](./skills/poteto-mode/playbooks/autopilot-full.md) | **多 PR 全自动合入**：并行推动多个独立 PR 合入，每 PR 单独认领。 |
| [autopilot-stack](./skills/poteto-mode/playbooks/autopilot-stack.md) | **线性堆叠 PR 推进**：构建并验证单条线性的分支堆叠链。 |
| [session pickup](./skills/poteto-mode/playbooks/session-pickup.md) | **会话状态接管**：无缝接续前一个智能体或人类遗留的半程工作。 |
| [pause safely](./skills/poteto-mode/playbooks/pause-safely.md) | **安全挂起**：建立持久化检查点，干净利落地暂停当前工作流。 |
| [multi-phase plan](./skills/poteto-mode/playbooks/multi-phase-plan.md) | **跨阶段复杂规划**：管理跨阶段、跨版本的大型工程演进。 |
| [worktree cleanup](./skills/poteto-mode/playbooks/worktree-cleanup.md) | **Git Worktree 磁盘清理**：回收已合并或废弃的 git 工作树磁盘空间。 |
| [opening a pr](./skills/poteto-mode/playbooks/opening-a-pr.md) | **规范化提 PR**：生成标准 Conventional Commit 标题、结构化简报与验证证据。 |

---

## 23 个核心工程原则 (Principles)

- **核心素养 (Core Posture)**：`laziness-protocol`, `foundational-thinking`, `redesign-from-first-principles`, `attack-the-premise`, `subtract-before-you-add`, `minimize-reader-load`, `outcome-oriented-execution`, `experience-first`, `exhaust-the-design-space`, `build-the-lever`
- **架构与类型纪律 (Architecture & Domain)**：`model-the-domain`, `boundary-discipline`, `type-system-discipline`, `make-operations-idempotent`, `migrate-callers-then-delete-legacy-apis`, `separate-before-serializing-shared-state`
- **验证与质量原则 (Verification & Quality)**：`prove-it-works`, `fix-root-causes`, `sequence-verifiable-units`, `test-behavior-not-implementation`
- **智能体元策略 (Delegation & Meta)**：`guard-the-context-window`, `never-block-on-the-human`, `encode-lessons-in-structure`

---

## 在当前仓库中安装与生效

### 方式 1：在本仓库直接使用（已就绪）
本仓库已在 `.agents/skills.json` 与 `.agents/plugins.json` 完成注册。在 Google Antigravity 或 DeepSeek Harness 中打开本工程，所有 pstack 技能即处于可直接调用状态。

### 方式 2：拷贝至你的独立工程
将本仓库的 `pstack/` 目录拷贝至你工程的 `.agents/skills/pstack` 或 `.agents/plugins/pstack` 即可生效。

---

## 许可证

本项目遵循 MIT 开源许可证。
