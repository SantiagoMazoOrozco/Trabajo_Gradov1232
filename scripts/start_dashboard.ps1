param(
    [int]$PortStart = 8001,
    [string]$ApiHost = '127.0.0.1',
    [int]$MaxTries = 10,
    [switch]$Verbose
)

# Starts the FastAPI dashboard (uvicorn) on the first available port >= PortStart
# Writes server info to data/results/_server_state/uvicorn_dashboard.json
# Logs go to data/results/_server_logs/

$ErrorActionPreference = 'Stop'

function Initialize-Venv {
    if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
        Write-Host "Creating virtual environment..."
        python -m venv .venv
    }
    $py = ".\.venv\Scripts\python.exe"
    & $py -m pip install --upgrade pip | Out-Null
    if (Test-Path ".\requirements.txt") {
        & $py -m pip install -r .\requirements.txt | Out-Null
    }
    return $py
}

function Test-Health {
    param([string]$ApiHostParam, [int]$Port, [int]$TimeoutSec = 5)
    try {
        $url = "http://$($ApiHostParam):$($Port)/health"
        $resp = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec $TimeoutSec
        if ($resp.StatusCode -eq 200) { return $true }
    } catch {}
    return $false
}

function Get-ApiPid {
    param([string]$ApiHostParam, [int]$Port)
    try {
        $url = "http://$($ApiHostParam):$($Port)/pid"
        $resp = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 5
        $obj = $resp.Content | ConvertFrom-Json
        return $obj.pid
    } catch { return $null }
}

$pyExe = Initialize-Venv

$stateDir = Join-Path (Get-Location) "data\results\_server_state"
$logsDir = Join-Path (Get-Location) "data\results\_server_logs"
if (-not (Test-Path $stateDir)) { New-Item -ItemType Directory -Path $stateDir | Out-Null }
if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir | Out-Null }

for ($i = 0; $i -lt $MaxTries; $i++) {
    $port = $PortStart + $i
    if (Test-Health -ApiHostParam $ApiHost -Port $port -TimeoutSec 3) {
        $serverPid = Get-ApiPid -ApiHostParam $ApiHost -Port $port
        Write-Host ("Dashboard already running at http://{0}:{1} (PID={2})" -f $ApiHost, $port, $serverPid)
        $info = [ordered]@{
            host = $ApiHost
            port = $port
            pid = $serverPid
            started_utc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
            existing = $true
        }
        $info | ConvertTo-Json -Depth 5 | Set-Content -Path (Join-Path $stateDir 'uvicorn_dashboard.json') -Encoding UTF8
        exit 0
    }

    $logBase = Join-Path $logsDir ("uvicorn_dashboard_" + (Get-Date -Format "yyyyMMdd_HHmmss") + "_" + $port)
    $outLog = $logBase + ".log"
    $errLog = $logBase + ".err.log"

    $procArgs = @('-m','uvicorn','backend.api.main:app','--host',$ApiHost,'--port',$port,'--log-level','info')
    $proc = Start-Process -FilePath $pyExe -ArgumentList $procArgs -RedirectStandardOutput $outLog -RedirectStandardError $errLog -PassThru -WindowStyle Hidden
    if ($Verbose) { Write-Host ("Started uvicorn (PID={0}) on {1}:{2}, waiting for health..." -f $proc.Id, $ApiHost, $port) }

    $deadline = (Get-Date).AddSeconds(30)
    while ((Get-Date) -lt $deadline) {
        if (Test-Health -ApiHostParam $ApiHost -Port $port -TimeoutSec 3) {
            $pidReported = Get-ApiPid -ApiHostParam $ApiHost -Port $port
            $info = [ordered]@{
                host = $ApiHost
                port = $port
                pid = if ($pidReported) { $pidReported } else { $proc.Id }
                started_utc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
                existing = $false
                logs = @{ stdout = $outLog; stderr = $errLog }
            }
            $info | ConvertTo-Json -Depth 6 | Set-Content -Path (Join-Path $stateDir 'uvicorn_dashboard.json') -Encoding UTF8
            Write-Host ("Dashboard UP at http://{0}:{1} (PID={2})" -f $ApiHost, $port, $info.pid)
            exit 0
        }
        Start-Sleep -Seconds 1
    }
    Write-Warning ("Health check failed on {0}:{1}, stopping process and trying next port..." -f $ApiHost, $port)
    try { if ($proc -and -not $proc.HasExited) { Stop-Process -Id $proc.Id -Force } } catch {}
}

Write-Error "Could not start dashboard on $ApiHost starting at port $PortStart (tried $MaxTries ports)"
exit 1
