#!/usr/bin/env bash
export PYTHONUNBUFFERED=1

if [ -f ".env" ]; then
set -a
. ./.env
set +a
fi
uvicorn app.main:app --host 0.0.0.0 --port 8000 -reload