FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic/alembic.ini .
COPY entrypoint.sh .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app && chmod +x /app/entrypoint.sh
USER appuser

EXPOSE 8000

CMD ["/app/entrypoint.sh"]