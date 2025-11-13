#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_root"

# Aggregate metrics across experiments
if [[ ! -f python-analysis/aggregate_metrics.py ]]; then
  echo "python-analysis/aggregate_metrics.py not found" >&2
  exit 2
fi

python3 python-analysis/aggregate_metrics.py --root data/results --output data/results/aggregate_metrics.csv "$@"
