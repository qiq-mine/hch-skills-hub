#!/usr/bin/env bash
set -euo pipefail

# deploy.sh — Deploy DeepSeek-V4-Flash on Ascend (single node) with vllm-ascend
#
# Usage:
#   ./deploy.sh \
#     --model /path/to/DeepSeek-V4-Flash-w8a8-mtp \
#     --image quay.io/ascend/vllm-ascend:deepseekv4-a3 \
#     --port 8008 \
#     --model-name dsv4

# ---- defaults ----
MODEL=""
IMAGE=""
PORT=8008
MODEL_NAME="dsv4"
GPU_MEM_UTIL=0.9
MAX_MODEL_LEN=1024000
TP_SIZE=4
DP_SIZE=4
NUM_SPEC_TOKENS=1
OMP_NUM_THREADS=10
CONTAINER_NAME="vllm-ascend-dsv4"

# ---- parse args ----
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)        MODEL="$2";        shift 2 ;;
    --image)        IMAGE="$2";        shift 2 ;;
    --port)         PORT="$2";         shift 2 ;;
    --model-name)   MODEL_NAME="$2";   shift 2 ;;
    --gpu-memory-util) GPU_MEM_UTIL="$2"; shift 2 ;;
    --max-model-len) MAX_MODEL_LEN="$2"; shift 2 ;;
    --tp-size)      TP_SIZE="$2";      shift 2 ;;
    --dp-size)      DP_SIZE="$2";      shift 2 ;;
    --num-spec-tokens) NUM_SPEC_TOKENS="$2"; shift 2 ;;
    --omp-threads)  OMP_NUM_THREADS="$2"; shift 2 ;;
    --container-name) CONTAINER_NAME="$2"; shift 2 ;;
    --help)
      echo "Usage: $0 --model <path> --image <docker-tag> [options]"
      echo ""
      echo "Required:"
      echo "  --model       Path to DeepSeek-V4-Flash-w8a8-mtp model directory"
      echo "  --image       Docker image tag (e.g. quay.io/ascend/vllm-ascend:deepseekv4-a3)"
      echo ""
      echo "Optional:"
      echo "  --port                  Port for OpenAI-compatible API (default: $PORT)"
      echo "  --model-name            Served model name (default: $MODEL_NAME)"
      echo "  --gpu-memory-util       GPU memory utilization 0-1 (default: $GPU_MEM_UTIL)"
      echo "  --max-model-len         Maximum context length (default: $MAX_MODEL_LEN)"
      echo "  --tp-size               Tensor parallelism degree (default: $TP_SIZE)"
      echo "  --dp-size               Data parallelism degree (default: $DP_SIZE)"
      echo "  --num-spec-tokens       MTP speculative tokens (default: $NUM_SPEC_TOKENS)"
      echo "  --omp-threads           OMP_NUM_THREADS (default: $OMP_NUM_THREADS)"
      echo "  --container-name        Docker container name (default: $CONTAINER_NAME)"
      exit 0 ;;
    *)
      echo "Unknown option: $1"
      exit 1 ;;
  esac
done

# ---- validate ----
if [[ -z "$MODEL" ]]; then
  echo "ERROR: --model is required"
  exit 1
fi
if [[ -z "$IMAGE" ]]; then
  echo "ERROR: --image is required"
  exit 1
fi
if [[ ! -d "$MODEL" ]]; then
  echo "ERROR: model directory not found: $MODEL"
  exit 1
fi

# ---- detect A2 vs A3 from image tag ----
if echo "$IMAGE" | grep -q -- '-a3'; then
  ASCEND_A3_ENABLE=1
  HCCL_BUFFSIZE=1024
  A3_FLAG=1
  MULTI_BLOCK_POOL=1
else
  ASCEND_A3_ENABLE=0
  HCCL_BUFFSIZE=512
  A3_FLAG=0
  MULTI_BLOCK_POOL=1
fi

# ---- build device flags ----
DAVINCI_DEVS=""
for i in $(seq 0 15); do
  DAVINCI_DEVS="$DAVINCI_DEVS --device /dev/davinci$i"
done

# ---- stop existing container ----
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

# ---- launch container ----
echo "=== Launching $CONTAINER_NAME ==="
docker run --rm -d \
  --name "$CONTAINER_NAME" \
  --net=host \
  --shm-size=512g \
  $DAVINCI_DEVS \
  --device /dev/davinci_manager \
  --device /dev/devmm_svm \
  --device /dev/hisi_hdc \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
  -v "$MODEL":/model \
  "$IMAGE" \
  bash -c "
set -euo pipefail

# Environment tuning
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=$OMP_NUM_THREADS
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export ACL_OP_INIT_MODE=1
export USE_MULTI_GROUPS_KV_CACHE=1
export USE_MULTI_BLOCK_POOL=$MULTI_BLOCK_POOL
export HCCL_BUFFSIZE=$HCCL_BUFFSIZE
export VLLM_ASCEND_ENABLE_FLASHCOMM1=1
export VLLM_ENGINE_READY_TIMEOUT_S=3600

if [ \"$ASCEND_A3_ENABLE\" = 1 ]; then
  export ASCEND_A3_ENABLE=1
  export VLLM_ASCEND_ENABLE_FUSED_MC2=1
fi

# Launch server
vllm serve /model \
  --enable-prefix-caching \
  --max_model_len $MAX_MODEL_LEN \
  --max-num-batched-tokens 8192 \
  --served-model-name $MODEL_NAME \
  --gpu-memory-utilization $GPU_MEM_UTIL \
  --api-server-count 1 \
  --max-num-seqs 16 \
  --data-parallel-size $DP_SIZE \
  --tensor-parallel-size $TP_SIZE \
  --enable-expert-parallel \
  --tokenizer-mode deepseek_v4 \
  --tool-call-parser deepseek_v4 \
  --enable-auto-tool-choice \
  --reasoning-parser deepseek_v4 \
  --safetensors-load-strategy prefetch \
  --quantization ascend \
  --speculative-config '{\"num_speculative_tokens\": $NUM_SPEC_TOKENS, \"method\": \"deepseek_mtp\"}' \
  --port $PORT \
  --block-size 128 \
  --compilation-config '{\"cudagraph_mode\": \"FULL_DECODE_ONLY\"}' \
  --async-scheduling
"

echo ""
echo "=== Server starting (container: $CONTAINER_NAME) ==="
echo "API endpoint: http://<host-ip>:$PORT/v1"
echo "Model name:   $MODEL_NAME"
echo ""
echo "Tail logs:   docker logs -f $CONTAINER_NAME"
echo "Stop server: docker stop $CONTAINER_NAME"
echo ""
echo "=== Test with curl ==="
echo "curl http://localhost:$PORT/v1/chat/completions \\"
echo "  -H \"Content-Type: application/json\" \\"
echo '  -d '\''{"model": "'"$MODEL_NAME"'", "messages": [{"role":"user","content":"Hello"}]}'\'''
