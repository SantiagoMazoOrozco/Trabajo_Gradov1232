#!/usr/bin/env bash
set -euo pipefail

# Quick validation of backend health and key metrics series.
# Usage: ./scripts/test_metrics.sh [--host HOST] [--port PORT]

HOST="127.0.0.1"
PORT=8000
while [[ $# -gt 0 ]]; do
  case "$1" in
    --host) HOST="$2"; shift 2 ;;
    --port) PORT="$2"; shift 2 ;;
    -h|--help) sed -n '1,120p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

BASE="http://${HOST}:${PORT}"
HEALTH_URL="${BASE}/health"
METRICS_URL="${BASE}/metrics"

printf "[test] Checking health %s...\n" "$HEALTH_URL"
if curl -fsS "$HEALTH_URL" >/dev/null; then
  echo "OK health"
else
  echo "FAIL health" >&2; exit 2
fi

printf "[test] Fetching metrics %s...\n" "$METRICS_URL"
METRICS_CONTENT=$(curl -fsS "$METRICS_URL" || true)
if [[ -z "$METRICS_CONTENT" ]]; then
  echo "FAIL metrics empty" >&2; exit 3
fi

missing=()
for name in train_duration_seconds eval_accuracy eval_f1 failures_total recoveries_total; do
  if ! grep -q "$name" <<< "$METRICS_CONTENT"; then
    missing+=("$name")
  fi
done

if (( ${#missing[@]} > 0 )); then
  echo "WARN missing series: ${missing[*]}" >&2
else
  echo "All expected series present"
fi

# Basic Prometheus exposition format sanity
if ! grep -q '^# HELP' <<< "$METRICS_CONTENT"; then
  echo "WARN no HELP lines found" >&2
fi

echo "[test] Done"
