param(
    [string]$StateFile = 'data\results\_server_state\uvicorn_dashboard.json'
)

# Stops the FastAPI dashboard if it was started via start_dashboard.ps1
# Reads PID from the state file and attempts a graceful stop.

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $StateFile)) {
    Write-Warning "State file not found: $StateFile"
    exit 0
}

try {
    $info = Get-Content -Raw -Path $StateFile | ConvertFrom-Json
} catch {
    Write-Warning "Could not read state file: $_"
    exit 1
}

if (-not $info.pid) {
    Write-Warning "No PID in state file."
    exit 0
}

$pidVal = [int]$info.pid
try {
    Write-Host "Stopping dashboard (PID=$pidVal)..."
    Stop-Process -Id $pidVal -Force -ErrorAction Stop
    Write-Host "Stopped."
} catch {
    Write-Warning "Process not running: PID=$pidVal"
}
