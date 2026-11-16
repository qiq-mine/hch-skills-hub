---
name: steamline
description: "AI 长期项目护航套件 — 从选型到发布的全生命周期工程实践。面向独立开发者和小团队，用 AI 长期开发复杂项目时，解决选型草率、方案看不懂、测试拖开发、疑难修不动、发版出事故等问题。底层按需调用 pstack 的工程纪律能力，用户不需要了解 pstack。Triggers: steamline, /steamline, 长期项目, 项目护航, AI开发管理, 选型调研, 方案确认, 分层测试, 止损, 发布流程, 安全模式."
---

# steamline — AI 长期项目护航套件

> 用 AI 长期开发复杂项目，不失控。

steamline 是一个 Antigravity 插件，把「一个人 + AI 开发复杂项目」的全生命周期组织成 8 个按需调用的技能。每个技能解决一个具体阶段的问题，按需调用 pstack 的底层能力，用户不需要了解 pstack 的内部结构。

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

## 8 个技能速查

| 技能 | 触发场景 | 做什么 |
|------|---------|--------|
| [`tech-recon`](./skills/tech-recon/SKILL.md) | "帮我调研技术方案"、新项目启动前 | 调研开源项目、框架、协议，评估 AI 对语言的掌握度，输出选型建议 |
| [`readable-proposal`](./skills/readable-proposal/SKILL.md) | "写个方案让我确认"、"方案给产品看" | 写出让确认者能看懂的方案，交叉审查后交人确认 |
| [`delegate-execute`](./skills/delegate-execute/SKILL.md) | 方案确认后开始编码 | 沟通模型拆任务 → 执行模型编码 → 审查模型检查，保持主对话干净 |
| [`layered-testing`](./skills/layered-testing/SKILL.md) | "测试太慢了"、"怎么安排测试" | 局部改动跑局部测试，完成后重型回归；反复调试路径封装成工具 |
| [`project-governance`](./skills/project-governance/SKILL.md) | 功能越多效果越差、样式不一致 | 高频错误变规则，交互规范集中维护，文档与代码定期对照巡检 |
| [`cut-losses`](./skills/cut-losses/SKILL.md) | "这个 bug 修不好"、连续几轮失败 | 两个强模型分别排查报置信度，人决定继续修、换方案还是砍功能 |
| [`release-gate`](./skills/release-gate/SKILL.md) | "准备发版"、设置发布流程 | 发布条件程序化（测试不过不准推送），保留回滚配置 |
| [`safe-mode`](./skills/safe-mode/SKILL.md) | 桌面/移动端项目、崩溃恢复设计 | 设计最底层恢复入口：程序崩溃时仍能告知用户解决方案 |

---

## 与 pstack 的关系

```
steamline（项目驾驭层 — 面向人）
  "什么时候该做什么，怎么组织 AI 的工作"
       │
       │ 按需自动调用
       ▼
pstack（智能体纪律层 — 面向 AI）
  "代码怎么写、怎么审查、怎么验证"
```

- **steamline 可以独立使用**：不装 pstack 也能跑，只是审查和验证环节会用更通用的方式。
- **装了 pstack 更强**：steamline 的 `delegate-execute` 会自动调用 `interrogate` 做交叉审查，`layered-testing` 会调用 `prove-it-works` 做验证，`readable-proposal` 会调用 `architect` 做技术设计。
- **用户不需要知道 pstack**：所有调用都在技能内部完成，用户只需要跟 steamline 的技能交互。

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

## 安装

steamline 是一个 Antigravity 插件，通过 `plugin.json` 声明规则、技能和智能体。

在项目的 `.agents/plugins.json` 中加载：
```json
{
  "entries": [
    { "path": "steamline" }
  ]
}
```

如果同时使用 pstack（推荐）：
```json
{
  "entries": [
    { "path": "steamline" },
    { "path": "pstack" }
  ]
}
```

### 插件结构

```
steamline/
├── plugin.json          ← 插件声明（名称、版本、入口）
├── SKILL.md             ← 主入口文档
├── rules/
│   └── AGENTS.md        ← 始终生效的项目约束（自动加载）
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
    └── steamline-agent.md  ← 主路由智能体
```

- `rules/` 下的规则**始终生效**，不需要手动触发
- `skills/` 下的技能**按需调用**，由用户输入或智能体路由触发
- `agents/` 下的智能体定义可被 Antigravity 作为子智能体调用
