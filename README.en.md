# skills-hub

Agent Skills Collection — Automated operations and deployment workflows for Huawei Cloud and Ascend AI infrastructure.

## Skills List

| Skill | Description |
|-------|-------------|
| [bms-create-ims](./bms-create-ims/) | Huawei Cloud Bare Metal Server (BMS) private image creation (OS install, partition, drivers, Cloud-Init) |
| [get-esm-api](./get-esm-api/) | ESM API integration — IAM Token auth, APIG AppCode, capacity/alarms/audit logs/billing query |
| [get-kaoshibao-list](./get-kaoshibao-list/) | Kaoshibao exam question extraction JS script (run in browser Console) |
| [run-deepseek-v4-flash](./run-deepseek-v4-flash/) | DeepSeek-V4-Flash Ascend single-node deployment — vllm-ascend, Docker, MTP inference |
| [run-deepseek-v4-pro](./run-deepseek-v4-pro/) | DeepSeek-V4-Pro Ascend multi-node cluster deployment — Apptainer, Slurm, 4×8×910B |
| [run-kaoshibao-collect](./run-kaoshibao-collect/) | Kaoshibao browser automated collection — Playwright, obfuscated font decoding, pagination |
| [run-qwen35-35b-mindie](./run-qwen35-35b-mindie/) | Qwen3.5-35B Ascend MindIE inference deployment — conf.json, environment scripts, mindieservice_daemon |
| [run-sg-policy-deploy](./run-sg-policy-deploy/) | Huawei Cloud security group port policy deployment — ticket parser, SG query, rule creation |

## Usage

Each skill resides in its own directory containing `SKILL.md` (instructions) and corresponding driver scripts.
Skills are automatically discovered and loaded on demand by the AI agent.

## License

Internal Use
