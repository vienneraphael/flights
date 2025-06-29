#!/bin/sh
set -e

exec python -m fastapi run backend/app.py \
    --host 0.0.0.0 \
    --port 8000
