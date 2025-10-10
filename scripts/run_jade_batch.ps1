param(
  [string]$ExperimentPrefix = "exp_jade_batch",
  [int]$Repeats = 5,
  [int]$SeedBase = 100,
  [string]$ApiHost = "127.0.0.1",
  [int]$ApiPort = 8001
)
$ErrorActionPreference = 'Stop'

# Ensure API is up
$builder = New-Object System.UriBuilder
$builder.Scheme = 'http'; $builder.Host = $ApiHost; $builder.Port = $ApiPort; $builder.Path = 'health'
$healthUri = $builder.Uri.AbsoluteUri
$apiBase = $builder.Uri.GetLeftPart([System.UriPartial]::Authority)
$resp = Invoke-WebRequest -Uri $healthUri -UseBasicParsing
if ($resp.StatusCode -ne 200) { throw "API not healthy at $apiBase" }

for ($i = 0; $i -lt $Repeats; $i++) {
  $seed = $SeedBase + $i
  $exp = "$ExperimentPrefix-$seed"
  Write-Host "Running $exp (seed=$seed)"
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_jade_experiment.ps1 -ExperimentId $exp -Seed $seed -ApiHost $ApiHost -ApiPort $ApiPort
}

Write-Host "Batch completed. You can aggregate with your existing Python tools."
