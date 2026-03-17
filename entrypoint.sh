#!/bin/sh
set -e

echo "Running database migrations..."
cd / && alembic -c /app/alembic.ini upgrade head

echo "Starting application..."
cd /app
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
