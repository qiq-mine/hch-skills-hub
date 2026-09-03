# skills-hub

技能集合

## 技能列表

| 技能 | 说明 |
|------|------|
| [bms-create-ims](./bms-create-ims/) | 裸金属服务器BMS私有镜像制作（OS 安装、分区、驱动、Cloud-Init） |
| [get-esm-api](./get-esm-api/) | ESM API 调用 — IAM Token 认证、APIG AppCode、容量/告警/审计/话单查询 |
| [run-deepseek-v4-flash](./run-deepseek-v4-flash/) | DeepSeek-V4-Flash 昇腾单机部署 — vllm-ascend、Docker、MTP 推理 |
| [run-deepseek-v4-pro](./run-deepseek-v4-pro/) | DeepSeek-V4-Pro 昇腾多机集群部署 — Apptainer、Slurm、4×8×910B |
| [get-kaoshibao-list](./get-kaoshibao-list/) | web-context提取原始 JS 脚本（浏览器 Console 运行） |
| [run-kaoshibao-collect](./run-kaoshibao-collect/) | web-context浏览器自动化采集 — Playwright、混淆字体解码、翻页提取 |
| [run-qwen35-35b-mindie](./run-qwen35-35b-mindie/) | Qwen3.5-35B 昇腾 MindIE 推理部署 — conf.json、环境脚本、mindieservice_daemon |
| [run-sg-policy-deploy](./run-sg-policy-deploy/) | 安全组端口策略工单开通 — 工单解析、查询安全组、添加规则、不删已有规则 |

## 使用方式

每个技能独立一个目录，包含 `SKILL.md`（使用说明）和对应的驱动脚本。
直接在 Claude Code 中调用 `/run-<技能名>` 即可加载对应技能。

## 许可证

内部使用
