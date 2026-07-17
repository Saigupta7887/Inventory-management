#!/bin/sh
set -e

# Apply database migrations, then start the production server.
echo "Running database migrations…"
alembic upgrade head

echo "Starting Gunicorn…"
exec gunicorn -c gunicorn_conf.py app.main:app
