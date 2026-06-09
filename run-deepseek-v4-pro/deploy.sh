#!/usr/bin/env bash
set -euo pipefail

# deploy.sh — Deploy DeepSeek-V4-Pro on multi-node Ascend cluster with vllm-ascend
#
# Generates the Slurm job scripts (node.sh + srun.sh), submits, and tails logs.
#
# Usage:
#   ./deploy.sh \
#     --model-dir /mnt/nvme1n1/model/DeepSeek-V4-Pro-w4a8-mtp \
#     --model-name DeepSeek-V4 \
#     --port 11025 \
#     --num-nodes 4 \
#     --nodelist "master0001,compute0001,compute0002,compute0003" \
#     --sif /mnt/nvme0n1/apptainer/vllm-ascend_deepseekv4.sif

# ---- defaults ----
MODEL_DIR=""
MODEL_NAME="DeepSeek-V4"
PORT=11025
NUM_NODES=4
NODELIST=""
SIF=""
PARTITION="batch"
WORK_DIR="${WORK_DIR:-/home/deepseek}"
TP_SIZE=8
MAX_MODEL_LEN=65536
GPU_MEM_UTIL=0.95
NUM_SPEC_TOKENS=3
NIC_NAME="eno0"            # "bond0" for standard bare-metal

# ---- parse args ----
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model-dir)  MODEL_DIR="$2";   shift 2 ;;
    --model-name) MODEL_NAME="$2";  shift 2 ;;
    --port)       PORT="$2";        shift 2 ;;
    --num-nodes)  NUM_NODES="$2";   shift 2 ;;
    --nodelist)   NODELIST="$2";    shift 2 ;;
    --sif)        SIF="$2";         shift 2 ;;
    --partition)  PARTITION="$2";   shift 2 ;;
    --work-dir)   WORK_DIR="$2";    shift 2 ;;
    --nic)        NIC_NAME="$2";    shift 2 ;;
    --tp-size)    TP_SIZE="$2";     shift 2 ;;
    --max-model-len) MAX_MODEL_LEN="$2"; shift 2 ;;
    --gpu-memory-util) GPU_MEM_UTIL="$2"; shift 2 ;;
    --num-spec-tokens) NUM_SPEC_TOKENS="$2"; shift 2 ;;
    --help)
      echo "Usage: $0 --model-dir <path> --sif <path> [options]"
      echo ""
      echo "Required:"
      echo "  --model-dir   Path to DeepSeek-V4-Pro-w4a8-mtp model directory (shared filesystem)"
      echo "  --sif         Path to vllm-ascend Apptainer .sif image"
      echo ""
      echo "Optional:"
      echo "  --model-name        Served model name (default: $MODEL_NAME)"
      echo "  --port              API port (default: $PORT)"
      echo "  --num-nodes         Number of compute nodes (default: $NUM_NODES)"
      echo "  --nodelist          Comma-separated node list (default: auto by Slurm)"
      echo "  --partition         Slurm partition (default: $PARTITION)"
      echo "  --work-dir          Working directory on shared fs (default: $WORK_DIR)"
      echo "  --nic               Network interface name (default: $NIC_NAME)"
      echo "  --tp-size           Tensor parallelism size per node (default: $TP_SIZE)"
      echo "  --max-model-len     Max context length (default: $MAX_MODEL_LEN)"
      echo "  --gpu-memory-util   GPU memory utilization (default: $GPU_MEM_UTIL)"
      echo "  --num-spec-tokens   MTP speculative tokens (default: $NUM_SPEC_TOKENS)"
      exit 0 ;;
    *)
      echo "Unknown option: $1"
      exit 1 ;;
  esac
done

# ---- validate ----
if [[ -z "$MODEL_DIR" ]]; then
  echo "ERROR: --model-dir is required"
  exit 1
fi
if [[ -z "$SIF" ]]; then
  echo "ERROR: --sif is required"
  exit 1
fi

# ---- create work directory ----
mkdir -p "$WORK_DIR/logs"
cd "$WORK_DIR"

# ---- generate node.sh ----
cat > "$WORK_DIR/node.sh" << NODESCRIPT
#!/bin/sh

nic_name="$NIC_NAME"
local_ip=\$(hostname -i | awk '{print \$1}')
node0_ip=\$MASTER_ADDR

export HCCL_IF_IP=\$local_ip
export GLOO_SOCKET_IFNAME=\$nic_name
export TP_SOCKET_IFNAME=\$nic_name
export HCCL_SOCKET_IFNAME=\$nic_name
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
  -B \$MODEL_DIR:/model \
  \$VLLM_IMG app-instance

if [ \$SLURM_NODEID == 0 ]; then
  apptainer exec instance://app-instance \\
    vllm serve /model \\
      --served-model-name "\$MODEL_NAME" \\
      --host 0.0.0.0 --port "\$MODEL_PORT" \\
      --data-parallel-size \$SLURM_NNODES \\
      --data-parallel-size-local 1 \\
      --data-parallel-address \$node0_ip \\
      --data-parallel-rpc-port 13389 \\
      --tensor-parallel-size $TP_SIZE \\
      --quantization ascend \\
      --seed 1024 \\
      --enable-expert-parallel \\
      --max-num-seqs 16 \\
      --max-model-len $MAX_MODEL_LEN \\
      --max-num-batched-tokens 4096 \\
      --tokenizer-mode deepseek_v4 \\
      --tool-call-parser deepseek_v4 \\
      --enable-auto-tool-choice \\
      --reasoning-parser deepseek_v4 \\
      --trust-remote-code \\
      --async-scheduling \\
      --enable-prefix-caching \\
      --gpu-memory-utilization $GPU_MEM_UTIL \\
      --safetensors-load-strategy prefetch \\
      --default-chat-template-kwargs '{"thinking": true}' \\
      --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \\
      --additional-config '{"ascend_compilation_config":{"enable_npugraph_ex":true,"enable_static_kernel":false},"enable_cpu_binding":"True"}' \\
      --speculative-config '{"num_speculative_tokens": $NUM_SPEC_TOKENS, "method": "deepseek_mtp"}'
else
  apptainer exec instance://app-instance \\
    vllm serve /model \\
      --served-model-name "\$MODEL_NAME" \\
      --host 0.0.0.0 --port "\$MODEL_PORT" \\
      --headless \\
      --data-parallel-size \$SLURM_NNODES \\
      --data-parallel-size-local 1 \\
      --data-parallel-start-rank \$SLURM_NODEID \\
      --data-parallel-address \$node0_ip \\
      --data-parallel-rpc-port 13389 \\
      --tensor-parallel-size $TP_SIZE \\
      --quantization ascend \\
      --seed 1024 \\
      --enable-expert-parallel \\
      --max-num-seqs 16 \\
      --max-model-len $MAX_MODEL_LEN \\
      --max-num-batched-tokens 4096 \\
      --tokenizer-mode deepseek_v4 \\
      --tool-call-parser deepseek_v4 \\
      --enable-auto-tool-choice \\
      --reasoning-parser deepseek_v4 \\
      --trust-remote-code \\
      --async-scheduling \\
      --enable-prefix-caching \\
      --gpu-memory-utilization $GPU_MEM_UTIL \\
      --safetensors-load-strategy prefetch \\
      --default-chat-template-kwargs '{"thinking": true}' \\
      --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \\
      --additional-config '{"ascend_compilation_config":{"enable_npugraph_ex":true,"enable_static_kernel":false},"enable_cpu_binding":"True"}' \\
      --speculative-config '{"num_speculative_tokens": $NUM_SPEC_TOKENS, "method": "deepseek_mtp"}'
fi
NODESCRIPT
chmod +x "$WORK_DIR/node.sh"

# ---- generate srun.sh ----
NODELIST_ARG=""
if [[ -n "$NODELIST" ]]; then
  NODELIST_ARG="#SBATCH --nodelist=$NODELIST"
fi

cat > "$WORK_DIR/srun.sh" << SRUNSCRIPT
#!/bin/bash
#SBATCH -N $NUM_NODES
#SBATCH --partition=$PARTITION
#SBATCH -J deepseek
#SBATCH -o $WORK_DIR/logs/log_%j.out
#SBATCH -e $WORK_DIR/logs/log_%j.err
#SBATCH --gres=gpu:8
#SBATCH --cpus-per-task=190
$NODELIST_ARG

export LC_CTYPE=C.UTF-8
export MASTER_ADDR=\$(scontrol show hostnames "\$SLURM_JOB_NODELIST" | head -n 1 | hostname -i)
export MODEL_NAME=$MODEL_NAME
export MODEL_PORT=$PORT
export MODEL_DIR=$MODEL_DIR
export VLLM_IMG=$SIF

srun --ntasks-per-node=1 \\
  -o $WORK_DIR/logs/log_%j.%t.out \\
  -e $WORK_DIR/logs/log_%j.%t.err \\
  $WORK_DIR/node.sh
SRUNSCRIPT
chmod +x "$WORK_DIR/srun.sh"

# ---- submit ----
echo "=== Submitting Slurm job ==="
echo "Nodes:       $NUM_NODES"
echo "Model:       $MODEL_DIR"
echo "SIF:         $SIF"
echo "Port:        $PORT"
echo "Work dir:    $WORK_DIR"
echo ""

JOB_OUTPUT=$(sbatch "$WORK_DIR/srun.sh")
echo "$JOB_OUTPUT"

# Extract job ID
JOB_ID=$(echo "$JOB_OUTPUT" | grep -oP '\d+' || true)
if [[ -n "$JOB_ID" ]]; then
  echo ""
  echo "=== Job $JOB_ID submitted ==="
  echo "Monitor: squeue | grep $JOB_ID"
  echo "Logs:    tail -f $WORK_DIR/logs/log_${JOB_ID}.out"
  echo "Stop:    scancel $JOB_ID"
  echo ""
  echo "=== Waiting for server (tail-ing log) ==="
  tail -f "$WORK_DIR/logs/log_${JOB_ID}.out" 2>/dev/null || \
    echo "(log not yet created — run 'squeue' to check status)"
fi
