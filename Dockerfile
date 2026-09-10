FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system agentiq && adduser --system --ingroup agentiq agentiq

COPY pyproject.toml README.md ./
COPY agentiq ./agentiq

RUN pip install --no-cache-dir .

USER agentiq
EXPOSE 8000

CMD ["uvicorn", "agentiq.api:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
