# Docker image combining vLLM OpenAI server (prebuilt) + Gradio UI.
# Uses official vLLM OpenAI image pinned to 0.2.7 for older GPU compatibility.
FROM vllm/vllm-openai:v0.2.7

# Environment defaults (override at runtime with -e ...)
ENV VLLM_MODEL=TinyLlama/TinyLlama-1.1B-Chat-v1.0 \
    VLLM_HOST=0.0.0.0 \
    VLLM_PORT=8000 \
    GRADIO_PORT=7860 \
    SYSTEM_PROMPT="You are a helpful assistant. Answer clearly and concisely."

RUN apt-get update && \
    apt-get install -y --no-install-recommends runit
ENV MODEL_PATH=/models/SmolLM2-135M-hf

ADD runit_folder/api_server /var/runit/api_server
RUN sed -i 's/\r$//g' /var/runit/api_server/run
RUN chmod +x /var/runit/api_server/run
ENV SVDIR=/var/runit
ENV WORKER_TIMEOUT=3600
EXPOSE 5001
# (Optional) set HF token at runtime:
#   -e HUGGING_FACE_HUB_TOKEN=hf_xxx

# Install only UI/client deps (vLLM already in base image).
# Avoid re-installing vllm pinned in requirements.txt to keep layers small.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        openai==1.34.0 \
        gradio \
        httpx==0.27.0

WORKDIR /app

# Copy application files
COPY chat_ui.py chat_ui_nostream.py  entrypoint.sh  ./

# Ensure entrypoint is executable
RUN chmod +x /app/entrypoint.sh 

# Expose both the vLLM API port and Gradio UI port
EXPOSE 8000 7860


# Start combined services (vLLM + UI)
#ENTRYPOINT ["/app/entrypoint.sh"]

ENTRYPOINT [ "runsvdir", "/var/runit" ]
