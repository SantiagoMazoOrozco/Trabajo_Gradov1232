param(
    [string]$ExperimentId,
    [ValidateSet('control','treatment')]
    [string]$Group = 'treatment',
    [switch]$Quiesce,
    [switch]$HighPriority,
    [int]$AffinityMask,
    [switch]$Monitored,
    [int]$MonitorSeconds = 180,
    [switch]$Report,
    [int]$Seed = 42,
    [string]$ApiHost = "127.0.0.1",
    [int]$ApiPort = 8000
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
    # Use script-scoped Python exe if available, else resolve
    if (-not $script:pyExe) {
        $script:pyExe = Join-Path (Get-Location) ".venv\Scripts\python.exe"
    }
    if (-not (Test-Path $script:pyExe)) { throw "Python venv not found at $script:pyExe" }
    $logsDir = Join-Path (Get-Location) "data\results\_server_logs"
    if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir | Out-Null }
    $script:apiLogPath = Join-Path $logsDir ("uvicorn_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".log")
    $script:apiErrPath = Join-Path $logsDir ("uvicorn_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".err.log")
    $args = @("-m","uvicorn","python-analysis.api.main:app","--host",$ApiHost,"--port",$ApiPort,"--log-level","info")
    $script:apiProcess = Start-Process -FilePath $script:pyExe -ArgumentList $args -RedirectStandardOutput $script:apiLogPath -RedirectStandardError $script:apiErrPath -PassThru -WindowStyle Hidden
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
        $resp = Invoke-WebRequest -UseBasicParsing -Uri ("http://" + $ApiHost + ":" + $ApiPort + "/health") -TimeoutSec 2
        if ($resp.StatusCode -eq 200) { $apiHealthy = $true }
    } catch {}

    $startedHere = $false
    $apiPid = $null
    if (-not $apiHealthy) {
        Start-Api
        $startedHere = $true
    if (-not (Wait-For-Health -Url ("http://" + $ApiHost + ":" + $ApiPort + "/health") -TimeoutSec 60)) {
            Write-Warning "API health check failed after 60s. Showing last lines of server log:"
            if ($script:apiLogPath -and (Test-Path $script:apiLogPath)) {
                try { Get-Content $script:apiLogPath -Tail 50 | Out-Host } catch {}
            }
            if ($script:apiErrPath -and (Test-Path $script:apiErrPath)) {
                try { Get-Content $script:apiErrPath -Tail 50 | Out-Host } catch {}
            }
            throw "API health check failed"
        }
        try {
            $pidResp = Invoke-WebRequest -UseBasicParsing -Uri ("http://" + $ApiHost + ":" + $ApiPort + "/pid") -TimeoutSec 5
            $apiPid = ($pidResp.Content | ConvertFrom-Json).pid
        } catch { Write-Warning "No se pudo obtener PID del API: $_" }
    } else {
        Write-Host "API already running."
    }

    # Start monitor if requested
    if ($Monitored) {
        try {
            Write-Host "Starting monitor for $MonitorSeconds seconds..."
            if (-not $script:pyExe) { $script:pyExe = Join-Path (Get-Location) ".venv\Scripts\python.exe" }
            $monArgs = @(".\python-analysis\monitor_run.py", $ExperimentId, "--duration", $MonitorSeconds)
            if ($apiPid) { $monArgs += @("--pid", $apiPid) }
            $script:monProcess = Start-Process -FilePath $script:pyExe -ArgumentList $monArgs -PassThru -WindowStyle Hidden
        } catch { Write-Warning "No se pudo iniciar el monitor: $_" }
    }

    Write-Host "Running simulation..."
    $env:API_BASE = "http://" + $ApiHost + ":" + $ApiPort
    if (-not $script:pyExe) { $script:pyExe = Join-Path (Get-Location) ".venv\Scripts\python.exe" }
    $simArgs = @(".\python-analysis\simulate_experiment.py", $ExperimentId, $Seed)
    & $script:pyExe $simArgs

    Write-Host "Done. Results at data/results/$ExperimentId"
    # Write experiment meta
    try {
        $metaDir = Join-Path (Get-Location) ("data/results/" + $ExperimentId)
        if (-not (Test-Path $metaDir)) { New-Item -ItemType Directory -Path $metaDir | Out-Null }
        $meta = [ordered]@{
            experimentId = $ExperimentId
            group = $Group
            seed = $Seed
            api_host = $ApiHost
            api_port = $ApiPort
            monitored = [bool]$Monitored
            created_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        }
        $metaPath = Join-Path $metaDir 'meta.json'
        $meta | ConvertTo-Json -Depth 5 | Set-Content -Path $metaPath -Encoding UTF8
    } catch { Write-Warning "No se pudo escribir meta.json: $_" }
    if ($Report) {
        try {
            Write-Host "Generating HTML report..."
            if (-not $script:pyExe) { $script:pyExe = Join-Path (Get-Location) ".venv\Scripts\python.exe" }
            & $script:pyExe .\python-analysis\report_run.py $ExperimentId | Out-Host
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
