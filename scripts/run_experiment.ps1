param(
    [string]$ExperimentId
)

# Purpose: Start FastAPI server, wait for health, run simulation, and stop server.
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\run_experiment.ps1 -ExperimentId exp_demo_01

$ErrorActionPreference = 'Stop'

function Ensure-Venv {
    if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
        Write-Host "Creating virtual environment..."
        python -m venv .venv
    }
    Write-Host "Activating virtual environment..."
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    . .\.venv\Scripts\Activate.ps1
    pip install --upgrade pip | Out-Null
    if (Test-Path ".\requirements.txt") {
        Write-Host "Installing requirements..."
        pip install -r .\requirements.txt | Out-Null
    }
}

function Wait-For-Health {
    param([string]$Url, [int]$TimeoutSec = 30)
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        try {
            $resp = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 5
            if ($resp.StatusCode -eq 200) { return $true }
        } catch {}
        Start-Sleep -Seconds 1
    }
    return $false
}

function Start-Api {
    Write-Host "Starting API server..."
    $env:PYTHONUNBUFFERED = "1"
    $apiCmd = "uvicorn python-analysis.api.main:app --host 127.0.0.1 --port 8000 --log-level warning"
    $script:apiProcess = Start-Process -FilePath powershell -ArgumentList "-NoProfile","-Command", $apiCmd -PassThru -WindowStyle Hidden
}

function Stop-Api {
    if ($script:apiProcess -and -not $script:apiProcess.HasExited) {
        Write-Host "Stopping API server (PID=$($script:apiProcess.Id))..."
        Stop-Process -Id $script:apiProcess.Id -Force
    }
}

try {
    if (-not $ExperimentId) {
        $ExperimentId = "exp_" + (Get-Date -Format "yyyyMMdd_HHmmss")
    }
    Write-Host "ExperimentId = $ExperimentId"

    Ensure-Venv

    # Check if API already up
    $apiHealthy = $false
    try {
        $resp = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2
        if ($resp.StatusCode -eq 200) { $apiHealthy = $true }
    } catch {}

    $startedHere = $false
    if (-not $apiHealthy) {
        Start-Api
        $startedHere = $true
        if (-not (Wait-For-Health -Url "http://127.0.0.1:8000/health" -TimeoutSec 30)) {
            throw "API health check failed"
        }
    } else {
        Write-Host "API already running."
    }

    Write-Host "Running simulation..."
    python .\python-analysis\simulate_experiment.py $ExperimentId

    Write-Host "Done. Results at data/results/$ExperimentId"
} finally {
    if ($startedHere) { Stop-Api }
}
