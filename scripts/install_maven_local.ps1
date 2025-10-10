param(
  [string]$Version = "3.9.9"
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSCommandPath
$workspace = Split-Path -Parent $root
$tools = Join-Path $workspace ".tools"
$mvndir = Join-Path $tools ("apache-maven-" + $Version)
$mvnzip = Join-Path $tools ("apache-maven-" + $Version + "-bin.zip")

New-Item -ItemType Directory -Force -Path $tools | Out-Null
if (!(Test-Path $mvndir)) {
  Write-Host "Downloading Maven $Version..."
  $url = "https://archive.apache.org/dist/maven/maven-3/$Version/binaries/apache-maven-$Version-bin.zip"
  Invoke-WebRequest -Uri $url -OutFile $mvnzip -UseBasicParsing
  Write-Host "Extracting..."
  Expand-Archive -Path $mvnzip -DestinationPath $tools -Force
}

# Export mvn path for current process
$mvnCmd = Join-Path $mvndir "bin/mvn.cmd"
if (!(Test-Path $mvnCmd)) { throw "mvn.cmd not found at $mvnCmd" }
[System.Environment]::SetEnvironmentVariable('MVN_CMD', $mvnCmd, 'Process')
Write-Host "Maven ready: $mvnCmd (set as MVN_CMD)"
