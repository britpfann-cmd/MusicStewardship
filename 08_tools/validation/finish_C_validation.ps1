# MusicStewardship — C validation completion runner
# Run from C:\Projects\MusicStewardship
# This script is intentionally diagnostic. It does not modify source collections.

$ErrorActionPreference = "Stop"

$project = (Get-Location).Path
if ((Split-Path $project -Leaf) -ne "MusicStewardship") {
    throw "Run this script from C:\Projects\MusicStewardship"
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$out = Join-Path $project "06_runtime\validation\C_completion_$stamp"
New-Item -ItemType Directory -Force -Path $out | Out-Null

Write-Host "=== C VALIDATION COMPLETION ===" -ForegroundColor Cyan
Write-Host "Project: $project"
Write-Host "Output:  $out"
Write-Host ""

Write-Host "[1] Inventory/tool interface check" -ForegroundColor Yellow
python .\08_tools\ingestion\source_tree\source_tree.py --help |
    Out-File (Join-Path $out "source_tree_help.txt") -Encoding utf8

Write-Host "[2] Rosetta regression tests" -ForegroundColor Yellow
python -m pytest .\07_tests\ingestion\test_ttt_rosetta_v02.py -q |
    Tee-Object (Join-Path $out "ttt_rosetta_test.txt")

Write-Host "[3] Processing idempotence tests" -ForegroundColor Yellow
python -m pytest .\07_tests\ingestion\test_processing_idempotence_v02.py .\07_tests\ingestion\test_processing_idempotence_v03.py -q |
    Tee-Object (Join-Path $out "idempotence_tests.txt")

Write-Host "[4] Entity/provenance regression tests relevant to C→D boundary" -ForegroundColor Yellow
python -m pytest .\07_tests\provenance\test_d2_entity_candidate_recognition.py -q |
    Tee-Object (Join-Path $out "d2_test.txt")

Write-Host ""
Write-Host "=== DIAGNOSTIC COMPLETE ===" -ForegroundColor Green
Write-Host "This runner does not claim C is production-ready."
Write-Host "Review the generated files and compare them with:"
Write-Host "  01_docs\08_Implementation\C_Development_Notebook_2026-09-27.md"
Write-Host "  01_docs\05_Ingestion\C_Validation_Completion_Criteria_v0.1.md"
Write-Host ""
Write-Host "Next validation work should be source-set coverage and Library Card completeness,"
Write-Host "not further polishing of individual exploratory components."
