---
name: streamline
description: "AI 长期项目护航套件 — 从选型到发布的全生命周期工程实践。面向独立开发者和小团队，用 AI 长期开发复杂项目时，解决选型草率、方案看不懂、测试拖开发、疑难修不动、发版出事故等问题。底层按需调用 pstack 的工程纪律能力，用户不需要了解 pstack。本文件是套件总览与路由表；具体阶段由各子技能处理。Triggers: streamline, /streamline, 长期项目, 项目护航, AI开发管理, 项目阶段怎么走."
---

# streamline — AI 长期项目护航套件

> 用 AI 长期开发复杂项目，不失控。

streamline 是一个面向 AI 长期项目研发的工程护航套件（深度支持 **Antigravity** 与 **Cursor**）。把「一个人 + AI 开发复杂项目」的全生命周期组织成 8 个按需调用的技能。每个技能解决一个具体阶段的问题，按需调用 pstack 的底层能力，用户不需要了解 pstack 的内部结构。

---

## 运行环境机制对照

| 机制维度 | Antigravity 运行机制 | Cursor 运行机制 |
|---|---|---|
| **常驻规则加载** | `.agents/rules/` 或 `rules/AGENTS.md` | `.cursor/rules/streamline.mdc` (`alwaysApply: true`) |
| **技能调用发现** | 插件自动注册或 `invoke_subagent` 调度 | `.cursor/skills/` 目录或 `@streamline` 显式引用 |
| **分工执行 (`delegate-execute`)** | 主对话拆解 + `invoke_subagent` 派发执行/审查子智能体 | 主会话拆解 + 新建独立 Composer 标签页执行编码 + 强推理模型审查 |
| **疑难止损 (`cut-losses`)** | `swarm` 多模型并发或子智能体分别排查 | 双 Chat/Composer 标签页 + 切换两大家族模型独立排查 |
| **项目规则沉淀** | 写入 `AGENTS.md` 或 `.agents/rules/` | 写入 `.cursor/rules/*.mdc` |

---

## 项目生命周期与技能对照

```
 开工前                    开发中                      收尾
┌──────────┐  ┌──────────────────────────────┐  ┌──────────────┐
│ 选型调研  │  │ 分工执行 → 分层测试 → 规则治理 │  │ 发布 → 回滚  │
│ 方案确认  │  │         ↕ 疑难止损            │  │   安全模式   │
└──────────┘  └──────────────────────────────┘  └──────────────┘
 tech-recon    delegate-execute                  release-gate
 readable-     layered-testing                   safe-mode
 proposal      project-governance
               cut-losses
```

---

## 8 个技能速查（唯一路由表）

`streamline-agent` 也按这张表路由。改触发场景只改这里和对应子技能的 frontmatter。

| 技能 | 触发场景 | 做什么 |
|------|---------|--------|
| [`tech-recon`](./skills/tech-recon/SKILL.md) | "帮我调研技术方案"、新项目启动前 | 调研开源项目、框架、协议，评估 AI 对语言的掌握度，输出选型建议 |
| [`readable-proposal`](./skills/readable-proposal/SKILL.md) | "写个方案让我确认"、"方案给产品看" | 写出让确认者能看懂的方案，交叉审查后交人确认 |
| [`delegate-execute`](./skills/delegate-execute/SKILL.md) | 方案确认后开始编码 | 沟通模型拆任务 → 执行模型编码 → 审查模型检查，保持主对话干净 |
| [`layered-testing`](./skills/layered-testing/SKILL.md) | "测试太慢了"、"怎么安排测试" | 局部改动跑局部测试，完成后重型回归；反复调试路径封装成工具 |
| [`project-governance`](./skills/project-governance/SKILL.md) | 功能越多效果越差、样式不一致 | 高频错误变规则，交互规范集中维护，文档与代码定期对照巡检 |
| [`cut-losses`](./skills/cut-losses/SKILL.md) | "这个 bug 修不好"、连续几轮失败 | 两个不同模型分别排查并给出可验证证据，人决定继续修、换方案还是砍功能 |
| [`release-gate`](./skills/release-gate/SKILL.md) | "准备发版"、设置发布流程 | 发布条件程序化（测试不过不准推送），保留回滚配置 |
| [`safe-mode`](./skills/safe-mode/SKILL.md) | 桌面/移动端项目、崩溃恢复设计 | 设计最底层恢复入口：程序崩溃时仍能告知用户解决方案 |

---

## 与 pstack 的关系

```
streamline（项目驾驭层 — 面向人）
  "什么时候该做什么，怎么组织 AI 的工作"
       │
       │ 可用时读取并遵循
       ▼
pstack（智能体纪律层 — 面向 AI）
  "代码怎么写、怎么审查、怎么验证"
```

- **streamline 可以独立使用**：不装 pstack 也能跑，只是审查和验证环节会用更通用的方式。
- **装了 pstack 更强**：技能不能自动触发别的技能，所以各子技能的「pstack 联动」写明了该读哪个 pstack 技能的 `SKILL.md` 并按它执行。例如 `delegate-execute` 审查时按 `interrogate` 执行，`layered-testing` 收尾时按 `principle-prove-it-works` 验证，`readable-proposal` 设计时按 `architect` 执行。
- **判断 pstack 是否可用**：看当前可用技能列表里有没有 `interrogate`。有就按 pstack 技能执行，没有就用子技能里写的替代方案。
- **模型分配**：子技能只写角色（判断 / 执行），不写具体模型名。装了 pstack 时按 `setup-pstack` 的配置选模型。
- **用户不需要知道 pstack**：用户只需要跟 streamline 的技能交互。

---

## 快速使用

### 新项目启动
```
帮我调研一下用什么技术做 [项目描述]
→ 自动触发 tech-recon

调研结果确认后：
帮我写个方案，我要确认后才开始做
→ 自动触发 readable-proposal
```

### 开发过程中
```
方案确认了，开始做
→ 自动触发 delegate-execute

测试跑太慢了，怎么安排
→ 自动触发 layered-testing

最近做出来的东西越来越乱
→ 自动触发 project-governance

这个 bug 修了好几轮了还没修好
→ 自动触发 cut-losses
```

### 准备发布
```
准备发版
→ 自动触发 release-gate

客户端崩溃了用户打不开怎么办
→ 自动触发 safe-mode
```

---

## 安装与集成

### 方式一：在 Cursor 中使用

1. **注入常驻规则**：
   将 `streamline/rules/streamline.mdc` 软链或复制到项目的 `.cursor/rules/` 目录：
   ```bash
   mkdir -p .cursor/rules
   ln -s /path/to/streamline/rules/streamline.mdc .cursor/rules/streamline.mdc
   ```
   > 规则内配置了 `alwaysApply: true`，在所有 Chat 和 Composer 会话中自动注入「方案先于代码」、「干净上下文」等纪律。

2. **载入技能目录（可选，作为 Cursor Agent Skills）**：
   如果使用 Cursor 的技能扩展能力，可将 `streamline/skills/` 软链到 `.cursor/skills/`：
   ```bash
   mkdir -p .cursor/skills
   ln -s /path/to/streamline/skills/* .cursor/skills/
   ```
   也可以直接在对话中通过 `@streamline` 或技能文件名引用。

### 方式二：在 Antigravity 中使用（插件模式）

streamline 是一个 Antigravity 插件，通过 `plugin.json` 声明规则、技能和智能体。

在项目的 `.agents/plugins.json` 中加载：
```json
{
  "entries": [
    { "path": "streamline" }
  ]
}
```

如果同时使用 pstack（推荐）：
```json
{
  "entries": [
    { "path": "streamline" },
    { "path": "pstack" }
  ]
}
```

### 目录结构

```
streamline/
├── plugin.json          ← Antigravity 插件声明（名称、版本、入口）
├── SKILL.md             ← 主入口文档 + 唯一路由表
├── README.md            ← 简介与安装
├── CHANGELOG.md         ← 版本记录
├── LICENSE
├── rules/
│   ├── AGENTS.md        ← Antigravity 始终生效的项目约束（自动加载）
│   └── streamline.mdc   ← Cursor 始终生效的项目约束（alwaysApply: true）
├── skills/              ← 8 个按需调用的技能
│   ├── tech-recon/
│   ├── readable-proposal/
│   ├── delegate-execute/
│   ├── layered-testing/
│   ├── project-governance/
│   ├── cut-losses/
│   ├── release-gate/
│   └── safe-mode/
└── agents/
    └── streamline-agent.md  ← 主路由智能体
```

- `rules/` 下的规则**始终生效**，不需要手动触发
- `skills/` 下的技能**按需调用**，由用户输入或智能体路由触发
- `agents/` 下的智能体定义可被 Antigravity 作为子智能体调用
