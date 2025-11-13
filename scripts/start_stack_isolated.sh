#!/usr/bin/env bash
set -euo pipefail

# Wrapper to start the stack in isolated mode (backend container with CPU pinning and memory limit)

DIR="$(cd "$(dirname "$0")" && pwd)"

"${DIR}/start_stack.sh" --build --isolated

echo "Tip: adjust CPU set via docker-compose (cpuset_cpus) or export CPU_POWER_W before running to tune energy proxy."
