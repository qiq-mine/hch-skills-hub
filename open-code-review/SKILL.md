---
name: open-code-review
description: "阿里巴巴开源 AI 代码审查工具 suite（确定性工程 × Agent 混合驱动）。支持使用 `ocr` CLI 对 Git diff、指定 commit、分支对比或全量代码文件进行行级精准审查，支持全自动模式与委托模式（由宿主 Agent 执行审查、OCR 执行确定性规则匹配）。Triggers: open-code-review, ocr, 代码审查, code review, 审查代码, PR review."
license: Apache-2.0
compatibility: "支持 Google Antigravity, DeepSeek Harness (DSH), Claude Code, Cursor 及命令行 CLI。需安装 ocr CLI (npm install -g @alibaba-group/open-code-review 或 GitHub release)。"
metadata:
  author: alibaba
  homepage: https://github.com/alibaba/open-code-review
  version: "1.0.0"
---

# Open Code Review — 阿里开源 AI 代码审查套件

> 阿里巴巴官方开源，两年前沿实战沉淀，万级开发者验证，数百万缺陷拦截。
> 结合**确定性工程**（精准文件筛选、分包隔离、模板规则匹配）与 **LLM Agent**（动态语义决策、深度上下文召回）的下一代代码审查平台。

---

## 包含技能模式

本项目内包含两种审查技能模式，根据运行环境和使用意图选择：

| 模式 | 技能路径 | 适用场景 |
|------|---------|---------|
| **1. 完整 CLI 驱动模式** | [`skills/open-code-review/SKILL.md`](./skills/open-code-review/SKILL.md) | 在本地已安装 `ocr` 并配置好 LLM Provider（如 OpenAI、Anthropic、Bedrock）时使用。支持全自动完成差异计算、规则匹配与审查结果输出。 |
| **2. 委托模式 (Delegate)** | [`skills/open-code-review-delegate/SKILL.md`](./skills/open-code-review-delegate/SKILL.md) | **推荐智能体使用**：`ocr` 仅提供确定性工程（文件筛选、依赖分包、审查规则分发），无需在 OCR 端配置 API Key，由当前宿主 Agent（如 Antigravity、DSH）自身的大模型执行审查并输出意见。 |

---

## 快速工作流

### 模式 A：智能体委托审查（推荐）

如果当前 Agent 自带强大的模型（如 Antigravity Pro、DSH DeepSeek-Reasoner），可直接利用 OCR 的确定性规则引擎：

1. **预检需要审查的文件**：
   ```bash
   ocr delegate preview --format json
   ```
2. **获取匹配的规则**：
   ```bash
   ocr delegate rule --format json <file1> <file2> ...
   ```
3. **获取变更差异**：
   ```bash
   git diff <base>...<target> -- <file>
   ```
4. **Agent 执行审查**：
   由智能体对照 OCR 分发的规则与业务上下文，直接在当前会话中提出结构化行级改进意见。

### 模式 B：全自动 CLI 审查

在终端或自动化流水线中直接运行：

```bash
# 工作区暂存/未暂存修改审查
ocr review --audience agent -b "业务背景说明"

# 跨分支比对审查
ocr review --from main --to feature-branch --audience agent

# 单次 commit 审查
ocr review --commit abc123 --audience agent

# 全量扫描目录
ocr scan --path internal/service
```

---

## 详细文档与参考

- 完整中文文档：[README.md](./README.md)
- 英文原始文档：[README_EN.md](./README_EN.md)
- CLI 驱动技能详细说明：[skills/open-code-review/SKILL.md](./skills/open-code-review/SKILL.md)
- 委托模式技能详细说明：[skills/open-code-review-delegate/SKILL.md](./skills/open-code-review-delegate/SKILL.md)
