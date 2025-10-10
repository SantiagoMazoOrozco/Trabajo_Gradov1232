param(
  [string]$ExperimentId = "exp_jade_demo",
  [int]$Seed = 42,
  [string]$JavaCmd = "mvn",
  [string]$ApiHost = "127.0.0.1",
  [int]$ApiPort = 8001
)

# Purpose: Start API if needed, then run Java coordinator prototype, and write meta.json
$ErrorActionPreference = 'Stop'

# Resolve workspace root
$root = Split-Path -Parent $PSCommandPath
$workspace = Split-Path -Parent $root

# Resolve Maven command if not on PATH
if ($JavaCmd -eq 'mvn') {
  if ($env:MVN_CMD -and (Test-Path $env:MVN_CMD)) {
    $JavaCmd = $env:MVN_CMD
  } elseif (Test-Path (Join-Path $workspace '.tools/apache-maven-3.9.9/bin/mvn.cmd')) {
    $JavaCmd = (Join-Path $workspace '.tools/apache-maven-3.9.9/bin/mvn.cmd')
  }
}

# Ensure API is up (reuse start_dashboard.ps1 logic for health)
try {
  $builder = New-Object System.UriBuilder
  $builder.Scheme = 'http'
  $builder.Host = $ApiHost
  $builder.Port = $ApiPort
  $builder.Path = 'health'
  $healthUri = $builder.Uri.AbsoluteUri
  # Base without path
  $apiBase = $builder.Uri.GetLeftPart([System.UriPartial]::Authority)

  $resp = Invoke-WebRequest -Uri $healthUri -UseBasicParsing
  if ($resp.StatusCode -ne 200) { throw "API not healthy" }
} catch {
  Write-Host "API not running; please start it via scripts/start_dashboard.ps1 -Port $ApiPort"
  throw
}

# Set env var so the Python CLI hits the right API (process-scoped)
[System.Environment]::SetEnvironmentVariable('API_BASE', $apiBase, 'Process')

Push-Location "$workspace\jade-platform"
try {
  # Pass ExperimentId and Seed to Java via environment variables
  [System.Environment]::SetEnvironmentVariable('EXPERIMENT_ID', $ExperimentId, 'Process')
  [System.Environment]::SetEnvironmentVariable('SEED', "$Seed", 'Process')
  # Prefer workspace venv python if available
  $venvPy = Join-Path $workspace "python-analysis/.venv/Scripts/python.exe"
  if (Test-Path $venvPy) { [System.Environment]::SetEnvironmentVariable('PYTHON_CMD', $venvPy, 'Process') }
  # Ensure JAVA_HOME for this session if missing
  if (-not $env:JAVA_HOME) {
    try {
      $javaHome = (Get-ItemProperty "HKLM:\SOFTWARE\Eclipse Adoptium\JDK\17" -ErrorAction SilentlyContinue).Path
      if (-not $javaHome) {
        $javaHome = (Get-ChildItem "HKLM:\SOFTWARE\Eclipse Adoptium\JDK" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.GetValue('Path') } | Select-Object -First 1).GetValue('Path')
      }
      if ($javaHome) { $env:JAVA_HOME = $javaHome }
    } catch { }
  }
  Write-Host "Running Maven: $JavaCmd -DskipTests=true -e compile exec:java"
  & $JavaCmd -DskipTests=true -e compile exec:java
} finally {
  Pop-Location
}

Write-Host "JADE prototype done. Check data/results/$ExperimentId for outputs."
