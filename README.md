# skills-hub

AI 智能体技能与插件集合 — 面向云基础设施运维部署、自动化代码审查、网页采集、AI视频制作与严谨软件工程工作流（原生适配 Google Antigravity、DeepSeek Harness (DSH) 与 Claude Code）。

## 技能列表

### 智能代码审查 (Alibaba Open Code Review)

> 阿里巴巴开源 AI 代码审查工具，结合确定性工程与 Agent 混合驱动，提供行级精准审查与委托审查能力。

| 技能 | 说明 |
|------|------|
| [open-code-review](./open-code-review/) | 阿里开源 AI 代码审查套件主索引 — 包含 CLI 驱动模式与 Agent 委托模式完整支持 |
| [open-code-review (skill)](./open-code-review/skills/open-code-review/) | 完整 CLI 驱动审查 — 自动化 Git diff 提取、规则匹配、LLM 审查与行级评论输出 |
| [open-code-review-delegate](./open-code-review/skills/open-code-review-delegate/) | 委托模式审查 — 由当前宿主 Agent 利用自身大模型推理，OCR 负责确定性规则匹配与文件筛选 |

### 华为云与昇腾 AI 基础设施

| 技能 | 说明 |
|------|------|
| [bms-create-ims](./bms-create-ims/) | 裸金属服务器BMS私有镜像制作（OS 安装、分区、驱动、Cloud-Init） |
| [get-esm-api](./get-esm-api/) | ESM API 调用 — IAM Token 认证、APIG AppCode、容量/告警/审计/话单查询 |
| [run-deepseek-v4-flash](./run-deepseek-v4-flash/) | DeepSeek-V4-Flash 昇腾单机部署 — vllm-ascend、Docker、MTP 推理 |
| [run-deepseek-v4-pro](./run-deepseek-v4-pro/) | DeepSeek-V4-Pro 昇腾多机集群部署 — Apptainer、Slurm、4×8×910B |
| [run-qwen35-35b-mindie](./run-qwen35-35b-mindie/) | Qwen3.5-35B 昇腾 MindIE 推理部署 — conf.json、环境脚本、mindieservice_daemon |
| [run-sg-policy-deploy](./run-sg-policy-deploy/) | 安全组端口策略工单开通 — 工单解析、查询安全组、添加规则、不删已有规则 |

### 严谨软件工程 (pstack 技能套件)

> 原生适配 Google Antigravity 与 DeepSeek Harness (DSH)，源自 Lauren Tan (@poteto)。

| 技能 | 说明 |
|------|------|
| [pstack](./pstack/) | 严谨软件工程技能套件主索引 — 包含 23 个任务剧本、23 个工程原则、多模型对抗审查、架构设计与行为级验证 |
| [poteto-mode](./pstack/skills/poteto-mode/) | 严谨自动化软件工程主循环 — 全生命周期推进、自愈与多阶段实施 |
| [setup-pstack](./pstack/skills/setup-pstack/) | pstack 环境初始化与模型路由配置（支持 Antigravity / DSH） |
| [architect](./pstack/skills/architect/) | 架构设计决策与 ADR 生成 — 方案对抗推演与架构把关 |
| [arena](./pstack/skills/arena/) | 多模型/多方案对抗评估 — 独立分支实施与胜者合并 |
| [interrogate](./pstack/skills/interrogate/) | 代码审阅与对抗质询 — 严格发现缺陷与潜在风险 |
| [reflect](./pstack/skills/reflect/) | 计划审阅与多视角把关 — 审查实施计划与技术方案 |
| [show-me-your-work](./pstack/skills/show-me-your-work/) | 决策证据链记录 — 记录设计决策、权衡与验证结果 |
| [create-verification-skill](./pstack/skills/create-verification-skill/) | 行为级验证技能编写 — 针对新功能沉淀可复用的验证逻辑 |

### 网页内容与数据采集

| 技能 | 说明 |
|------|------|
| [get-exam4ksb-list](./get-exam4ksb-list/) | 考试宝(ksb)题目提取原始 JS 脚本（浏览器 Console 运行，支持混淆字体解码与导出） |
| [run-exam4ksb-collect](./run-exam4ksb-collect/) | 考试宝(ksb)浏览器自动化采集 — Playwright、混淆字体解码、翻页提取与截图 |

### AI 课程与视频内容生产

| 技能 | 说明 |
|------|------|
| [deeplearn-vp-create](./deeplearn-vp-create/) | DeepLearning.AI 课程视频制作全流程 — 字幕提取、翻译旁白、故事板审阅、TTS配音与Remotion渲染 |
| [dl-ai-lesson-create](./dl-ai-lesson-create/) | DL.AI 课程视频制作 — Python + Pillow + ffmpeg 确定性渲染器与 DashScope 语音合成 |
| [dl-ai-lesson-remotion](./dl-ai-lesson-remotion/) | Remotion AI 课程视频制作 — 审阅优先(Review-First)工作流、原生1080p渲染与课程封面生成 |
| [video](./video/) | AI 视频制作与编程式视频生成 — Remotion/Hyperframes、AI Avatars (HeyGen) 及生成大模型 |

### 架构可视化与项目管理

| 技能 | 说明 |
|------|------|
| [creating-architecture-web-explainers](./creating-architecture-web-explainers/) | 架构 Web 交互式解释器制作 — 将技术栈与架构流转转为中文单文件 Web 解释器或 Archscribe 图 |
| [pmo-methodology](./pmo-methodology/) | 项目管理公约与项目实施方法论 — 涵盖实施六阶段、交付物标准及六大管理公约 |

## 使用方式

每个技能独立一个目录，包含 `SKILL.md`（使用说明）及可选的辅助驱动脚本。

### 在 Google Antigravity 中使用
- 本仓库已在 `.agents/skills.json` 和 `.agents/plugins.json` 中配置好技能发现规则。
- 在 Antigravity 中打开本仓库，即可自动发现所有技能。
- 支持在对话中直接通过 `/<skill-name>` 调用（如 `/poteto-mode`, `/setup-pstack`, `/architect`, `/bms-create-ims`）。

### 在 DeepSeek Harness (DSH) 中使用
- 将相应技能目录或 `pstack/skills/` 挂载至 DSH 技能目录。
- 智能体根据任务需求自动加载对应 `SKILL.md` 指令。

### 在 Claude Code 中使用
- 直接调用 `/<技能名>` 即可加载对应技能。

## 许可证

内部使用 / pstack 沿用 MIT 许可证
