#!/usr/bin/env bash
set -euo pipefail

# Stop local monitoring stack
# Usage: ./scripts/stop_stack.sh

compose_dir="infra/compose"
file="${compose_dir}/docker-compose.yml"
if [[ ! -f "$file" ]]; then
  echo "Compose file not found: $file" >&2
  exit 2
fi

pushd "$compose_dir" >/dev/null
# Graceful shutdown
docker compose down
popd >/dev/null

echo "Stack stopped."
