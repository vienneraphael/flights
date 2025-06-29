#!/bin/sh
set -e

exec python -m fastapi run backend/main.py \
    --host 0.0.0.0 \
    --port 8000
