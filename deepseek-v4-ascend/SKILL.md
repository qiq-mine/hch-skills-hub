---
name: deepseek-v4-ascend
description: "Deploy DeepSeek V4 on Ascend NPU with vllm-ascend — two topologies: single-node Docker (Flash w8a8) or multi-node Slurm+Apptainer cluster (Pro w4a8). OpenAI-compatible API, MTP speculative decoding, tool-call support. 昇腾框架选型指路：若使用华为官方 MindIE 推理引擎部署 Qwen 等模型见 qwen35-ascend-mindie。"
---

# DeepSeek V4 on Ascend (vllm-ascend)

两种部署拓扑，二选一（同一引擎 `vllm-ascend`，不同模型与调度方式）：

| | A：单机 Docker | B：多机 Slurm 集群 |
|---|---|---|
| 模型 | `DeepSeek-V4-Flash-w8a8-mtp`（W8A8，1M 上下文） | `DeepSeek-V4-Pro-w4a8-mtp`（W4A8，1M 上下文） |
| 容器 | Docker（`quay.io/ascend/vllm-ascend`） | Apptainer SIF |
| 调度 | 无（`docker run`） | Slurm |
| 驱动脚本 | [`deploy-single.sh`](./deploy-single.sh) | [`deploy-cluster.sh`](./deploy-cluster.sh) |
| 硬件 | Atlas 800 A2/A3 单机（8×910B） | 4+ 节点 × 8×910B，共享存储 + RoCE |

两种拓扑都暴露 OpenAI 兼容 API（`http://<host>:<port>/v1`），都支持 MTP 投机解码与工具调用。

---

## 拓扑 A：单机 Docker（Flash）

### Prerequisites

- **Hardware:**
  - Atlas 800 A2 (8 × Ascend 910B, 64G each) — image tag `deepseekv4`
  - Atlas 800 A3 (8 × Ascend 910B, 128G each) — image tag `deepseekv4-a3`
- **Software:**
  - Docker
  - Ascend NPU driver + CANN installed on host
  - Model weights downloaded (e.g. via `modelscope`) at known path

### Build / Setup

No build needed — use the pre-built Docker images from `quay.io`:

```bash
# A2 (Atlas 800 A2, 8×64G)
docker pull quay.io/ascend/vllm-ascend:deepseekv4

# A3 (Atlas 800 A3, 8×128G)
docker pull quay.io/ascend/vllm-ascend:deepseekv4-a3
```

### Run (agent path)

```bash
cd <project-root>/deepseek-v4-ascend
./deploy-single.sh \
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

### Run (human path)

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

### Key configuration differences (A2 vs A3)

| Hardware | Docker image | Env vars | TP | DP | Max context |
|----------|-------------|----------|----|----|-------------|
| A2 (8×64G) | `deepseekv4` | `OMP_NUM_THREADS=8`, `LD_PRELOAD=jemalloc` | 8 | 1 | 135168 |
| A3 (8×128G) | `deepseekv4-a3` | `OMP_NUM_THREADS=10`, `ASCEND_A3_ENABLE=1` | 4 | 4 | 1024000 |

---

## 拓扑 B：多机 Slurm 集群（Pro）

### Prerequisites

- **Hardware:**
  - 1 × management/control node (8× 910B)
  - 3+ × compute nodes (each 8× 910B)
  - Shared storage (OceanFS / SFS Turbo, 100‑500 GB)
  - RoCE or high-speed Ethernet interconnect
- **Software:**
  - Ascend NPU driver + CANN on all nodes
  - Apptainer (or Singularity)
  - Slurm workload manager
  - `cthpc` CLI (for fast model × container distribution)
  - Model weights downloaded at shared path

### Build / Setup

No build needed — use the pre-built SIF image and official checkpoint:

```bash
# Install model weights (w4a8-mtp quantized variant)
cthpc model install DeepSeek-V4-Pro-w4a8-mtp --dir /mnt/nvme1n1/model/

# Install the vllm-ascend Apptainer image
cthpc apptainer install vllm-ascend_deepseekv4 --dir /mnt/nvme0n1/apptainer/

# Or pull directly
apptainer pull vllm-ascend_deepseekv4.sif \
  docker://quay.io/ascend/vllm-ascend:deepseekv4
```

### Run (agent path)

```bash
cd <project-root>/deepseek-v4-ascend
./deploy-cluster.sh \
  --model-dir /mnt/nvme1n1/model/DeepSeek-V4-Pro-w4a8-mtp \
  --model-name DeepSeek-V4 \
  --port 11025 \
  --num-nodes 4 \
  --nodelist "master0001,compute0001,compute0002,compute0003" \
  --sif /mnt/nvme0n1/apptainer/vllm-ascend_deepseekv4.sif
```

The driver:
1. Creates `node.sh` and `srun.sh` in the working directory
2. Submits the Slurm job
3. Tails the log until the server is ready

**Monitor the job:**

```bash
squeue                    # list jobs
tail -f logs/log_*.out    # tail server log
```

**Stop the server:**

```bash
scancel -n deepseek       # cancel by job name
# or
scancel <JOBID>           # cancel by job ID
```

### Run (human path)

#### Directory layout

| Path | Purpose |
|------|---------|
| `/mnt/nvme0n1/apptainer/` | Apptainer SIF images (fast NVMe) |
| `/home/deepseek/` | Deployment working directory |
| `/mnt/nvme1n1/model/DeepSeek-V4-Pro-w4a8-mtp/` | Model weights |

#### Step-by-step

1. **Create `node.sh`** on the shared filesystem:

```bash
#!/bin/sh

nic_name="eno0"           # Use "bond0" for standard bare-metal
local_ip=$(hostname -i | awk '{print $1}')
node0_ip=$MASTER_ADDR

export HCCL_IF_IP=$local_ip
export GLOO_SOCKET_IFNAME=$nic_name
export TP_SOCKET_IFNAME=$nic_name
export HCCL_SOCKET_IFNAME=$nic_name
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=10
export HCCL_BUFFSIZE=200
export HCCL_OP_EXPANSION_MODE="AIV"
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export HCCL_CONNECT_TIMEOUT=120
export HCCL_INTRA_PCIE_ENABLE=1
export HCCL_INTRA_ROCE_ENABLE=0
export ACL_OP_INIT_MODE=1
export TRITON_ALL_BLOCKS_PARALLEL=1
export USE_MULTI_BLOCK_POOL=1
export USE_MULTI_GROUPS_KV_CACHE=1
export ASCEND_BUFFER_POOL=0:0
export VLLM_ASCEND_ENABLE_FLASHCOMM1=1
export VLLM_ENGINE_READY_TIMEOUT_S=3600

apptainer instance start --no-home --writable-tmpfs \
  -B /usr/local/sbin:/usr/local/sbin \
  -B /usr/local/Ascend/driver:/usr/local/Ascend/driver \
  -B ascend_log:/root/ascend \
  -B $MODEL_DIR:/model \
  $VLLM_IMG app-instance

if [ $SLURM_NODEID == 0 ]; then
  apptainer exec instance://app-instance \
    vllm serve /model \
      --served-model-name "$MODEL_NAME" \
      --host 0.0.0.0 --port "$MODEL_PORT" \
      --data-parallel-size $SLURM_NNODES \
      --data-parallel-size-local 1 \
      --data-parallel-address $node0_ip \
      --data-parallel-rpc-port 13389 \
      --tensor-parallel-size 8 \
      --quantization ascend \
      --seed 1024 \
      --enable-expert-parallel \
      --max-num-seqs 16 \
      --max-model-len 65536 \
      --max-num-batched-tokens 4096 \
      --tokenizer-mode deepseek_v4 \
      --tool-call-parser deepseek_v4 \
      --enable-auto-tool-choice \
      --reasoning-parser deepseek_v4 \
      --trust-remote-code \
      --async-scheduling \
      --enable-prefix-caching \
      --gpu-memory-utilization 0.95 \
      --safetensors-load-strategy prefetch \
      --default-chat-template-kwargs '{"thinking": true}' \
      --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
      --additional-config '{"ascend_compilation_config":{"enable_npugraph_ex":true,"enable_static_kernel":false},"enable_cpu_binding":"True"}' \
      --speculative-config '{"num_speculative_tokens": 3, "method": "deepseek_mtp"}'
else
  apptainer exec instance://app-instance \
    vllm serve /model \
      --served-model-name "$MODEL_NAME" \
      --host 0.0.0.0 --port "$MODEL_PORT" \
      --headless \
      --data-parallel-size $SLURM_NNODES \
      --data-parallel-size-local 1 \
      --data-parallel-start-rank $SLURM_NODEID \
      --data-parallel-address $node0_ip \
      --data-parallel-rpc-port 13389 \
      --tensor-parallel-size 8 \
      --quantization ascend \
      --seed 1024 \
      --enable-expert-parallel \
      --max-num-seqs 16 \
      --max-model-len 65536 \
      --max-num-batched-tokens 4096 \
      --tokenizer-mode deepseek_v4 \
      --tool-call-parser deepseek_v4 \
      --enable-auto-tool-choice \
      --reasoning-parser deepseek_v4 \
      --trust-remote-code \
      --async-scheduling \
      --enable-prefix-caching \
      --gpu-memory-utilization 0.95 \
      --safetensors-load-strategy prefetch \
      --default-chat-template-kwargs '{"thinking": true}' \
      --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
      --additional-config '{"ascend_compilation_config":{"enable_npugraph_ex":true,"enable_static_kernel":false},"enable_cpu_binding":"True"}' \
      --speculative-config '{"num_speculative_tokens": 3, "method": "deepseek_mtp"}'
fi
```

2. **Create `srun.sh`** to submit the job:

```bash
#!/bin/bash
#SBATCH -N 4
#SBATCH --partition=batch
#SBATCH -J deepseek
#SBATCH -o logs/log_%J.out
#SBATCH -e logs/log_%J.err
#SBATCH --gres=gpu:8
#SBATCH --cpus-per-task=190
#SBATCH --nodelist=master0001,compute0001,compute0002,compute0003

export LC_CTYPE=C.UTF-8
export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1 | hostname -i)
export MODEL_NAME=DeepSeek-V4
export MODEL_PORT=11025
export MODEL_DIR=/mnt/nvme1n1/model/DeepSeek-V4-Pro-w4a8-mtp
export VLLM_IMG=/mnt/nvme0n1/apptainer/vllm-ascend_deepseekv4.sif

srun --ntasks-per-node=1 \
  -o logs/log_%J.%t.out \
  -e logs/log_%J.%t.err \
  ./node.sh
```

3. **Submit and monitor:**

```bash
cd /home/deepseek
chmod +x node.sh
sbatch srun.sh
squeue
```

#### Gotchas (cluster)

- **VLLM_ENGINE_READY_TIMEOUT_S=3600** is essential — the first launch
  compiles NPU graphs and can take 20+ minutes across 4 nodes.
- **Model path must be on shared storage** accessible from all nodes.
  OceanFS / SFS Turbo recommended; NFS may be too slow for weight loading.
- **`--default-chat-template-kwargs '{"thinking": true}'`** enables the
  reasoning/thinking tags in the model output — omit this if you don't
  need the chain-of-thought prefix.
- **`enable_npugraph_ex: true`** in additional-config is critical for
  performance — enables NPU graph acceleration (A3-era feature).

---

## 通用说明（vllm-ascend，两种拓扑适用）

- **Always use `--quantization ascend`** (not `w8a8`/`w4a8`). The `ascend`
  scheme is the correct quantization backend for the adapted checkpoints.
- **`--tokenizer-mode deepseek_v4`** is required — the default tokenizer
  does not handle DeepSeek V4's special tokens (tool-calls, reasoning).
- **Model loading takes 5–20 minutes** on the first launch because of NPU
  graph compilation. Set `VLLM_ENGINE_READY_TIMEOUT_S=3600` if it times out.
- **`vllm_abort_stream` / `KeyError` on client disconnect:** harmless — the
  server logs these but the remaining requests continue fine.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Transformers does not recognize deepseek_v4` | Use the Ascend-adapted checkpoint (`-w8a8-mtp`/`-w4a8-mtp` variant), not the raw HuggingFace original |
| `invalid tool call parser: deepseek_v4` | Image too old — use `deepseekv4`-tagged image or apply the agentic-support patch |
| `ImportError: set_random_seed` | Version mismatch between vllm and vllm-ascend — never mix; always use the pre-built image |
| Engine ready timeout | Increase `VLLM_ENGINE_READY_TIMEOUT_S=3600` |
| OOM on A2 (single-node) | Reduce `--max-model-len` to 65536 and `--gpu-memory-utilization` to 0.85 |
| NPU device not found | Verify `/dev/davinci*` devices exist and driver is loaded (`npu-smi info`) |
| `HCCL connection timeout` (cluster) | Check `HCCL_CONNECT_TIMEOUT=120` and that all nodes can reach each other on the data-parallel-rpc-port |
| Node stuck at `Waiting for other nodes...` (cluster) | Verify `--data-parallel-address` points to the master node's reachable IP and `HCCL_IF_IP` is set correctly per node |
| Apptainer: `failed to mount` (cluster) | Ensure `-B /usr/local/Ascend/driver` points to the correct driver path on each node |
| Model loading extremely slow (cluster) | Share storage via parallel filesystem (OceanFS/SFS Turbo), not NFS |
| Server starts but responses are garbled | Verify `--tokenizer-mode deepseek_v4` and `--quantization ascend` are set |
| Out of memory at max_model_len (cluster) | Reduce `--max-model-len` to 32768 or lower `--gpu-memory-utilization` to 0.9 |

## References

- https://docs.vllm.ai/projects/ascend/zh-cn/v0.18.0/tutorials/models/DeepSeek-V4-Flash.html
- https://github.com/vllm-project/vllm-ascend
- https://www.hiascend.com/zh/developer/techArticles/20260425-1
- https://www.ctyun.cn/document/20661708/11094350

---
*2026-10-08：由 `run-deepseek-v4-flash`（单机 Docker）与 `run-deepseek-v4-pro`（多机 Slurm 集群）合并为 `deepseek-v4-ascend`（拓扑二选一；驱动脚本分别保留为 deploy-single.sh / deploy-cluster.sh）。`run-qwen35-35b-mindie` 保持独立（模型与引擎均不同）。*
