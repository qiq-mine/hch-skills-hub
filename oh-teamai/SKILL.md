---
name: oh-teamai
description: >
  团队级 AI 资产中台与配置同步治理技能（基于腾讯开源 TeamAI）。
  负责统一团队内部所有成员的 AI 智能体配置：Skills、Rules、Prompt、MCP 配置与环境上下文，
  支持在 16+ 款 AI 编程工具（Claude Code, Cursor, Windsurf, Antigravity, Roo Code, Copilot 等）间无缝分发与同步。
  支持团队从零初始化 AI 知识仓库、成员加入与拉取更新、通过 PR/MR 审核共享新技能，
  以及大型多代码库架构逆向沉淀（Team Wiki）与会话经验回流（Session Learning Share）。
  当用户提到 "teamai", "oh-teamai", "团队技能同步", "团队AI配置", "多工具AI同步", "团队AI仓库", "沉淀团队经验" 时触发。
metadata:
  version: 1.0.0
  source: "https://github.com/Tencent/teamai-cli"
---

# oh-teamai: 团队级 AI 资产中台与配置协同治理

个人的 AI 习惯散落在每个工程师的笔记本里（不同的 `.cursorrules`、不同的 MCP 配置、各写各的 Prompt）。**TeamAI** 的核心使命是将“个人的 AI 能力”转化为“团队共享的组织级资产”，让团队所有成员的智能体按组织约定的标准协同工作。

---

## 一、核心工作流路由 (Workflow Routing)

当用户输入 `/teamai` 或调用本技能时，先判断用户诉求，并引导执行标准流程：

```
                    ┌─────────────────────────┐
                    │  用户输入 /teamai 诉求   │
                    └────────────┬────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
【场景 A: 团队初始化】    【场景 B: 日常协作同步】    【场景 C: 知识与经验沉淀】
  创建全新团队仓库          `teamai pull` / `push`     Wiki 逆向工程 / 会话反哺
  统一规范与成员邀请        健康检查 `teamai doctor`   `teamai share` 提交 MR
```

---

## 二、场景指南与命令速查

### 场景 A：从零创建团队 AI 资产库 (Admin Day-0)
适合企业架构师或 Tech Lead 统一规范。
1. **安装环境**：
   ```bash
   npm i -g teamai-cli@latest
   ```
2. **初始化团队仓库**：
   ```bash
   # 在远端 Git（GitHub / GitLab / Coding / Gitee）创建一个空的私有仓库，例如：
   # https://git.company.com/architecture/team-ai-hub.git
   teamai init
   ```
3. **纳入团队基准规则**：
   * 将通用的工程规范（如 `pstack` 原则、代码规范、`AGENTS.md`）放入仓库。
   * 配置全局 MCP 推荐清单（如数据库查库工具、API 检索工具）。

### 场景 B：新成员加入与日常拉取 (Member Day-1)
新员工或团队成员一键同步组织级 AI 装备：
```bash
# 1. 首次加入团队
teamai join https://git.company.com/architecture/team-ai-hub.git

# 2. 每日开工：拉取团队最新的 Skills 与规则
teamai pull

# 3. 诊断当前环境是否已正确生效到本地各大 Agent 工具
teamai doctor
```

### 场景 C：贡献与共享新 Skill / 规则 (Publish & Share)
当某位成员沉淀了优秀的技能（如在本地验证有效的 Prompt 或工作流）：
```bash
# 1. 查看本地新增或改动的 AI 资产
teamai status

# 2. 推送并创建分支 / 发起 Merge Request 供架构委员会评审
teamai push -m "feat(skill): add high-precision cloud-init validation skill"
```

### 场景 D：大型多仓库架构知识库构建 (Team Wiki)
对大型微服务或复杂遗留系统进行架构逆向工程：
```bash
# 启动架构扫描分析，生成跨仓库知识图谱与 Wiki 文档
teamai wiki generate --depth 3
```

### 场景 E：会话经验回流 (Session Learning Share)
当智能体在当前会话中解决了一个疑难杂症，或纠正了某种易错点：
* 触发提示：`[teamai share]`
* 自动提炼核心经验，转写为 Markdown 规则条目，生成补丁。

---

## 三、跨客户端兼容支持 (16+ AI Agents)

TeamAI CLI 会自动将统一的团队规范分发适配至对应客户端的私有格式：

| 客户端类别 | 目标适配文件 | 同步内容 |
| :--- | :--- | :--- |
| **Cursor** | `.cursor/rules/*.mdc`, `.cursorrules` | 团队代码规则与前置上下文 |
| **Claude Code** | `CLAUDE.md`, `.claude/skills/*` | 智能体工作流与标准技能 |
| **Google Antigravity** | `.agents/skills.json`, `pstack/rules` | 技能发现索引与工程公约 |
| **Windsurf / Roo Code** | `.windsurfrules`, `.roomodes` | 模式与指令集 |
| **通用 MCP 客户端** | `mcp.json` / `claude_desktop_config.json` | 团队公共工具服务接入 |

---

## 四、团队 AI 资产评审公约 (PR/MR Review Guidelines)

所有纳入团队共享仓库的 Skill 必须满足：
1. **符合规范**：必须具备完备的 YAML Frontmatter（包含 `name`, `description`, `metadata`）。
2. **严禁硬编码敏感信息**：禁止在技能文档或脚本中包含 API Key、内部生产环境 Token 或私有 IP。
3. **验证闭环**：提供至少一个经过实测检验的输入/输出范例。
4. **幂等与无害**：自动化脚本必须支持反复重入，绝不带破坏性副作用。
