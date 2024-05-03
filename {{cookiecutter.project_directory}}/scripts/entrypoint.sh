#!/bin/sh

set -e

# Check connections
python ./src/pre_start.py

# Set default value for environment variable
: "${ENVIRONMENT:=development}"
: "${SERVER:=false}"
: "${SERVER_WORKER:=1}"
: "${PORT:=8888}"
: "${WORKER:=false}"
: "${WORKER_CONCURRENCY:=1}"

# Metadata
echo "###########################################################"
echo "ENVIRONMENT: ${ENVIRONMENT}"
# Start server if SERVER environment variable is set
echo "SERVER: ${SERVER}"
if [ "${SERVER}" = "true" ]; then
    echo "PORT: ${PORT}"
    echo "SERVER_WORKER: ${SERVER_WORKER}"
fi

echo "WORKER: ${WORKER}"
if [ "${WORKER}" = "true" ]; then
    echo "WORKER_CONCURRENCY: ${WORKER_CONCURRENCY}"
fi

echo "###########################################################"

# If SERVER environment variable is set, run uvicorn command
if [ "${SERVER}" = "true" ]; then
    echo "Starting uvicorn server..."
    exec uvicorn src.main:app --host=0.0.0.0 --port=${PORT} --workers=${SERVER_WORKER}
fi

# If WORKER environment variable is set, run celery command
if [ "${WORKER}" = "true" ]; then
    echo "Starting celery worker..."
    exec celery -A src.main.celery worker --loglevel=INFO --concurrency=${WORKER_CONCURRENCY} -E --without-heartbeat --without-mingle --without-gossip -Ofair
fi

# Evaluating passed command:
exec "$@"
