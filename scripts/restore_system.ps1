# Restore system to pre-quiesce state

$ErrorActionPreference = 'Continue'
$statePath = Join-Path (Split-Path $MyInvocation.MyCommand.Path) ".quiesce_state.json"
if (-not (Test-Path $statePath)) {
    Write-Warning "No hay estado previo ($statePath). Nada que restaurar."
    return
}

$state = Get-Content -Raw -Path $statePath | ConvertFrom-Json

function Test-IsAdmin {
    try {
        $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
        return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    } catch { return $false }
}

$needAdmin = -not (Test-IsAdmin)

# Restore power scheme
if ($state.PowerScheme) {
    try { powercfg /SETACTIVE $state.PowerScheme | Out-Null } catch { Write-Warning "No se pudo restaurar plan de energía." }
}

# Restart services if they were running
foreach ($entry in $state.Services) {
    try {
        if ($entry.WasRunning -eq $true) {
            if ($needAdmin) { Write-Warning "Se requiere PowerShell como Administrador para iniciar $($entry.Name). Omitiendo." }
            else { Start-Service -Name $entry.Name -ErrorAction SilentlyContinue }
        }
    } catch {}
}

# Relaunch OneDrive if it was running
if ($state.OneDriveWasRunning -eq $true) {
    $odPath = Join-Path $env:LOCALAPPDATA 'Microsoft\OneDrive\OneDrive.exe'
    if (Test-Path $odPath) {
        Start-Process -FilePath $odPath -WindowStyle Hidden
    }
}

Write-Host "Sistema restaurado. Puedes borrar $statePath si ya no es necesario."