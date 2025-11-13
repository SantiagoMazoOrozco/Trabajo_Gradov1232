#!/usr/bin/env bash
set -euo pipefail

# Kill uvicorn backend process started from this repo (best-effort).

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Try to kill by module name
pids=$(pgrep -f "uvicorn\s+backend\.api\.main:app" || true)
if [[ -n "${pids}" ]]; then
  echo "Killing uvicorn by module match: ${pids}"
  kill ${pids} 2>/dev/null || true
  sleep 1
fi

# Also try to kill any python process holding a port from state file
STATE_FILE="${ROOT_DIR}/data/results/_server_state/uvicorn_dashboard.json"
if [[ -f "$STATE_FILE" ]]; then
  port=$(grep -o '"port"\s*:\s*[0-9]\+' "$STATE_FILE" | grep -o '[0-9]\+' | head -n1 || true)
  if [[ -n "${port}" ]]; then
    echo "Attempting to kill process listening on :$port"
    pid=$(ss -ltnp 2>/dev/null | awk -v p=":$port" '$4 ~ p {print $6}' | sed 's/.*,pid=\([0-9]\+\),.*/\1/' | head -n1)
    if [[ -n "${pid}" ]]; then
      kill "$pid" 2>/dev/null || true
      sleep 1
    fi
  fi
fi

echo "Backend kill attempt done."
