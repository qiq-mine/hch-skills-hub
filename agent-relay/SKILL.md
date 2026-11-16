---
name: agent-relay
description: "一句话把边界清楚的任务委托给 Claude Code（cc）、WorkBuddy（wb）、Antigravity（agy）、Codex、OpenCode、DeepSeek Harness（dsh）、Grok Build（grok）或 Kimi Code（kimi）CLI，返回结构化结果并续接原会话；支持静默扫描、启用执行器与默认选择，并可按用途（代码审查、方案挑刺、疑难会诊、工程实现）记住各角色分工。用户要求 agent-relay、跨 Agent 委托、统一调用或调用上述外部 CLI Agent 时使用；不用于普通直接问答或显式 /codex。"
license: MIT
metadata:
  version: "1.0.0"
---

# agent-relay

`SKILL_DIR` 指当前 Skill 的绝对目录；`<python>` 指 Python 3.10+（macOS/Linux 通常为 `python3`，Windows 通常为 `py -3`）；`RELAY` 是 `<python> "$SKILL_DIR"/scripts/relay.py` 的简写（兼容 `delegate.py`）。

## 核心规则

- 用户只说自然语言，由当前宿主 Agent 执行包装器，不要求用户另开终端。
- 每次只委托一个边界清楚的任务；用户点名的 runner 优先，按角色委托时用该角色保存的选择，其余情况使用默认值，不擅自换 runner。
- 沿用各 CLI 的模型、provider 与本地登录缓存，不传递或保存密钥，不把密钥写入提示词。
- 调用方负责范围、权限和最终验收；外部 Agent 的自报结果不能替代工作区真实检查与测试。

## 运行模式

| 模式 | 适用情况 | 路径 | 默认停止点 |
| --- | --- | --- | --- |
| 首次 Onboarding | 未指定 `--runner` 且 `run` 返回 `NEEDS_ONBOARDING`，或用户要求重配 | 静默扫描 → 用户确认启用池与默认项 → 保存 | 已有任务继续执行；仅重配时结束 |
| 新任务 | 把一次分析、评审或修改交给外部 Agent | 整理委托契约 → `run` → 读取结果并验收 | 汇报结论与验证证据 |
| 续接任务 | 对同一 CLI 的上一轮结果追问或返工 | 核对 runner 与 session ID → `run --session` | 汇报本轮变化 |
| 按角色委托 | 配合 `steamline` 或 `pstack` 委托审查、方案挑刺、会诊或实现 | `run --role` → 按返回状态处理 | 汇报结论与验证证据 |
| 配置与诊断 | 查看环境、预览权限或处理失败 | `onboard --scan`、`config`、`run --dry-run` | 给出明确下一步 |

## 委托契约

提示词应简洁覆盖：

1. **目标与边界**：要查明或修改什么，明确不应改动的范围。
2. **完成标准**：预期行为、边界情况、最终必须交付的结果。
3. **入口线索**：用 `--file` 提供 1–4 个已确认文件，其余让外部 Agent 自行探索。
4. **验证**：从仓库配置确认真实测试、检查或构建命令，不写空泛的“运行测试”。
5. **最终报告**：改动与原因、涉及文件、验证命令和结果、未完成事项。

缺少仓库事实先查找，不猜测。诊断与评审要求引用文件和行号，并区分事实与推断。

## 工作流

### 1. Onboarding 与 runner 选择

未完成 onboarding 时，显式传入 `--runner <已安装名称或别名>` 会直接执行该 CLI（不写 `config.json`、不阻塞在首次引导）；只有省略 `--runner` 的首次默认委托才会返回 `NEEDS_ONBOARDING`。已完成 onboarding 后，显式点名未启用的 runner 会报错拒绝，不会静默替换。

收到 `NEEDS_ONBOARDING` 或用户要求配置启用池与默认项时：

1. 首次省略 `--runner` 的 `run` 已自动完成静默扫描并返回 detected/installed runners，无需用户执行任何命令。需要刷新时运行 `RELAY onboard --scan`。扫描不写配置、不读取凭据、不调用模型、不安装、不登录。
2. 展示已安装 runner、版本、来源、能力和 aliases，说明“已安装不等于已认证”。首次配置前读 [Runner 适配参考](references/runners.md)，讲清 read/write 权限差异、外部服务费用与任务文本会交给对应 provider。
3. 询问启用哪些 runner，以及默认使用一个还是每次询问。得到回答后才保存：
   ```text
   RELAY onboard --enable <claude,workbuddy,antigravity,codex,opencode,dsh,grok,kimi> --default-runner <runner|ask>
   ```

名称不区分大小写，启用、默认项、委托和二进制路径配置都走同一套别名解析，保存时统一转为正式 Runner 名；完整映射见 [Runner 适配参考](references/runners.md)。

本次已有待执行任务时，保存后返回步骤 2 继续，不要求用户重发；只有用户只是重配时才停止。

未指定 runner 且没有默认值时，`run` 返回 `NEEDS_RUNNER_CHOICE`。询问本次选择；只有用户同意沉淀偏好时，才运行 `RELAY config --set-default-runner <runner>`。

查看配置或指定非标准二进制路径：

```text
RELAY config
RELAY config --set-bin <runner>=<可执行文件绝对路径>
```

### 2. 派发新任务

- 默认省略 `--mode`，使用 `write` 和各 CLI 的最高权限；分析、探索和评审也不自动降级。
- 只有用户明确要求只读、plan 或限制权限时才使用 `--mode read`；按读类角色委托时由角色自动只读。Kimi 的非交互模式自带 auto 权限，不能保证只读，因此拒绝 read，不伪装支持。
- 默认使用当前工作目录，跨项目时显式指定 `--workspace`。
- 调用：

```text
RELAY run --runner <名称> \
  --workspace "<项目绝对路径>" \
  --file "<相对入口文件>" \
  --prompt "<目标、边界、完成标准与真实验证命令>"
```

已配置默认 runner 时省略 `--runner`。启动前需要核对参数时追加 `--dry-run`；预览不会启动外部 Agent。

### 按角色委托

配合 `steamline`（`readable-proposal`、`delegate-execute`、`cut-losses`）或 `pstack`（`interrogate`、`architect`）等工作流按用途委托时使用 `--role`，由用户保存的偏好决定交给谁：

| 角色 | 用途 | 权限 | 契合工作流 |
| --- | --- | --- | --- |
| `review` | 独立代码审查 | 只读 | `steamline` 审查 / `pstack interrogate` |
| `critique` | 方案挑刺与边界把关 | 只读 | `steamline readable-proposal` / `pstack reflect` |
| `diagnose` | 疑难问题双模型会诊（保存两不同选择，分别调 slot 1 和 slot 2） | 只读 | `steamline cut-losses` / `pstack attack-the-premise` |
| `implement` | 按已确认方案实现 | 写入 | `steamline delegate-execute` / `pstack feature` |

```text
RELAY run --role review --workspace "<项目绝对路径>" --prompt "<审查范围与要求>"
```

- 读类角色自动只读，不要再传 `--mode`；Kimi 不能保证只读，不能配给读类角色。
- 返回 `NEEDS_ROLE_CHOICE`（退出码 12）：该角色尚未绑定。展示 `candidates` 并询问用户一次（`host` 表示由当前宿主 Agent 开设全新子 Agent）。用户希望记住时保存 `RELAY config --set-role review=<选择>`（`diagnose` 写两个，逗号分隔）；仅本次使用则改传 `--runner`。
- 返回 `USE_HOST`（退出码 13）：用户偏好由宿主 Agent 自己完成。改用宿主的全新子 Agent 执行，不调用外部 CLI。
- 显式传 `--runner` 时以它为准，权限仍由角色决定。
- 用户指定类似“以后 review 都用 codex”时，直接用 `config --set-role` 保存；`--set-role review=ask` 可清除。`review` 或 `critique` 与 `implement` 选了同一 runner 时，配置会输出 `warnings`，建议用户使用不同模型保证对抗独立性。
- 角色偏好保存在 agent-relay 的状态目录（`~/.agent-relay/config.json`），不污染项目文件。

### 3. 续接原会话

读取上一轮输出的 `session_id`，只对同一 runner 续接：

```text
RELAY run --runner <原 runner> \
  --workspace "<原工作区>" \
  --mode <read|write> \
  --session <session_id> \
  --prompt "<本轮新发现、追问或修正要求>"
```

续接只发送本轮增量信息，不重复整个任务背景。跨 runner 不能复用 session ID；需要第二意见时开启新任务并补充必要上下文。DSH 续接必须使用原 cwd。

### 4. 验收与失败恢复

1. 读取 `output_path` 的摘要；需要退出码、session ID 或错误结构时读取 `result_path`，协议诊断读取 `events_path`。
2. 检查工作区改动是否越界，检查测试是否被篡改或弱化，重新运行真实测试套件。
3. 需要返工时续接原会话，只发送新发现和修正要求。
4. 非零退出、协议错误或超时后不盲目重试。先根据错误修正配置、登录状态、任务范围或权限。
5. 缺少 CLI 或登录时停止并给出官方入口；安装与登录必须另行获得用户授权。

## 输出与结构化契约

成功后脚本输出 `status`、`session_id`、`runner`、`output_path`、`result_path`、`events_path` 和 `elapsed`。每次运行拥有独立目录，包含 prompt、精简 Markdown、结构化 result、原始 stdout/stderr 与事件日志。result 里的 `resume_command` 是用户在终端直接续接该会话的命令。

给程序或父智能体调用时追加 `--json`：stdout 只输出单一 JSON 对象（包含 `contract_version: 1`），保证机器解析可靠。

最终向用户汇报时只保留结论、实际改动、验证证据、未完成事项和必要 session ID。

## 资源导航

- [references/runners.md](references/runners.md)：各 CLI 启动参数、权限机制、续接命令与官方参考文档。
- [scripts/relay.py](scripts/relay.py)：扫描、配置、调用、解析与产物管理的确定性 Python 工具。
- [tests/test_delegate.py](tests/test_delegate.py)：八种 Runner 的完整自动化回归测试套件。
