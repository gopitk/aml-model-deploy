FROM vllm/vllm-openai:latest

# runit package is expected to be installed in the container by Azure ML
RUN apt-get update && \
    apt-get install -y --no-install-recommends runit
ENV MODEL_PATH /models/SmolLM2-135M-hf

ADD runit_folder/api_server /var/runit/api_server
# "run" script will launch the inference server
RUN chmod +x /var/runit/api_server/run
ENV SVDIR=/var/runit
ENV WORKER_TIMEOUT=3600
EXPOSE 5001
ENTRYPOINT [ "runsvdir", "/var/runit" ]

