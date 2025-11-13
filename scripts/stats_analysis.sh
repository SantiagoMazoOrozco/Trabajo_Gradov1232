#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_root"

# Statistical analysis of aggregated metrics
if [[ ! -f python-analysis/stats_analysis.py ]]; then
  echo "python-analysis/stats_analysis.py not found" >&2
  exit 2
fi

python3 python-analysis/stats_analysis.py --csv data/results/aggregate_metrics.csv --outdir data/results --permutations "${PERMUTATIONS:-5000}" "$@"
