param([string]$PackagePath = "$env:USERPROFILE\Downloads\MusicStewardship_Processing_Log_Idempotent_Reporting_v0.2_POC_Install.zip")
$ErrorActionPreference = "Stop"
if (-not (Test-Path $PackagePath)) { throw "Package not found: $PackagePath" }
$root = Get-Location
$tmp = Join-Path $env:TEMP "MusicStewardship_Processing_v0.2_Install"
Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
Expand-Archive $PackagePath $tmp -Force
Copy-Item "$tmp\*" $root -Recurse -Force
Remove-Item $tmp -Recurse -Force
Write-Host "Installed Processing Prototype v0.2" -ForegroundColor Green
