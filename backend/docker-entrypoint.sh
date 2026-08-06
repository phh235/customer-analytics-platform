#!/bin/bash
set -e

echo "Starting Customer Analytics Backend..."

# Chạy Alembic migration
echo "Running database migrations..."
alembic upgrade head || echo "Migration failed or already up to date"

# Start the application
echo "Starting FastAPI application..."
exec "$@"
