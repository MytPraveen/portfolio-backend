#!/bin/sh

set -e

if [ -f /vault/secrets/db ]; then
    echo "Loading Vault secrets..."
    set -a
    . /vault/secrets/db
    set +a
fi

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000
