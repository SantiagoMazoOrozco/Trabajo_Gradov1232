#!/usr/bin/env bash
set -euo pipefail

# Simple single experiment runner (Linux equivalent of run_experiment.ps1)
# Usage:
#   ./scripts/run_experiment.sh [--group treatment|control] [--id EXP_ID] [--monitor-seconds N] [--report]
# If EXP_ID is omitted an auto id is generated.

GROUP="treatment"
EXP_ID=""
MONITOR_SECONDS=0
REPORT=0
SEED=${SEED:-42}

now_ts() { date +"%Y%m%d_%H%M%S"; }
auto_id() { echo "exp_$(now_ts)"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --group) GROUP="$2"; shift 2 ;;
    --id) EXP_ID="$2"; shift 2 ;;
    --monitor-seconds) MONITOR_SECONDS="$2"; shift 2 ;;
    --report) REPORT=1; shift ;;
    -h|--help)
      sed -n '1,200p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$EXP_ID" ]]; then
  EXP_ID="$(auto_id)"
fi

echo "[run_experiment] id=$EXP_ID group=$GROUP monitor_seconds=$MONITOR_SECONDS report=$REPORT"

# Choose python interpreter
choose_python() {
  if command -v python >/dev/null 2>&1; then echo python; return; fi
  if command -v python3 >/dev/null 2>&1; then echo python3; return; fi
  echo python
}
PY=$(choose_python)

SCRIPT=python-analysis/simulate_experiment.py
if [[ ! -f "$SCRIPT" ]]; then
  echo "Missing $SCRIPT" >&2; exit 2
fi

# Discover backend port from state file if present and set API_BASE for python clients
STATE_FILE="data/results/_server_state/uvicorn_dashboard.json"
API_HOST="127.0.0.1"
API_PORT="${API_PORT:-}"
if [[ -f "$STATE_FILE" && -z "${API_PORT}" ]]; then
  DETECTED_PORT=$(grep -o '"port"\s*:\s*[0-9]\+' "$STATE_FILE" | grep -o '[0-9]\+' | head -n1 || true)
  if [[ -n "${DETECTED_PORT:-}" ]]; then API_PORT="$DETECTED_PORT"; fi
fi
if [[ -z "${API_PORT:-}" ]]; then API_PORT=8000; fi
export API_BASE="http://${API_HOST}:${API_PORT}"

"$PY" "$SCRIPT" "$EXP_ID" "$SEED" --group "$GROUP"

if (( MONITOR_SECONDS > 0 )); then
  echo "[monitor] capturing metrics for $MONITOR_SECONDS seconds"
  PY_MON=python-analysis/monitor_run.py
  if [[ -f "$PY_MON" ]]; then
    "$PY" "$PY_MON" "$EXP_ID" --duration "$MONITOR_SECONDS"
  else
    echo "monitor_run.py not found, skipping monitoring" >&2
  fi
fi

if (( REPORT == 1 )); then
  PY_REP=python-analysis/report_run.py
  if [[ -f "$PY_REP" ]]; then
    "$PY" "$PY_REP" "$EXP_ID"
  else
    echo "report_run.py not found, skipping report" >&2
  fi
fi

echo "[done] experiment $EXP_ID"

