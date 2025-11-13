#!/usr/bin/env bash
set -euo pipefail

# Start local monitoring stack (backend, Prometheus, Grafana)
# Usage: ./scripts/start_stack.sh [--build]

BUILD=0
ISOLATED=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --build) BUILD=1; shift ;;
    --isolated) ISOLATED=1; shift ;;
    -h|--help) sed -n '1,200p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

compose_dir="infra/compose"
file="${compose_dir}/docker-compose.yml"
if [[ -f "$file" ]]; then
  # Always start local backend first (so Prometheus can scrape it)
  state_dir="data/results/_server_state"
  mkdir -p "$state_dir"
  if (( ISOLATED == 1 )); then
    # Containerized backend; Prometheus scrapes service name inside the compose network
    backend_port=8000
    printf '{"host":"127.0.0.1","port":%s,"started_utc":"%s","existing":false,"mode":"isolated"}\n' "$backend_port" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$state_dir/uvicorn_dashboard.json"
    cat > "$state_dir/prom_targets.json" <<EOF
[
  {"labels": {"job": "app"}, "targets": ["backend:8000"]}
]
EOF
  else
    start_port=8000
    max_tries=11
    chosen_port=""
    for ((i=0; i<max_tries; i++)); do
      p=$((start_port + i))
      if ! (ss -ltn 2>/dev/null | awk '{print $4}' | grep -q ":$p$"); then
        chosen_port="$p"
        break
      fi
    done
    if [[ -z "$chosen_port" ]]; then
      echo "No free port found in range 8000..8010" >&2
      exit 3
    fi
    nohup python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port "$chosen_port" --log-level info >/dev/null 2>&1 &
    printf '{"host":"127.0.0.1","port":%s,"started_utc":"%s","existing":false,"mode":"host"}\n' "$chosen_port" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$state_dir/uvicorn_dashboard.json"

    # Generate Prometheus file_sd target pointing to host backend via host gateway
    host_gateway=172.17.0.1
    if ip -4 addr show docker0 >/dev/null 2>&1; then
      host_gateway=$(ip -4 addr show docker0 | awk '/inet /{print $2}' | cut -d/ -f1 | head -n1)
    fi
    cat > "$state_dir/prom_targets.json" <<EOF
[
  {"labels": {"job": "app"}, "targets": ["${host_gateway}:${chosen_port}"]}
]
EOF
  fi

  pushd "$compose_dir" >/dev/null
  if (( BUILD == 1 )); then
    if (( ISOLATED == 1 )); then
      # Pick a free host port for backend publish
      start_port=8000
      max_tries=11
      host_port=""
      for ((i=0; i<max_tries; i++)); do
        p=$((start_port + i))
        if ! (ss -ltn 2>/dev/null | awk '{print $4}' | grep -q ":$p$"); then
          host_port="$p"
          break
        fi
      done
      : "${host_port:?no free port for backend publish}"
      # Patch dashboard apiBase and links to published host port
      dash_json="$OLDPWD/infra/compose/provisioning/dashboards/json/sma-overview.json"
      if [[ -f "$dash_json" ]]; then
        sed -i "s#http://localhost:8004#http://localhost:${host_port}#g" "$dash_json" || true
      fi
      CPU_POWER_W=${CPU_POWER_W:-60} BACKEND_PORT=$host_port docker compose up -d --build backend prometheus grafana
      # Persist published host port for dashboards/docs
      echo -n "$host_port" > "$OLDPWD/$state_dir/backend_host_port.txt"
    else
      docker compose up -d --build prometheus grafana
    fi
  else
    if (( ISOLATED == 1 )); then
      # Pick a free host port for backend publish
      start_port=8000
      max_tries=11
      host_port=""
      for ((i=0; i<max_tries; i++)); do
        p=$((start_port + i))
        if ! (ss -ltn 2>/dev/null | awk '{print $4}' | grep -q ":$p$"); then
          host_port="$p"
          break
        fi
      done
      : "${host_port:?no free port for backend publish}"
      # Patch dashboard apiBase and links to published host port
      dash_json="$OLDPWD/infra/compose/provisioning/dashboards/json/sma-overview.json"
      if [[ -f "$dash_json" ]]; then
        sed -i "s#http://localhost:8004#http://localhost:${host_port}#g" "$dash_json" || true
      fi
      CPU_POWER_W=${CPU_POWER_W:-60} BACKEND_PORT=$host_port docker compose up -d backend prometheus grafana
      # Persist published host port for dashboards/docs
      echo -n "$host_port" > "$OLDPWD/$state_dir/backend_host_port.txt"
    else
      docker compose up -d prometheus grafana
    fi
  fi
  popd >/dev/null
  if (( ISOLATED == 1 )); then
    echo "Stack started (isolated). Services: backend:${host_port} (container published), prometheus:9090, grafana:3000"
  else
    echo "Stack started. Services: backend:(host) see _server_state/uvicorn_dashboard.json, prometheus:9090, grafana:3000"
  fi
else
  echo "[start_stack] Compose file not found ($file). Falling back to local uvicorn backend only..." >&2
  # Start FastAPI backend on the first available port >= 8000
  start_port=8000
  max_tries=11
  chosen_port=""
  for ((i=0; i<max_tries; i++)); do
    p=$((start_port + i))
    if ! (ss -ltn 2>/dev/null | awk '{print $4}' | grep -q ":$p$"); then
      chosen_port="$p"
      break
    fi
  done
  if [[ -z "$chosen_port" ]]; then
    echo "No free port found in range 8000..8010" >&2
    exit 3
  fi
  # Use nohup to detach and avoid SIGHUP
  nohup python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port "$chosen_port" --log-level info >/dev/null 2>&1 &
  echo "Backend started at http://127.0.0.1:${chosen_port} (uvicorn fallback). Prometheus/Grafana not started."
  # Save state file similar to PowerShell script
  state_dir="data/results/_server_state"
  mkdir -p "$state_dir"
  printf '{"host":"127.0.0.1","port":%s,"started_utc":"%s","existing":false}\n' "$chosen_port" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$state_dir/uvicorn_dashboard.json"
fi
