# skills-hub

技能集合

## 技能列表

### 华为云与昇腾 AI 基础设施

| 技能 | 说明 |
|------|------|
| [bms-create-ims](./bms-create-ims/) | 裸金属服务器BMS私有镜像制作（OS 安装、分区、驱动、Cloud-Init） |
| [get-esm-api](./get-esm-api/) | ESM API 调用 — IAM Token 认证、APIG AppCode、容量/告警/审计/话单查询 |
| [run-deepseek-v4-flash](./run-deepseek-v4-flash/) | DeepSeek-V4-Flash 昇腾单机部署 — vllm-ascend、Docker、MTP 推理 |
| [run-deepseek-v4-pro](./run-deepseek-v4-pro/) | DeepSeek-V4-Pro 昇腾多机集群部署 — Apptainer、Slurm、4×8×910B |
| [run-qwen35-35b-mindie](./run-qwen35-35b-mindie/) | Qwen3.5-35B 昇腾 MindIE 推理部署 — conf.json、环境脚本、mindieservice_daemon |
| [run-sg-policy-deploy](./run-sg-policy-deploy/) | 安全组端口策略工单开通 — 工单解析、查询安全组、添加规则、不删已有规则 |

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

每个技能独立一个目录，包含 `SKILL.md`（使用说明）和对应的驱动脚本。
直接在 Claude Code 中调用 `/run-<技能名>` 即可加载对应技能。

## 许可证

内部使用
