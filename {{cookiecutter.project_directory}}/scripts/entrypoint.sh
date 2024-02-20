#!/bin/sh

set -e

# Check connections
python ./src/pre_start.py

# Set default value for environment variable
: "${APP_ENVIRONMENT:=development}"
: "${SERVER:=false}"
: "${SERVER_WORKER:=1}"
: "${PORT:=8888}"

# Metadata
echo "###########################################################"
echo "ENVIRONMENT: ${APP_ENVIRONMENT}"
# Start server if SERVER environment variable is set
echo "SERVER: ${SERVER}"
if [ "${SERVER}" = "true" ]; then
    echo "PORT: ${PORT}"
    echo "SERVER_WORKER: ${SERVER_WORKER}"
fi

echo "###########################################################"

# If SERVER environment variable is set, run uvicorn command
if [ "${SERVER}" = "true" ]; then
    echo "Starting uvicorn server..."
    exec uvicorn src.main:app --host=0.0.0.0 --port=${PORT} --workers=${SERVER_WORKER}
fi

# Evaluating passed command:
exec "$@"
