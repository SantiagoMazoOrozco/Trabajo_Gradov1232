param(
    [string]$Date = (Get-Date -Format 'yyyy-MM-dd'),
    [switch]$NoDailyLog
)

$ErrorActionPreference = 'Stop'

function Get-GitLogForDate {
    param([string]$Date)
    $since = "$Date 00:00"
    $until = "$Date 23:59"
    $raw = & git --no-pager log --since="$since" --until="$until" --pretty=format:"%h`t%ad`t%s" --date=short --name-only 2>$null
    if ($LASTEXITCODE -ne 0) { throw "git log failed with exit code $LASTEXITCODE" }
    if ($null -eq $raw) { return @() }
    $text = ($raw | Out-String)
    $lines = $text -split "`r?`n"
    return $lines
}

function ConvertFrom-GitLog {
    param([string[]]$Lines)
    $entries = @()
    $current = $null
    foreach ($line in $Lines) {
        $line = $line.TrimEnd()
        if ($line -match '^[0-9a-f]{7,}\t\d{4}-\d{2}-\d{2}\t') {
            if ($current) { $entries += $current }
            $parts = $line -split "`t"
            $current = [ordered]@{
                hash = $parts[0]
                date = $parts[1]
                subject = $parts[2]
                files = @()
            }
        } elseif ($line -ne '') {
            if ($current) { $current.files += $line }
        }
    }
    if ($current) { $entries += $current }
    return $entries
}

function Write-DailyIndex {
    param(
        [string]$Date,
        [object[]]$Entries
    )
    $docsFiles = New-Object 'System.Collections.Generic.HashSet[string]'
    $codeFiles = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($e in $Entries) {
        foreach ($f in $e.files) {
            if ($f -like 'docs/*' -or $f -like 'docs\\*') { [void]$docsFiles.Add($f) }
            else { [void]$codeFiles.Add($f) }
        }
    }

    $dayDir = Join-Path 'docs' $Date
    if (-not (Test-Path $dayDir)) { New-Item -ItemType Directory -Path $dayDir | Out-Null }

    $indexPath = Join-Path $dayDir 'index.md'
    $sb = New-Object System.Text.StringBuilder
    [void]$sb.AppendLine("# Documentación del día $Date")
    [void]$sb.AppendLine()

    if ($docsFiles.Count -gt 0) {
        [void]$sb.AppendLine("Archivos de documentación creados/actualizados:")
        [void]$sb.AppendLine()
        foreach ($f in ($docsFiles | Sort-Object)) {
            $rel = "../$f" -replace '\\','/'
            [void]$sb.AppendLine("- $rel")
        }
        [void]$sb.AppendLine()
    } else {
        [void]$sb.AppendLine("No hubo cambios en docs en esta fecha según git log.")
        [void]$sb.AppendLine()
    }

    if ($codeFiles.Count -gt 0) {
        [void]$sb.AppendLine("Código relevante cambiado hoy:")
        [void]$sb.AppendLine()
        foreach ($f in ($codeFiles | Sort-Object)) {
            $rel = "../../$f" -replace '\\','/'
            [void]$sb.AppendLine("- $rel")
        }
        [void]$sb.AppendLine()
    }

    Set-Content -Path $indexPath -Value $sb.ToString() -Encoding UTF8
}

function Write-DailyLog {
    param(
        [string]$Date,
        [object[]]$Entries
    )
    $dayDir = Join-Path 'docs' $Date
    if (-not (Test-Path $dayDir)) { New-Item -ItemType Directory -Path $dayDir | Out-Null }
    $logPath = Join-Path $dayDir ("daily-log-$Date.md")
    $sb = New-Object System.Text.StringBuilder
    [void]$sb.AppendLine("# Registro diario - $Date")
    [void]$sb.AppendLine()
    if ($Entries.Count -eq 0) {
    [void]$sb.AppendLine("Sin commits en esta fecha segun git log.")
    } else {
        foreach ($e in $Entries) {
            [void]$sb.AppendLine("- ``" + $e.hash + "`` " + $e.subject)
            if ($e.files.Count -gt 0) {
                foreach ($f in $e.files) { [void]$sb.AppendLine("  - " + $f) }
            }
            [void]$sb.AppendLine()
        }
    }
    Set-Content -Path $logPath -Value $sb.ToString() -Encoding UTF8
}

function Update-MasterIndex {
    $docsDir = Join-Path (Get-Location) 'docs'
    $dirs = Get-ChildItem $docsDir -Directory | Where-Object { $_.Name -match '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' } | Sort-Object Name
    $sb = New-Object System.Text.StringBuilder
    [void]$sb.AppendLine('# Índice por fecha de documentación')
    [void]$sb.AppendLine()
    foreach ($d in $dirs) {
    [void]$sb.AppendLine("- " + $d.Name + " - docs/" + $d.Name + "/index.md")
    }
    [void]$sb.AppendLine()
    [void]$sb.AppendLine('Nota: Los enlaces apuntan a índices diarios que referencian los documentos fuente.')
    Set-Content -Path (Join-Path $docsDir 'INDEX_BY_DATE.md') -Value $sb.ToString() -Encoding UTF8
}

# Main
try {
    $lines = Get-GitLogForDate -Date $Date
    $entries = ConvertFrom-GitLog -Lines $lines
    Write-DailyIndex -Date $Date -Entries $entries
    if (-not $NoDailyLog) { Write-DailyLog -Date $Date -Entries $entries }
    Update-MasterIndex
    Write-Host "Daily index generated for $Date under docs/$Date."
} catch {
    Write-Error $_
    exit 1
}
