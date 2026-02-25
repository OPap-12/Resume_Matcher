#!/bin/sh
set -e

# Wait for the database to be ready (optional but recommended in some cases)
# We handle connection issues by relying on orchestrated restarts or standard Alembic errors.

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting server..."
exec "$@"
