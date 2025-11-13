#!/usr/bin/env bash
set -euo pipefail

# Export selected Grafana panels as PNG images into docs/figures/
# Requirements: grafana-image-renderer plugin installed and Grafana running on localhost:3000
# Auth: uses basic auth admin:admin by default (adjust via env vars)

GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
GRAFANA_USER="${GRAFANA_USER:-admin}"
GRAFANA_PASS="${GRAFANA_PASS:-admin}"
DASH_UID="${DASH_UID:-sma-overview}"
DASH_SLUG="${DASH_SLUG:-SMA%20Overview}"
FROM="${FROM:-now-1h}"
TO="${TO:-now}"
V_JOB="${V_JOB:-app}"
OUT_DIR="${OUT_DIR:-docs/figures}"
WIDTH="${WIDTH:-1200}"
HEIGHT="${HEIGHT:-600}"

mkdir -p "$OUT_DIR"

render_panel() {
  local panel_id="$1"; shift
  local name="$1"; shift
  local url="${GRAFANA_URL}/render/d-solo/${DASH_UID}/${DASH_SLUG}?panelId=${panel_id}&from=${FROM}&to=${TO}&var-job=${V_JOB}&width=${WIDTH}&height=${HEIGHT}&tz=UTC"
  echo "Exporting panel ${panel_id} -> ${OUT_DIR}/${name}.png"
  curl -fsS -u "${GRAFANA_USER}:${GRAFANA_PASS}" -o "${OUT_DIR}/${name}.png" "$url"
}

# Example panels from sma-overview.json (adjust if you change the dashboard):
# 97: Live Avg Watts (timeseries)
# 98: Live Records/s (timeseries)
# 20: CPU % (avg last train)
# 23: Avg Watts (last train)
# 61: Avg Watts (last train) - timeseries
# 62: Watts/MB (last train) - timeseries

render_panel 97 live_avg_watts
render_panel 98 live_records_per_s
render_panel 20 cpu_avg_last_train
render_panel 23 avg_watts_last_train
render_panel 61 avg_watts_last_train_ts
render_panel 62 watts_per_mb_last_train_ts

echo "Images written into ${OUT_DIR}/"
