#!/usr/bin/env bash
set -euo pipefail

# Combined launcher: vLLM OpenAI server (from base image) + Gradio UI.
# Base image: vllm/vllm-openai (we will pin version in Dockerfile).
#
# Environment variables (with defaults):
: "${VLLM_MODEL:=TinyLlama/TinyLlama-1.1B-Chat-v1.0}"
: "${VLLM_HOST:=0.0.0.0}"
: "${VLLM_PORT:=8000}"
: "${GRADIO_PORT:=7860}"
: "${SYSTEM_PROMPT:=You are a helpful assistant. Answer clearly and concisely.}"

echo "[entrypoint] Starting vLLM server"
python3 -m vllm.entrypoints.openai.api_server \
  --model "${VLLM_MODEL}" \
  $VLLM_ARGS &
VLLM_PID=$!

#Wait for some time for VLLM to come up
sleep 30
echo "[entrypoint] vLLM ready"

# Launch Gradio UI
echo "[entrypoint] Starting Gradio UI on port ${GRADIO_PORT}"
export VLLM_MODEL  # ensure chat_ui sees same model
export SYSTEM_PROMPT
python3 /app/chat_ui_nostream.py --port "${GRADIO_PORT}" || {
  echo "[entrypoint] Gradio UI exited with error"
  kill "${VLLM_PID}" 2>/dev/null || true
  exit 1
}

