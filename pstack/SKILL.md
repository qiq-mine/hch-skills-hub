---
name: pstack
description: "pstack 严谨软件工程技能套件（深度适配 Antigravity / DSH / Claude Code）。包含 23 个工程原则 (principles)、23 个任务剧本 (playbooks)、模型分工调度 (setup-pstack / poteto-mode)、架构设计 (architect)、多模型对抗审查 (interrogate / arena / swarm)、代码去水 (unslop / no-comments) 及独立验证体系。当用户需要高质量代码交付、严谨排错、多模型协作或自动化开发流时使用。Triggers: pstack, poteto-mode, /setup-pstack, 严谨工程, 对抗审查, 架构设计, unslop, fearless parallelism."
---

# pstack — 严谨工程与多智能体协作技能套件

> 原作：Lauren Tan ([@poteto](https://x.com/poteto)) | 适配：Google Antigravity & DeepSeek Harness (DSH)

pstack 是一套经过工业级验证的 AI 智能体软件工程范式。其核心理念是 **"Go deep first"** —— 拒绝堆砌毫无验证的代码（AI Slop），通过结构化剧本、多模型角色分工、独立验证和工程原则，将 AI 编程智能体打造成一支纪律严密的资深研发团队。

---

## 核心能力一览

```
                                      ┌── [架构与探索] architect / how / why
                                      ├── [多模型对抗] interrogate / arena / swarm
用户目标 ──▶ /poteto-mode ──▶ 匹配 23 个剧本 ──┼── [实现与驱动] tdd / feature / bug-fix
                                      ├── [代码去水] unslop / no-comments
                                      └── [独立验证] prove-it-works / create-verification-skill
```

### 1. 核心入口
- **[`poteto-mode`](./skills/poteto-mode/SKILL.md)**：严谨工程的主入口。自动将任务匹配到 23 个标准研发剧本，并在各阶段调度对应专业技能与子智能体。
- **[`setup-pstack`](./skills/setup-pstack/SKILL.md)**：智能体模型与推理预算配置。检测当前环境可用模型，并生成工程角色映射规则。

### 2. 核心工作流技能
- **[`architect`](./skills/architect/SKILL.md)**：跨函数/模块边界的系统设计，先定数据结构与契约接口，再编写实现。
- **[`arena`](./skills/arena/SKILL.md)**：多方案竞技场。并发生成 N 个独立候选方案，由独立裁判评估，融合最佳构件。
- **[`swarm`](./skills/swarm/SKILL.md)**：蜂群并行。并行分发覆盖矩阵、竞速方案或子切片，汇总为单份严密报告。
- **[`interrogate`](./skills/interrogate/SKILL.md)**：多模型对抗审查。多角度交叉审查变更，杜绝盲点。
- **[`how`](./skills/how/SKILL.md)**：子系统架构与运行时数据流探索。
- **[`why`](./skills/why/SKILL.md)**：历史决策与深层动机归因（检索代码仓库、提交历史、文档与观测系统）。
- **[`unslop`](./skills/unslop/SKILL.md)**：去除 AI 常见废话套话与模式化句式，保证技术文档与代码精简严密。
- **[`no-comments`](./skills/no-comments/SKILL.md)**：剔除多余过程注释与自辩代码，驱动代码本身表达意图。
- **[`show-me-your-work`](./skills/show-me-your-work/SKILL.md)**：生成并维护可审计的决策链路表（`decisions.tsv`）。
- **[`tdd`](./skills/tdd/SKILL.md)**：测试驱动开发，先写失败用例，再写最小通过实现。
- **[`create-verification-skill`](./skills/create-verification-skill/SKILL.md)**：为项目自动生成专属的行为级验证技能与功能地图。

### 3. 23 个工程原则 (Principles)
位于 [`skills/`](./skills/) 目录下，包含：
- **核心原则**：`laziness-protocol`（懒惰协议/优先做减法）、`foundational-thinking`（基础数据结构优先）、`redesign-from-first-principles`（第一性原理重构）、`attack-the-premise`（攻击前提假设）、`subtract-before-you-add`（先减后加）、`minimize-reader-load`（最小化读者认知负荷）、`build-the-lever`（构建工具杠杆）等。
- **架构原则**：`model-the-domain`（领域建模结构化）、`boundary-discipline`（边界防御纪律）、`type-system-discipline`（类型系统严谨性）、`make-operations-idempotent`（操作幂等性）等。
- **验证原则**：`prove-it-works`（运行时真实验证）、`fix-root-causes`（追溯根本原因修复）、`sequence-verifiable-units`（步骤原子化验证）、`test-behavior-not-implementation`（测试行为而非实现细节）。

---

## 运行环境适配 (Antigravity & DSH)

本版本已彻底移除 Cursor 专有依赖（`.cursor` 目录绑定、`Task` 私有参数、`/loop` 命令依赖等），原生支持 **Google Antigravity** 与 **DeepSeek Harness (DSH)**：

| 机制 | Cursor 原生 | Antigravity 适配 | DeepSeek Harness (DSH) 适配 |
|------|------------|-----------------|-----------------------------|
| **子智能体调度** | `Task(subagent_type: ...)` | `invoke_subagent` (TypeName: self/research) | DSH Subagent Runner / Task Plugin |
| **高难度判断模型** | `claude-fable-5-1-thinking-max` | `Model: "pro"` (高推理深度) | `deepseek-reasoner` (R1 思考模型) |
| **快速机械执行模型**| `grok-4.6-fast-xhigh` | `Model: "flash"` (超快响应) | `deepseek-chat` (V3 高性能编码) |
| **交互式提问** | `AskQuestion` | `ask_question` (结构化单/多选) | 终端交互提示或控制台交互 |
| **配置规则存储** | `~/.cursor/rules/pstack-models.mdc` | `.agents/rules/pstack-models.md` 或 `GEMINI.md` | `.dsh/rules/` 或 `AGENTS.md` |
| **会话轨迹审查** | `~/.cursor/projects/...` | `<appDataDir>/brain/<id>/.../transcript.jsonl` | DSH 会话工作目录下的会话记录 |
| **自主循环运行** | `/loop` 专有命令 | `/goal` 命令 / `schedule` 调度器工具 | DSH 守护循环模式 |

---

## 快速使用

### 方式一：直接调用对应技能
- 进入严谨开发模式：`/poteto-mode [你的任务描述]`
- 配置当前模型分配：`/setup-pstack`
- 跨边界架构设计：`/architect [待设计的模块]`
- 开展代码对抗审查：`/interrogate [分支或 diff]`

### 方式二：作为 Antigravity 插件加载
在项目的 `.agents/plugins.json` 或本技能库根目录下直接作为插件载入：
```json
{
  "entries": [
    { "path": "pstack" }
  ]
}
```

---

## 目录索引

- [全部 47 个子技能目录](./skills/)
- [23 个研发剧本目录](./skills/poteto-mode/playbooks/)
- [完整官方指南](./docs/guide/README.md)
- [Antigravity/DSH 规则注入文件](./rules/AGENTS.md)
