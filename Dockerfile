FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

RUN .venv/bin/python -c "\
    from fastembed import TextEmbedding; \
    TextEmbedding('sentence-transformers/all-MiniLM-L6-v2', \
    cache_dir='/app/.fastembed_cache')"


FROM python:3.13-slim AS runtime

RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy venv and model cache from builder
COPY --from=builder /app/.venv .venv
COPY --from=builder /app/.fastembed_cache .fastembed_cache 

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

ENV FASTEMBED_CACHE_PATH="/app/.fastembed_cache"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]