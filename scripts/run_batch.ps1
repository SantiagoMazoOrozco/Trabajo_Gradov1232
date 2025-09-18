param(
    [int]$Repeats = 10,
    [int]$MonitorSeconds = 0,
    [string]$ApiHost = "127.0.0.1",
    [int]$ApiPort = 8000
)

$ErrorActionPreference = 'Stop'

function Invoke-RunOnce {
    param([string]$Group)
    $id = "${Group}_" + (Get-Date -Format "yyyyMMdd_HHmmss_ffff")
    $parms = @(".\scripts\run_experiment.ps1", "-ExperimentId", $id, "-Group", $Group, "-ApiHost", $ApiHost, "-ApiPort", $ApiPort)
    if ($MonitorSeconds -gt 0) { $parms += @("-Monitored", "-MonitorSeconds", $MonitorSeconds) }
    powershell -NoProfile -ExecutionPolicy Bypass -File $parms | Out-Host
    return $id
}

try {
    $all = @()
    Write-Host "Batch: running $Repeats repeats per group (control vs treatment)"
    for ($i=1; $i -le $Repeats; $i++) {
        Write-Host "[$i/$Repeats] control"
    $all += Invoke-RunOnce -Group 'control'
        Start-Sleep -Seconds 1
    Write-Host "[$i/$Repeats] treatment"
    $all += Invoke-RunOnce -Group 'treatment'
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
}
