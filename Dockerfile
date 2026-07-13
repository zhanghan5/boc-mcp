FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

RUN pip install uv
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN uv pip install --python /usr/local/bin/python --system -e "."

FROM python:3.12-slim AS runtime

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BOC_MCP__HOST=0.0.0.0 \
    BOC_MCP__PORT=8000

RUN groupadd --gid 10001 boc && useradd --uid 10001 --gid boc --create-home boc
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --chown=boc:boc src/ ./src/
COPY --chown=boc:boc config/ ./config/
COPY --chown=boc:boc pyproject.toml README.md ./

USER boc
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz',timeout=3).status==200 else 1)"

CMD ["python", "-m", "boc_mcp"]