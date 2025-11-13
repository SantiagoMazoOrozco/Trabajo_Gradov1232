#!/usr/bin/env bash
set -euo pipefail

# Quick smoke to validate monitoring stack
# - Starts stack
# - Waits for backend health
# - Runs a couple of quick experiments
# - Aggregates and runs stats

API_HOST=${API_HOST:-127.0.0.1}
API_PORT=${API_PORT:-8000}
HEALTH_URL="http://${API_HOST}:${API_PORT}/health"

HEALTH_URL="http://${API_HOST}:${API_PORT}/health"
# Start stack (no rebuild by default)
./scripts/start_stack.sh

# If backend started on a non-default port, detect it from state file and override API_PORT locally
STATE_FILE="data/results/_server_state/uvicorn_dashboard.json"
if [[ -f "$STATE_FILE" ]]; then
  DETECTED_PORT=$(grep -o '"port"\s*:\s*[0-9]\+' "$STATE_FILE" | grep -o '[0-9]\+' | head -n1 || true)
  if [[ -n "${DETECTED_PORT:-}" ]]; then
    API_PORT="$DETECTED_PORT"
    echo "Detected backend port from state: $API_PORT"
  fi
fi

HEALTH_URL="http://${API_HOST}:${API_PORT}/health"
echo "Waiting for backend health at ${HEALTH_URL} ..."
for i in {1..60}; do
  if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
    echo "Backend is healthy"
    break
  fi
  sleep 1
  if [[ $i -eq 60 ]]; then
    echo "Backend did not become healthy in time" >&2
    exit 3
  fi
done

# Run minimal workload to generate metrics
bash scripts/run_experiment.sh --group control --monitor-seconds 10 --report || true
bash scripts/run_experiment.sh --group treatment --monitor-seconds 10 --report || true

# Aggregate and stats
bash scripts/aggregate_metrics.sh || true
bash scripts/stats_analysis.sh || true

echo "Smoke done. You can check Grafana at http://localhost:3000 (admin/admin)."
