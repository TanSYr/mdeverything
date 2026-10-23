FROM node:22-slim AS javascript
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
COPY --from=javascript /usr/local/bin/node /usr/local/bin/node
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir ".[transcribe]" \
    && useradd --create-home --uid 10001 mde \
    && mkdir -p /data /models && chown -R mde:mde /data /models
USER mde
ENV MDE_DATA_DIR=/data HF_HOME=/models
EXPOSE 8765
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/api/health')" || exit 1
CMD ["mde", "serve", "--host", "0.0.0.0", "--port", "8765"]
