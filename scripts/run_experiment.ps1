param(
    [string]$ExperimentId,
    [switch]$Quiesce,
    [switch]$HighPriority,
    [int]$AffinityMask,
    [switch]$Monitored,
    [int]$MonitorSeconds = 180,
    [switch]$Report
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
    $py = Join-Path (Get-Location) ".venv\Scripts\python.exe"
    if (-not (Test-Path $py)) { throw "Python venv not found at $py" }
    $script:apiProcess = Start-Process -FilePath $py -ArgumentList "-m","uvicorn","python-analysis.api.main:app","--host","127.0.0.1","--port","8000","--log-level","warning" -PassThru -WindowStyle Hidden
    Start-Sleep -Milliseconds 300
    if ($HighPriority -and $script:apiProcess) {
        try { (Get-Process -Id $script:apiProcess.Id).PriorityClass = 'High' } catch {}
    }
    if ($AffinityMask -and $script:apiProcess) {
        try {
            $proc = Get-Process -Id $script:apiProcess.Id
            $proc.ProcessorAffinity = [intptr]$AffinityMask
        } catch { Write-Warning "No se pudo establecer afinidad de CPU." }
    }
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
    if ($Quiesce) {
        try { & .\scripts\quiesce_system.ps1 } catch { Write-Warning "Quiesce falló: $_" }
    }

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

    # Start monitor if requested
    if ($Monitored) {
        try {
            Write-Host "Starting monitor for $MonitorSeconds seconds..."
            $py = Join-Path (Get-Location) ".venv\Scripts\python.exe"
            $script:monProcess = Start-Process -FilePath $py -ArgumentList ".\python-analysis\monitor_run.py", $ExperimentId, "--duration", $MonitorSeconds -PassThru -WindowStyle Hidden
        } catch { Write-Warning "No se pudo iniciar el monitor: $_" }
    }

    Write-Host "Running simulation..."
    python .\python-analysis\simulate_experiment.py $ExperimentId

    Write-Host "Done. Results at data/results/$ExperimentId"
    if ($Report) {
        try {
            Write-Host "Generating HTML report..."
            $py = Join-Path (Get-Location) ".venv\Scripts\python.exe"
            & $py .\python-analysis\report_run.py $ExperimentId | Out-Host
        } catch { Write-Warning "No se pudo generar el reporte: $_" }
    }
} finally {
    if ($Monitored -and $script:monProcess -and -not $script:monProcess.HasExited) {
        try { $script:monProcess.WaitForExit() } catch {}
    }
    if ($startedHere) { Stop-Api }
    if ($Quiesce) {
        try { & .\scripts\restore_system.ps1 } catch { Write-Warning "Restore falló: $_" }
    }
}
