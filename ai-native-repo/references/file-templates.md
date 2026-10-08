# File Templates (AI Native Repo)

## AGENTS.md

```markdown
---
owner: <团队名>
status: active
last-verified: 2026-10-08
standard-version: "0.1"
---

# <repo 一句话>

## 项目快照
<3-5 行：做什么、给谁用、技术栈>

## 一键命令
- 启动：`task setup && task dev`
- 验证：`task test && task lint`

## 通用约定
<5-10 行：分支策略、提交格式、PR 要求>

## 安全红线
<3-5 行：密钥走环境变量；危险操作列表>

## 索引（JIT：只给路径，不贴内容）
- 架构：`docs/architecture.md`
- 接口契约：`spec/`
- 变更提案：`changes/`（进行中）/ `changes/archive/`（已完成）
```

## harness.yaml

```yaml
version: "0.1"
skills:
  - name: <skill 名>
    path: skills/<name>/SKILL.md
    triggers: ["<何时触发，如 before-deploy>"]
hooks:
  - event: pre-commit
    run: task lint
gates:
  blocking: [tests, spec-validate, secret-scan]   # 不过不让合
  garden: [doc-freshness, eval-drift]              # 只开 issue，不拦人
permissions:
  read: ["**"]
  write: ["src/**", "docs/**", "spec/**"]
  deny: [".env", "**/*.pem", "infra/prod/**"]
```

- `spec-validate`：校验 `spec/` 契约与 CodeSpec 的一致性（由 SDD CLI 提供）。
- 换工具演练标准：新工具只读 `harness.yaml` + `AGENTS.md`，能独立走完一次
  `changes/` 提案流程，即通过。

## skills/\<name\>/SKILL.md

```markdown
---
name: <skill 名>
triggers: ["<触发条件>"]
version: "0.1"
---

# <做什么>

## 前置条件
## 步骤
1. ...
## 验收标准
- [ ] ...
## 反模式（别这么干）
```

沉淀时机：同一操作重复 3 次即抽成 skill。

## changes/\<verb-slug\>/

`proposal.md`:
```markdown
# <标题>
- 为什么改（一句话，写具体失败而非愿景）：
- 范围：做 / 不做：
- 方案与被否决的备选：
```

`spec-delta.md`（delta 表达，不直接改原 spec）:
```markdown
## MODIFIED Requirements
### Requirement: <名称>
#### Scenario: <至少一个场景>
```

`tasks.md`:
```markdown
- [ ] T1 <任务>（验收：...）
```

流程：propose → 人评审 → apply（按 tasks.md 顺序实现）→ archive
（`changes/archive/YYYY-MM-DD-<id>/`，delta 合回 `spec/`）。

## CodeSpec (`*.codespec.yaml`)

```yaml
api: <模块/接口名>
version: "0.1"
preconditions: ["<前置>"]
postconditions: ["<后置>"]
invariants: ["<不变量>"]
acceptance:
  - name: <用例名>
    given: <输入>
    then: <断言>
```

规则：实现不得改契约；契约要改，回流到 CodeSpec + 人确认。

## rules/agent-permissions.md

```markdown
# Agent 权限声明（唯一真相源，子目录不得放宽）

- 可读：`read`（见 harness.yaml）
- 可写：`write`（见 harness.yaml）
- 禁区：`deny`（见 harness.yaml）
- 危险操作（删数据/动生产/动硬件）：必须走 PR + @<reviewer>
```
