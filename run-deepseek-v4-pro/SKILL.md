---
name: run-deepseek-v4-pro
description: Deploy DeepSeek-V4-Pro model on multi-node Ascend cluster with vllm-ascend — Apptainer/Singularity, Slurm scheduling, tensor+data+expert parallelism, MTP speculative decoding, tool-call/agent support
---

# Deploy DeepSeek-V4-Pro on Ascend with vllm-ascend

Deploy `DeepSeek-V4-Pro-w4a8-mtp` (W4A8 quantized, 1M context) on a
multi-node Ascend cluster using the official `vllm-ascend` Apptainer (SIF)
image and Slurm workload manager. Minimum: 4 nodes × 8× Ascend 910B (64G).

The deployment exposes an OpenAI-compatible API at
`http://<master-node-ip>:<port>/v1`.

**Driver:** [`deploy.sh`](./deploy.sh)

## Prerequisites

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

## Build / Setup

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

## Run (agent path)

Use the `deploy.sh` driver. It generates the Slurm job script and submits
it to the cluster.

```bash
cd <project-root>/run-deepseek-v4-pro
./deploy.sh \
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

## Run (human path)

### Directory layout

| Path | Purpose |
|------|---------|
| `/mnt/nvme0n1/apptainer/` | Apptainer SIF images (fast NVMe) |
| `/home/deepseek/` | Deployment working directory |
| `/mnt/nvme1n1/model/DeepSeek-V4-Pro-w4a8-mtp/` | Model weights |

### Step-by-step

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

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │         Master Node (node0)          │
                    │  ┌──────────────────────────────┐    │
                    │  │ vllm serve (API server)      │    │
                    │  │ TP=8 DP=4 EP on (8× 910B)   │    │
                    │  │ Port 11025 /v1                │    │
                    │  └──────────┬───────────────────┘    │
                    └─────────────┼────────────────────────┘
                                  │ DP-RPC (port 13389)
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
  ┌──────┴──────┐         ┌──────┴──────┐         ┌──────┴──────┐
  │ Compute 1   │         │ Compute 2   │         │ Compute 3   │
  │ vllm serve  │         │ vllm serve  │         │ vllm serve  │
  │ --headless  │         │ --headless  │         │ --headless  │
  │ TP=8 DP=4   │         │ TP=8 DP=4   │         │ TP=8 DP=4   │
  │ 910B × 8    │         │ 910B × 8    │         │ 910B × 8    │
  └─────────────┘         └─────────────┘         └─────────────┘
```

## Gotchas

- **VLLM_ENGINE_READY_TIMEOUT_S=3600** is essential — the first launch
  compiles NPU graphs and can take 20+ minutes across 4 nodes.
- **Model path must be on shared storage** accessible from all nodes.
  OceanFS / SFS Turbo recommended; NFS may be too slow for weight loading.
- **`--default-chat-template-kwargs '{"thinking": true}'`** enables the
  reasoning/thinking tags in the model output — omit this if you don't
  need the chain-of-thought prefix.
- **`enable_npugraph_ex: true`** in additional-config is critical for
  performance — enables NPU graph acceleration (A3-era feature).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `HCCL connection timeout` | Check `HCCL_CONNECT_TIMEOUT=120` and that all nodes can reach each other on the data-parallel-rpc-port |
| Node stuck at `Waiting for other nodes...` | Verify `--data-parallel-address` points to the master node's reachable IP and `HCCL_IF_IP` is set correctly per node |
| `OMP_NUM_THREADS` mismatch warnings | Set `OMP_PROC_BIND=false` and same `OMP_NUM_THREADS` on all nodes (10 recommended) |
| Apptainer: `failed to mount` | Ensure `-B /usr/local/Ascend/driver` points to the correct driver path on each node |
| Model loading extremely slow | Share storage via parallel filesystem (OceanFS/SFS Turbo), not NFS |
| Server starts but responses are garbled | Verify `--tokenizer-mode deepseek_v4` and `--quantization ascend` are set |
| Out of memory at max_model_len | Reduce `--max-model-len` to 32768 or lower `--gpu-memory-utilization` to 0.9 |

## References

- https://www.ctyun.cn/document/20661708/11094350
- https://docs.vllm.ai/projects/ascend/zh-cn/v0.18.0/tutorials/models/DeepSeek-V4-Flash.html
- https://github.com/vllm-project/vllm-ascend
