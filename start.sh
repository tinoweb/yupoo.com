#!/bin/bash

# Use PORT from environment or default to 8000
PORT="${PORT:-8000}"

# Start uvicorn with the port
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --proxy-headers --forwarded-allow-ips='*'
