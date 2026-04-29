FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

RUN addgroup --system mcpgroup && adduser --system --ingroup mcpgroup mcpuser

COPY --from=builder /install /usr/local
COPY . .

RUN mkdir -p logs && chown -R mcpuser:mcpgroup /app

USER mcpuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
