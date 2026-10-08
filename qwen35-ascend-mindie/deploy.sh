#!/usr/bin/env bash
set -euo pipefail

# deploy.sh — Deploy Qwen3.5-35B on Ascend with MindIE inference engine
#
# Usage:
#   bash deploy.sh /data/models/Qwen3.5-35B-Instruct [model_name] [world_size] [port] [max_seq_len]
#
# Examples:
#   bash deploy.sh /data/models/Qwen3.5-35B-Instruct
#   bash deploy.sh /data/models/Qwen3.5-35B-A3B qwen35-moe 2 1025 8192
#
# Environment:
#   Assumes MindIE is installed at /usr/local/Ascend/mindie/latest/

MODEL_PATH="${1:-}"
MODEL_NAME="${2:-qwen35}"
WORLD_SIZE="${3:-4}"            # 4 cards for 35B Dense, 2-4 for MoE
PORT="${4:-1025}"
MAX_SEQ_LEN="${5:-8192}"
MINDIE_DIR="/usr/local/Ascend/mindie/latest/mindie-service"
CONF_DIR="$MINDIE_DIR/conf"

# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------

if [[ -z "$MODEL_PATH" ]]; then
  echo "Usage: $0 <model_path> [model_name] [world_size] [port] [max_seq_len]"
  echo ""
  echo "  model_path  — Absolute path to model weights (required)"
  echo "  model_name  — Served model name (default: qwen35)"
  echo "  world_size  — Tensor parallelism (default: 4, recommended: 4 for 35B)"
  echo "  port        — API port (default: 1025)"
  echo "  max_seq_len — Max sequence length (default: 8192)"
  exit 1
fi

if [[ ! -d "$MODEL_PATH" ]]; then
  echo "[ERROR] Model path not found: $MODEL_PATH"
  exit 1
fi

if [[ ! -f "$MODEL_PATH/config.json" ]]; then
  echo "[WARN] No config.json found at $MODEL_PATH — model directory may be incomplete"
fi

if [[ ! -d "$MINDIE_DIR" ]]; then
  echo "[ERROR] MindIE not found at $MINDIE_DIR"
  echo "  Install MindIE first or check the path."
  exit 1
fi

# ---------------------------------------------------------------------------
# Step 1: Source environment scripts
# ---------------------------------------------------------------------------

echo ""
echo "============================================================"
echo "  Qwen3.5-35B — MindIE Deployment"
echo "============================================================"
echo ""
echo "Model:    $MODEL_PATH"
echo "Name:     $MODEL_NAME"
echo "World:    $WORLD_SIZE (cards)"
echo "Port:     $PORT"
echo "MaxSeq:   $MAX_SEQ_LEN"
echo ""

ENV_SCRIPTS=(
  "/usr/local/Ascend/ascend-toolkit/set_env.sh"
  "/usr/local/Ascend/nnal/atb/set_env.sh"
  "/usr/local/Ascend/atb-models/set_env.sh"
  "/usr/local/Ascend/mindie/set_env.sh"
  "/usr/local/Ascend/mindie/latest/mindie-service/set_env.sh"
)

for script in "${ENV_SCRIPTS[@]}"; do
  if [[ -f "$script" ]]; then
    source "$script"
    echo "[OK] Sourced: $script"
  else
    echo "[WARN] Not found: $script"
  fi
done

# ---------------------------------------------------------------------------
# Step 2: Set environment variables (user-provided optimized config)
# ---------------------------------------------------------------------------

echo ""
echo "--- Setting environment variables ---"

export LD_PRELOAD="${LD_PRELOAD:-}:/usr/lib64/libjemalloc.so.2"
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

echo "[OK] Environment variables set"

# ---------------------------------------------------------------------------
# Step 3: Generate conf/config.json
# ---------------------------------------------------------------------------

mkdir -p "$CONF_DIR"

# Build NPU device IDs based on worldSize
NPU_IDS="["
for ((i=0; i<WORLD_SIZE; i++)); do
  [[ $i -gt 0 ]] && NPU_IDS+=", "
  NPU_IDS+="$i"
done
NPU_IDS+="]"

cat > "$CONF_DIR/config.json" << CONFEOF
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
    "port": $PORT,
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
    "npuDeviceIds": [[$NPU_IDS]],
    "tokenizerProcessNumber": 8,
    "ModelDeployConfig": {
      "maxSeqLen": $MAX_SEQ_LEN,
      "maxInputTokenLen": $MAX_SEQ_LEN,
      "truncation": false,
      "ModelConfig": [{
        "modelName": "$MODEL_NAME",
        "modelInstanceType": "Standard",
        "modelWeightPath": "$MODEL_PATH",
        "worldSize": $WORLD_SIZE,
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
CONFEOF

echo "[OK] Generated $CONF_DIR/config.json"

# ---------------------------------------------------------------------------
# Step 4: Kill existing mindieservice_daemon if running
# ---------------------------------------------------------------------------

if pgrep -f mindieservice_daemon > /dev/null 2>&1; then
  echo "[INFO] Stopping existing mindieservice_daemon..."
  pkill -f mindieservice_daemon || true
  sleep 3
fi

# ---------------------------------------------------------------------------
# Step 5: Start the service
# ---------------------------------------------------------------------------

cd "$MINDIE_DIR"

echo ""
echo "--- Starting mindieservice_daemon ---"
echo "Logs: $MINDIE_DIR/output.log"
echo ""

nohup ./bin/mindieservice_daemon > output.log 2>&1 &
PID=$!
echo "$PID" > mindie.pid
echo "[OK] Started PID: $PID"

echo ""
echo "--- Waiting for service to become ready ---"
echo "(This may take 5-15 minutes on first launch for NPU graph compilation)"
echo ""

# Poll for startup (max 900s = 15 min)
MAX_WAIT=900
INTERVAL=30
ELAPSED=0
READY=false

while [[ $ELAPSED -lt $MAX_WAIT ]]; do
  # Check if process is alive
  if ! kill -0 $PID 2>/dev/null; then
    echo "[ERROR] Process died unexpectedly. Check logs:"
    tail -30 "$MINDIE_DIR/output.log"
    exit 1
  fi

  # Check for ready markers in log
  if grep -q "Start server success\|listening on\|gRPC server started\|Server start" "$MINDIE_DIR/output.log" 2>/dev/null; then
    READY=true
    break
  fi

  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))
  echo "  ... waited ${ELAPSED}s / ${MAX_WAIT}s"
done

echo ""

if [[ "$READY" == "true" ]]; then
  echo "============================================================"
  echo "  Service is READY!"
  echo "============================================================"
  echo ""
  echo "API Endpoint:  http://127.0.0.1:$PORT/v1/chat/completions"
  echo "Model:         $MODEL_NAME"
  echo "PID:           $PID"
  echo ""
  echo "Tail logs:     tail -f $MINDIE_DIR/output.log"
  echo "Stop service:  pkill -f mindieservice_daemon"
  echo ""
  echo "--- Test the API ---"
  echo "curl -X POST http://127.0.0.1:$PORT/v1/chat/completions \\"
  echo "  -H \"Content-Type: application/json\" \\"
  echo '  -d '\''{"model": "'"$MODEL_NAME"'", "messages": [{"role":"user","content":"你好"}]}'\'''
  echo ""
else
  echo "[WARN] Timeout reached ($MAX_WAIT s). Process is still running but not yet ready."
  echo "  Check logs: tail -f $MINDIE_DIR/output.log"
  echo "  The first compilation may take longer. Consider increasing MAX_WAIT."
fi
