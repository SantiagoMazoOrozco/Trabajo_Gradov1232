#!/usr/bin/env bash#!/usr/bin/env bash

set -euo pipefail# Linux batch: run control vs treatment N times, aggregate and run stats

set -euo pipefail

# Batch runner (Linux equivalent of run_batch.ps1)

# Usage: ./scripts/run_batch.sh [--repeats N] [--monitor-seconds N]repo_root="$(cd "$(dirname "$0")/.." && pwd)"

# Runs control and treatment groups N times each.cd "$repo_root"



REPEATS=${REPEATS:-10}REPEATS=${REPEATS:-10}

MONITOR_SECONDS=${MONITOR_SECONDS:-60}SEED_BASE=${SEED_BASE:-42}

API_HOST=${API_HOST:-127.0.0.1}

while [[ $# -gt 0 ]]; doAPI_PORT=${API_PORT:-8000}

  case "$1" inMONITOR_SECONDS=${MONITOR_SECONDS:-0}

    --repeats) REPEATS="$2"; shift 2 ;;

    --monitor-seconds) MONITOR_SECONDS="$2"; shift 2 ;;# ensure venv

    -h|--help)if [[ ! -d .venv ]]; then

      sed -n '1,25p' "$0"; exit 0 ;;  python3 -m venv .venv

    *) echo "Unknown arg: $1" >&2; exit 1 ;;fi

  esacsource .venv/bin/activate

donepython3 -m pip install --upgrade pip >/dev/null

if [[ -f requirements.txt ]]; then

echo "[run_batch] repeats=$REPEATS monitor_seconds=$MONITOR_SECONDS"  pip install -r requirements.txt >/dev/null

fi

for GROUP in control treatment; do

  for ((i=1; i<=REPEATS; i++)); do# start API if needed

    echo "--- $GROUP run $i/$REPEATS ---"health_url="http://${API_HOST}:${API_PORT}/health"

    ./scripts/run_experiment.sh --group "$GROUP" --monitor-seconds "$MONITOR_SECONDS" --report || {if ! curl -fsS "$health_url" >/dev/null 2>&1; then

      echo "Run failed for $GROUP $i" >&2  echo "+ starting API at ${API_HOST}:${API_PORT}"

    }  ( PYTHONUNBUFFERED=1 python3 -m uvicorn backend.api.main:app --host "$API_HOST" --port "$API_PORT" --log-level warning >/dev/null 2>&1 & echo $! > .api_pid )

  done  for i in {1..30}; do

done    if curl -fsS "$health_url" >/dev/null 2>&1; then break; fi

    sleep 1

# Aggregate metrics  done

if [[ -f python-analysis/aggregate_metrics.py ]]; thenfi

  python python-analysis/aggregate_metrics.py || true

firun_one() {

  local group="$1"; shift

# Stats analysis  local seed="$1"; shift

if [[ -f python-analysis/stats_analysis.py ]]; then  local id="${group}_$(date +%Y%m%d_%H%M%S_%N)"

  python python-analysis/stats_analysis.py || true  API_BASE="http://${API_HOST}:${API_PORT}" python3 python-analysis/simulate_experiment.py "$id" "$seed"

fi}



echo "[done] batch"echo "Batch: $REPEATS repeticiones por grupo (control vs treatment)"

for ((i=1; i<=REPEATS; i++)); do
  seed=$((SEED_BASE + i))
  echo "[$i/$REPEATS] control (seed=$seed)"
  run_one control "$seed"
  sleep 1
  seed=$((SEED_BASE + 1000 + i))
  echo "[$i/$REPEATS] treatment (seed=$seed)"
  run_one treatment "$seed"
  sleep 1
done

# aggregate and stats
python3 python-analysis/aggregate_metrics.py
python3 python-analysis/stats_analysis.py

echo "Batch listo. Ver data/results/aggregate_metrics.csv y stats_summary.*"

# stop API if started
if [[ -f .api_pid ]]; then
  pid=$(cat .api_pid || true)
  if [[ -n "${pid:-}" ]] && ps -p "$pid" >/dev/null 2>&1; then
    kill "$pid" || true
  fi
  rm -f .api_pid
fi
