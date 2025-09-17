param(
    [switch]$AlsoStopWindowsUpdate
)

# Quiesce system for controlled experiment runs.
# - Sets power plan to High/Ultimate performance
# - Pauses OneDrive sync
# - Stops non-critical services (WSearch, SysMain); optional Windows Update
# - Saves prior state to scripts/.quiesce_state.json for restoration

$ErrorActionPreference = 'Continue'
$statePath = Join-Path (Split-Path $MyInvocation.MyCommand.Path) ".quiesce_state.json"

function Test-IsAdmin {
    try {
        $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
        return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    } catch { return $false }
}

$state = @{
    Timestamp = (Get-Date).ToString("s")
    PowerScheme = $null
    OneDriveWasRunning = $false
    Services = @()
}

# Capture current power scheme
try {
    $active = (powercfg /GETACTIVESCHEME) 2>$null
    if ($active) {
        if ($active -match 'GUID:\s*([a-f0-9\-]+)') { $state.PowerScheme = $matches[1] }
    }
} catch {}

# Find High/Ultimate performance scheme
$targetScheme = $null
try {
    $list = (powercfg /LIST) 2>$null
    $ultimate = ($list | Select-String -Pattern 'Ultimate Performance|Rendimiento.*\(disponible\)')
    $high = ($list | Select-String -Pattern 'High performance|Alto rendimiento')
    if ($ultimate -and ($ultimate.Line -match '([a-f0-9\-]{36})')) { $targetScheme = $matches[1] }
    elseif ($high -and ($high.Line -match '([a-f0-9\-]{36})')) { $targetScheme = $matches[1] }
} catch {}

if ($targetScheme) {
    try { powercfg /SETACTIVE $targetScheme | Out-Null } catch { Write-Warning "No se pudo cambiar el plan de energía." }
} else {
    Write-Warning "No se encontró plan 'High/Ultimate performance'; se mantiene el actual."
}

# Pause OneDrive (if running)
try {
    $od = Get-Process -Name OneDrive -ErrorAction SilentlyContinue
    if ($od) {
        $state.OneDriveWasRunning = $true
        $odPath = Join-Path $env:LOCALAPPDATA 'Microsoft\OneDrive\OneDrive.exe'
        if (Test-Path $odPath) {
            Start-Process -FilePath $odPath -ArgumentList "/shutdown" -WindowStyle Hidden
            Start-Sleep -Seconds 2
        } else {
            Write-Warning "OneDrive.exe no encontrado para shutdown."
        }
    }
} catch {}

# Stop non-critical services
$needAdmin = -not (Test-IsAdmin)
$serviceNames = @('WSearch','SysMain')
if ($AlsoStopWindowsUpdate) { $serviceNames += 'wuauserv' }

foreach ($svc in $serviceNames) {
    try {
        $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
        if ($null -ne $s) {
            $state.Services += @{ Name=$svc; WasRunning=($s.Status -eq 'Running') }
            if ($s.Status -eq 'Running') {
                if ($needAdmin) { Write-Warning "Se requiere PowerShell como Administrador para detener $svc. Omitiendo." }
                else { Stop-Service -Name $svc -Force -ErrorAction SilentlyContinue }
            }
        }
    } catch {}
}

# Save state
try { $state | ConvertTo-Json -Depth 5 | Set-Content -Path $statePath -Encoding UTF8 } catch {}

Write-Host "Sistema en modo controlado. Estado guardado en $statePath"