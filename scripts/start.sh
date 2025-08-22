#!/usr/bin/env bash
set -euo pipefail

# Apply database migrations
echo "Running database migrations..."
#alembic upgrade head

# Start the application (Cloud Run provides $PORT)
PORT="${PORT:-8000}"
WORKERS="${WEB_CONCURRENCY:-1}"
THREADS="${WEB_THREADS:-1}"

echo "Starting server on 0.0.0.0:${PORT} with ${WORKERS} workers..."
exec gunicorn -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:${PORT} \
  --workers ${WORKERS} \
  --threads ${THREADS} \
  src.main:app


