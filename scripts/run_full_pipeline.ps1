param(
  [string]$ExperimentPrefix = "exp_jade_batch",
  [int]$Repeats = 5,
  [int]$SeedBase = 100,
  [string]$ApiHost = "127.0.0.1",
  [int]$ApiPort = 8001
)

$ErrorActionPreference = 'Stop'

# 1) Run batch
Write-Host "==> Running batch: $Repeats runs (prefix=$ExperimentPrefix)"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_jade_batch.ps1 -ExperimentPrefix $ExperimentPrefix -Repeats $Repeats -SeedBase $SeedBase -ApiHost $ApiHost -ApiPort $ApiPort

# 2) Aggregate metrics (python)
Write-Host "==> Aggregating metrics"
$py = "$PSScriptRoot\..\python-analysis\.venv\Scripts\python.exe"
if (!(Test-Path $py)) { $py = "python" }
& $py -u python-analysis/aggregate_metrics.py --results-dir data/results --out data/results/aggregate_metrics.csv

# 3) Run stats analysis
Write-Host "==> Running stats analysis"
& $py -u python-analysis/stats_analysis.py --results data/results --out data/results/stats_summary.json --md-out data/results/stats_summary.md

Write-Host "Full pipeline done. Outputs in data/results/"
