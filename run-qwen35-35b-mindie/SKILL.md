---
name: run-qwen35-35b-mindie
description: Deploy Qwen3.5-35B on Ascend with MindIE inference engine — source env scripts, conf.json config, mindieservice_daemon startup, OpenAI-compatible API
---

# Deploy Qwen3.5-35B on Ascend with MindIE

Deploy `Qwen3.5-35B` (or `Qwen3.5-35B-A3B` MoE variant) on Ascend hardware
using Huawei MindIE inference engine. The service exposes an
OpenAI-compatible API at `http://<host>:1025/v1/chat/completions`.

**Driver:** [`deploy.sh`](./deploy.sh) — sources MindIE env, generates config, starts service.

## Prerequisites

### Hardware

- **Ascend Atlas 800I A2** (8 × Ascend 910B, 64G each) — recommended
- **Atlas 800 A3** (8 × Ascend 910B, 128G each)
- 35B model recommended **4 cards** (worldSize=4, FP16 inference)
- 35B-A3B MoE model recommended **2–4 cards**

### Software

- Ascend NPU driver + CANN + MindIE installed (usually under `/usr/local/Ascend/`)
- JEMalloc (`/usr/lib64/libjemalloc.so.2`)
- Model weights downloaded

## Install / Setup

### 1. Download model weights

```bash
pip install modelscope

# Qwen3.5-35B (Dense)
modelscope download --model Qwen/Qwen3.5-35B-Instruct \
  --local_dir /data/models/Qwen3.5-35B-Instruct

# Or Qwen3.5-35B-A3B (MoE) — if using this variant
modelscope download --model Qwen/Qwen3.5-35B-A3B \
  --local_dir /data/models/Qwen3.5-35B-A3B
```

### 2. Verify MindIE installation

```bash
ls /usr/local/Ascend/mindie/latest/mindie-service/
# Should see: bin/ conf/ lib/ ...

# Check CANN
source /usr/local/Ascend/ascend-toolkit/set_env.sh
npu-smi info
```

## Run (agent path)

Use the `deploy.sh` driver. It:
1. Sources all MindIE/CANN environment scripts
2. Sets the optimized environment variables
3. Generates `conf/config.json` with proper Qwen3.5-35B settings
4. Starts `mindieservice_daemon` in the background
5. Waits for the service to be ready

```bash
cd <project-root>/run-qwen35-35b-mindie

# Start the service
bash deploy.sh /data/models/Qwen3.5-35B-Instruct qwen35
```

**Parameters:**

| Arg | Description |
|-----|-------------|
| `model_path` (required) | Absolute path to model weights directory |
| `model_name` (optional) | Served model name, default `qwen35` |
| `world_size` (optional) | Tensor parallelism, default `4` |
| `port` (optional) | API port, default `1025` |
| `max_seq_len` (optional) | Max sequence length, default `8192` |

**Test the API:**

```bash
# After service is ready
curl -X POST http://127.0.0.1:1025/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen35",
    "messages": [{"role":"user","content":"你好，请介绍一下你自己"}]
  }'
```

**Check service status:**

```bash
tail -f /usr/local/Ascend/mindie/latest/mindie-service/output.log
```

**Stop the service:**

```bash
pkill -f mindieservice_daemon
# or
kill $(pgrep -f mindieservice_daemon)
```

## Run (human path)

### Step 1: Source environment

```bash
source /usr/local/Ascend/ascend-toolkit/set_env.sh
source /usr/local/Ascend/nnal/atb/set_env.sh
source /usr/local/Ascend/atb-models/set_env.sh
source /usr/local/Ascend/mindie/set_env.sh
source /usr/local/Ascend/mindie/latest/mindie-service/set_env.sh
```

### Step 2: Set environment variables

```bash
export LD_PRELOAD="/usr/lib64/libjemalloc.so.2"
export MINDIE_ASYNC_SCHEDULING_ENABLE=1
export PYTORCH_NPU_ALLOC_CONF="expandable_segments:True"
export NPU_MEMORY_FRACTION=0.96
export ASCEND_SLOG_PRINT_TO_STDOUT=0
export ASCEND_GLOBAL_EVENT_ENABLE=1
export ATB_LOG_TO_FILE=0
export ASDOPS_LOG_LEVEL=ERROR
export MINDIE_LLM_CONTINUOUS_BATCHING=1
export MINDIE_LLM_RECOMPUTE_THRESHOLD=0.5
export DIST_PD_DISAGGREGATION=1
export ATB_WORKSPACE_MEM_ALLOC_ALG_TYPE=3
export OMP_NUM_THREADS=8
export DP_MOVE_UP_ENABLE=1
export CPU_AFFINITY_CONF=1
export TASK_QUEUE_ENABLE=2
export ATB_OPERATION_EXECUTE_ASYNC=2
export MINDIE_LOG_TO_STDOUT=0
export HCCL_CONNECT_TIMEOUT=7200
unset HCCL_OP_EXPANSION_MODE
unset ATB_LLM_HCCL_ENABLE
```

### Step 3: Configure conf/config.json

Edit `/usr/local/Ascend/mindie/latest/mindie-service/conf/config.json`:

```json
{
  "Version": "1.0.0",
  "LogConfig": {
    "logLevel": "Info",
    "logFileSize": 20,
    "logFileNum": 20,
    "logPath": "logs/"
  },
  "ServerConfig": {
    "ipAddress": "0.0.0.0",
    "managementIpAddress": "127.0.0.2",
    "port": 1025,
    "managementPort": 1026,
    "metricsPort": 1027,
    "allowAllZeroIpListening": true,
    "maxLinkNum": 1000,
    "httpsEnabled": false,
    "fullTextEnabled": false,
    "inferMode": "standard",
    "openAiSupport": "vllm"
  },
  "BackendConfig": {
    "backendName": "mindieservice_llm_engine",
    "modelInstanceNumber": 1,
    "npuDeviceIds": [[0, 1, 2, 3]],
    "tokenizerProcessNumber": 8,
    "ModelDeployConfig": {
      "maxSeqLen": 8192,
      "maxInputTokenLen": 8192,
      "truncation": false,
      "ModelConfig": [{
        "modelName": "qwen35",
        "modelInstanceType": "Standard",
        "modelWeightPath": "/data/models/Qwen3.5-35B-Instruct",
        "worldSize": 4,
        "cpuMemSize": 10,
        "npuMemSize": -1,
        "backendType": "atb",
        "trustRemoteCode": true
      }]
    },
    "ScheduleConfig": {
      "maxBatchSize": 64,
      "maxPrefillBatchSize": 32,
      "maxPrefillTokens": 4096,
      "cacheBlockSize": 128
    }
  }
}
```

> **Note:** For HTTPS environments, set `"httpsEnabled": true` and configure `tlsCaPath`, `tlsCert`, `tlsPk`.

### Step 4: Start the service

```bash
cd /usr/local/Ascend/mindie/latest/mindie-service
nohup ./bin/mindieservice_daemon > output.log 2>&1 &
echo $! > mindie.pid
```

### Step 5: Verify

```bash
# Wait for startup (~2-5 min for first load with graph compilation)
sleep 60
tail -20 output.log
# Should show: "Start server success" or "listening on 0.0.0.0:1025"

# Test inference
curl -X POST http://127.0.0.1:1025/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen35",
    "messages": [{"role":"user","content":"Hello"}]
  }'
```

## Configuration Reference

### Key config.json parameters

| Section | Parameter | Recommended | Description |
|---------|-----------|-------------|-------------|
| ServerConfig | `port` | `1025` | API port |
| ServerConfig | `ipAddress` | `0.0.0.0` | Listen all interfaces |
| ServerConfig | `httpsEnabled` | `false` | Disable for internal network |
| BackendConfig | `npuDeviceIds` | `[[0,1,2,3]]` | 4 cards for 35B model |
| BackendConfig | `tokenizerProcessNumber` | `8` | Tokenizer workers |
| ModelDeployConfig | `maxSeqLen` | `8192` | Max context length |
| ModelDeployConfig | `maxInputTokenLen` | `8192` | Max input length |
| ModelConfig | `worldSize` | `4` | Tensor parallel size |
| ModelConfig | `backendType` | `atb` | Ascend backend |
| ModelConfig | `cpuMemSize` | `10` | CPU memory (GB) |
| ModelConfig | `npuMemSize` | `-1` | -1 = auto |
| ScheduleConfig | `maxBatchSize` | `64` | Max batch size |
| ScheduleConfig | `cacheBlockSize` | `128` | KV cache block size |

### WorldSize recommendation

| Model | Precision | Cards (worldSize) |
|-------|-----------|-------------------|
| Qwen3.5-35B (Dense) | FP16 | 4 |
| Qwen3.5-35B (Dense) | BF16 | 4 |
| Qwen3.5-35B-A3B (MoE) | FP16 | 2–4 |
| Qwen3.5-35B-A3B (MoE) | W8A8 | 2 |

### Environment variable guide

See `deploy.sh` for the complete set. The key groups are:

| Group | Variables | Purpose |
|-------|-----------|---------|
| Memory | `PYTORCH_NPU_ALLOC_CONF`, `NPU_MEMORY_FRACTION`, `LD_PRELOAD` (jemalloc) | NPU/host memory tuning |
| Scheduling | `MINDIE_ASYNC_SCHEDULING_ENABLE`, `MINDIE_LLM_CONTINUOUS_BATCHING`, `TASK_QUEUE_ENABLE` | Async + continuous batching |
| Communication | `HCCL_CONNECT_TIMEOUT`, `DIST_PD_DISAGGREGATION`, unset `HCCL_OP_EXPANSION_MODE` | HCCL distributed settings |
| Logging | `ASCEND_SLOG_PRINT_TO_STDOUT=0`, `ATB_LOG_TO_FILE=0`, `MINDIE_LOG_TO_STDOUT=0` | Suppress verbose logs |
| Compute | `OMP_NUM_THREADS=8`, `ATB_OPERATION_EXECUTE_ASYNC=2`, `DP_MOVE_UP_ENABLE=1` | CPU/NPU compute optimization |

## Gotchas

- **First startup takes 5-15 minutes** — MindIE compiles NPU graphs on the
  first run. Subsequent starts are faster.
- **`conf/config.json` must be in the MindIE service directory** — the
  service reads it relative to its working directory, not from an arbitrary
  path.
- **`openAiSupport: "vllm"`** makes the API compatible with the vllm-style
  OpenAI endpoint (`/v1/chat/completions`). Without this, the endpoint path
  differs.
- **Do NOT set `HCCL_OP_EXPANSION_MODE`** — the deployment explicitly unsets
  it (`unset HCCL_OP_EXPANSION_MODE`), which is required for MindIE's
  internal HCCL management.
- **`ATB_LLM_HCCL_ENABLE` is also unset** — MindIE uses its own HCCL
  configuration; explicitly disabling this avoids conflicts.
- **`npuMemSize: -1` means auto-detect** — the engine uses all available
  NPU memory, respecting `NPU_MEMORY_FRACTION=0.96`.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `libjemalloc.so.2: cannot open` | Install: `apt-get install libjemalloc2` or `yum install jemalloc` |
| `mindieservice_daemon: command not found` | Check `source` scripts ran correctly and `mindie/latest/mindie-service/bin/` exists |
| `Start server failed` / `bind error: Address already in use` | Port conflict — change `port` in config.json or kill existing process |
| Service starts but 502 on API call | Model not fully loaded yet — wait 5-15 min for first-time graph compilation |
| `HCCL timeout` with multi-card | Increase `HCCL_CONNECT_TIMEOUT=7200`; check `npu-smi info` shows all cards online |
| OOM during inference | Reduce `maxSeqLen` to 4096, or increase `worldSize` to use more cards |
| `tokenizer not found` error | Set `trustRemoteCode: true` in config; verify model path contains `tokenizer_config.json` |
| `backendType not supported` | Ensure MindIE version supports `atb` backend (MindIE 1.0.RC2+) |
| No responses but no error | Check `ASCEND_SLOG_PRINT_TO_STDOUT=0` — set to 1 temporarily to see Ascend logs |
| `libascend_hal.so` not found | Verify CANN is installed and sourced correctly via `set_env.sh` |

## References

- [华为 MindIE 文档](https://www.hiascend.com/document/detail/zh/mindie/21RC2/index/index.html)
- [MindIE Service 配置参数说明](https://www.hiascend.com/document/detail/zh/mindie/10RC3/mindiellm/llmdev/mindie_llm0004.html)
- [MindIE Service 启动服务](https://www.hiascend.com/document/detail/zh/mindie/100/mindieservice/servicedev/mindie_service0004.html)
- [Qwen3.5 模型专区](https://modelers.cn/topics/qwen3)
- [Datawhale — Qwen3-8B MindIE 部署教程](https://github.com/datawhalechina/self-llm/blob/master/models_ascend/qwen3/01-Qwen3-8B-MindIE%E9%83%A8%E7%BD%B2%E8%B0%83%E7%94%A8.md)
