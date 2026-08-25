---
name: run-deepseek-v4-flash
description: Deploy DeepSeek-V4-Flash model on Ascend NPU with vllm-ascend — single-node Docker launch, environment tuning, OpenAI-compatible API, MTP speculative decoding, tool-call support
---

# Deploy DeepSeek-V4-Flash on Ascend with vllm-ascend

Deploy `DeepSeek-V4-Flash-w8a8-mtp` (W8A8 quantized, 1M context) on a single
Ascend node using the official `vllm-ascend` Docker image. The deployment
exposes an OpenAI-compatible API at `http://<host>:<port>/v1`.

**Driver:** [`deploy.sh`](./deploy.sh)

## Prerequisites

- **Hardware:**
  - Atlas 800 A2 (8 × Ascend 910B, 64G each) — image tag `deepseekv4`
  - Atlas 800 A3 (8 × Ascend 910B, 128G each) — image tag `deepseekv4-a3`
- **Software:**
  - Docker
  - Ascend NPU driver + CANN installed on host
  - Model weights downloaded (e.g. via `modelscope`) at known path

## Build / Setup

No build needed — use the pre-built Docker images from `quay.io`:

```bash
# A2 (Atlas 800 A2, 8×64G)
docker pull quay.io/ascend/vllm-ascend:deepseekv4

# A3 (Atlas 800 A3, 8×128G)
docker pull quay.io/ascend/vllm-ascend:deepseekv4-a3
```

## Run (agent path)

Use the `deploy.sh` driver. It launches the container, sets environment
variables, and starts the `vllm serve` process.

```bash
cd <project-root>/run-deepseek-v4-flash
./deploy.sh \
  --model /path/to/DeepSeek-V4-Flash-w8a8-mtp \
  --image quay.io/ascend/vllm-ascend:deepseekv4-a3 \
  --port 8008 \
  --model-name dsv4 \
  --gpu-memory-util 0.9 \
  --max-model-len 1024000
```

The driver starts the container in the background, prints the container
name, and tails the server log. Access the API at:

```bash
curl http://<host-ip>:8008/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dsv4",
    "messages": [{"role":"user","content":"Hello!"}]
  }'
```

**Stop the server:**

```bash
docker stop vllm-ascend-dsv4
```

## Run (human path)

Start the container interactively, then run `vllm serve` inside:

```bash
# Start container
docker run --rm --name vllm-ascend \
  --net=host --shm-size=512g \
  --device /dev/davinci0 --device /dev/davinci1 --device /dev/davinci2 \
  --device /dev/davinci3 --device /dev/davinci4 --device /dev/davinci5 \
  --device /dev/davinci6 --device /dev/davinci7 \
  --device /dev/davinci_manager --device /dev/devmm_svm \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
  -v /mnt/model:/root/.cache \
  -it quay.io/ascend/vllm-ascend:deepseekv4-a3 bash

# Inside container — set env vars
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=10
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export ACL_OP_INIT_MODE=1
export ASCEND_A3_ENABLE=1
export USE_MULTI_GROUPS_KV_CACHE=1
export USE_MULTI_BLOCK_POOL=1
export HCCL_BUFFSIZE=1024
export VLLM_ASCEND_ENABLE_FUSED_MC2=1
export VLLM_ASCEND_ENABLE_FLASHCOMM1=1

# Launch server
vllm serve /root/.cache/modelscope/hub/models/vllm-ascend/DeepSeek-V4-Flash-w8a8-mtp \
  --enable-prefix-caching \
  --max_model_len 1024000 \
  --max-num-batched-tokens 8192 \
  --served-model-name dsv4 \
  --gpu-memory-utilization 0.9 \
  --api-server-count 1 \
  --max-num-seqs 16 \
  --data-parallel-size 4 \
  --tensor-parallel-size 4 \
  --enable-expert-parallel \
  --tokenizer-mode deepseek_v4 \
  --tool-call-parser deepseek_v4 \
  --enable-auto-tool-choice \
  --reasoning-parser deepseek_v4 \
  --safetensors-load-strategy prefetch \
  --quantization ascend \
  --speculative-config '{"num_speculative_tokens": 1,"method": "deepseek_mtp"}' \
  --port 8008 \
  --block-size 128 \
  --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
  --async-scheduling
```

## Key configuration differences

| Hardware | Docker image | Env vars | TP | DP | Max context |
|----------|-------------|----------|----|----|-------------|
| A2 (8×64G) | `deepseekv4` | `OMP_NUM_THREADS=8`, `LD_PRELOAD=jemalloc` | 8 | 1 | 135168 |
| A3 (8×128G) | `deepseekv4-a3` | `OMP_NUM_THREADS=10`, `ASCEND_A3_ENABLE=1` | 4 | 4 | 1024000 |

## Gotchas

- **`vllm_abort_stream` / `KeyError` on client disconnect:** harmless — the
  server logs these but the remaining requests continue fine.
- **Model loading takes 5–10 minutes** on the first launch because of NPU
  graph compilation. Set `VLLM_ENGINE_READY_TIMEOUT_S=3600` if it times out.
- **Always use `--quantization ascend`** (not `w8a8`). The `ascend` scheme
  is the correct quantization backend for the adapted checkpoints.
- **`--tokenizer-mode deepseek_v4`** is required — the default tokenizer
  does not handle DeepSeek V4's special tokens (tool-calls, reasoning).
- **Multi-node** requires `--data-parallel-address` and `--headless` on
  secondary nodes (see [`run-deepseek-v4-pro`](../run-deepseek-v4-pro/SKILL.md) skill for the pattern).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Transformers does not recognize deepseek_v4` | Use the Ascend-adapted checkpoint (`-w8a8-mtp` variant), not the raw HuggingFace original |
| `invalid tool call parser: deepseek_v4` | Image too old — use `deepseekv4`-tagged image or apply the agentic-support patch |
| `ImportError: set_random_seed` | Version mismatch between vllm and vllm-ascend — never mix; always use the pre-built Docker image |
| Engine ready timeout | Increase `VLLM_ENGINE_READY_TIMEOUT_S=3600` |
| OOM on A2 | Reduce `--max-model-len` to 65536 and `--gpu-memory-utilization` to 0.85 |
| NPU device not found | Verify `/dev/davinci*` devices exist and driver is loaded (`npu-smi info`) |

## References

- https://docs.vllm.ai/projects/ascend/zh-cn/v0.18.0/tutorials/models/DeepSeek-V4-Flash.html
- https://github.com/vllm-project/vllm-ascend
- https://www.hiascend.com/zh/developer/techArticles/20260425-1
