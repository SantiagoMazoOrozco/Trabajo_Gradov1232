param(
    [int]$Repeats = 10,
    [int]$MonitorSeconds = 0,
    [int]$SeedBase = 42,
    [string]$ApiHost = "127.0.0.1",
    [int]$ApiPort = 8000
)

$ErrorActionPreference = 'Stop'

function Ensure-Venv {
    if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
        Write-Host "Creating virtual environment..."
        python -m venv .venv
    }
    # Ensure dependencies are installed for API startup
    $py = ".\.venv\Scripts\python.exe"
    if (Test-Path $py) {
        & $py -m pip install --upgrade pip | Out-Null
        if (Test-Path ".\requirements.txt") {
            Write-Host "Installing requirements (batch)..."
            & $py -m pip install -r .\requirements.txt | Out-Host
        }
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

function Start-ApiOnce {
    param([string]$ApiHostParam, [int]$Port)
    # Reuse if already healthy
    if (Wait-For-Health -Url ("http://" + $ApiHostParam + ":" + $Port + "/health") -TimeoutSec 5) {
        Write-Host "API already running at http://$($ApiHostParam):$($Port)"
        return @{ startedHere = $false; port = $Port }
    }
    $py = ".\.venv\Scripts\python.exe"
    if (-not (Test-Path $py)) { throw "Python venv not found at $py" }
    $logsDir = Join-Path (Get-Location) "data\results\_server_logs"
    if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir | Out-Null }
    for ($attempt=0; $attempt -lt 10; $attempt++) {
        $portTry = $Port + $attempt
        Write-Host "Starting API server on $($ApiHostParam):$($portTry) ..."
        $script:apiLogPath = Join-Path $logsDir ("uvicorn_batch_" + (Get-Date -Format "yyyyMMdd_HHmmss") + "_" + $portTry + ".log")
        $script:apiErrPath = $script:apiLogPath + ".err"
    $args = @("-m","uvicorn","backend.api.main:app","--host",$ApiHostParam,"--port",$portTry,"--log-level","info")
        $script:apiProcess = Start-Process -FilePath $py -ArgumentList $args -RedirectStandardOutput $script:apiLogPath -RedirectStandardError $script:apiErrPath -PassThru -WindowStyle Hidden
        Start-Sleep -Milliseconds 300
        if (Wait-For-Health -Url ("http://" + $ApiHostParam + ":" + $portTry + "/health") -TimeoutSec 30) {
            Write-Host "API is healthy at http://$($ApiHostParam):$($portTry)"
            return @{ startedHere = $true; port = $portTry }
        } else {
            Write-Warning "API failed to start on $($ApiHostParam):$($portTry), trying next port..."
            try { if ($script:apiProcess -and -not $script:apiProcess.HasExited) { Stop-Process -Id $script:apiProcess.Id -Force } } catch {}
        }
    }
    throw "Could not start API on $ApiHostParam starting at port $Port (10 attempts)"
}

function Stop-ApiOnce {
    if ($script:apiProcess -and -not $script:apiProcess.HasExited) {
        Write-Host "Stopping API server (PID=$($script:apiProcess.Id))..."
        Stop-Process -Id $script:apiProcess.Id -Force
    }
}

function Invoke-RunOnce {
    param([string]$Group, [int]$Seed)
    $id = "${Group}_" + (Get-Date -Format "yyyyMMdd_HHmmss_ffff")
    $parms = @(".\scripts\run_experiment.ps1", "-ExperimentId", $id, "-Group", $Group, "-Seed", $Seed, "-ApiHost", $ApiHost, "-ApiPort", $ApiPort)
    if ($MonitorSeconds -gt 0) { $parms += @("-Monitored", "-MonitorSeconds", $MonitorSeconds) }
    powershell -NoProfile -ExecutionPolicy Bypass -File $parms | Out-Host
    return $id
}

try {
    Ensure-Venv
    $apiInfo = Start-ApiOnce -ApiHostParam $ApiHost -Port $ApiPort
    $startedHere = $apiInfo.startedHere
    $ApiPort = [int]$apiInfo.port
    $all = @()
    Write-Host "Batch: running $Repeats repeats per group (control vs treatment)"
    for ($i=1; $i -le $Repeats; $i++) {
        $seed = $SeedBase + $i
        Write-Host "[$i/$Repeats] control (seed=$seed)"
        $all += Invoke-RunOnce -Group 'control' -Seed $seed
        Start-Sleep -Seconds 1
        $seed = $SeedBase + 1000 + $i
        Write-Host "[$i/$Repeats] treatment (seed=$seed)"
        $all += Invoke-RunOnce -Group 'treatment' -Seed $seed
        Start-Sleep -Seconds 1
    }
    Write-Host "Aggregating metrics..."
    .\.venv\Scripts\python.exe .\python-analysis\aggregate_metrics.py | Out-Host
    Write-Host "Running stats analysis..."
    .\.venv\Scripts\python.exe .\python-analysis\stats_analysis.py | Out-Host
    Write-Host "Batch complete. Experiments: $($all -join ', ')"
} catch {
    Write-Error $_
    exit 1
} finally {
    if ($startedHere) { Stop-ApiOnce }
}
