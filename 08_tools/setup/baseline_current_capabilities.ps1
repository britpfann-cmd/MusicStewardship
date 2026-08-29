# MusicStewardship — baseline current architecture/tools
# Run from: C:\Projects\MusicStewardship
#
# This script:
#   1. adds a project-local ephemeral sandbox to .gitignore
#   2. ignores generated Python/test artifacts
#   3. stages the current documentation baseline
#   4. stages the current reusable ingest/reference tools
#
# It deliberately does NOT stage historical test iterations, generated CSV
# results, databases, __pycache__, downloaded web-page assets, or other
# exploratory artifacts.

$ErrorActionPreference = "Stop"

$root = Get-Location

if (-not (Test-Path ".git")) {
    throw "Run this script from the MusicStewardship repository root."
}

# ---------------------------------------------------------------------------
# 1. Establish an ephemeral project-local sandbox.
# ---------------------------------------------------------------------------

$sandbox = ".\99_sandbox"
New-Item -ItemType Directory -Path $sandbox -Force | Out-Null

$gitignore = ".\.gitignore"
$entries = @(
    "",
    "# MusicStewardship ephemeral working area",
    "99_sandbox/",
    "",
    "# Generated Python runtime artifacts",
    "__pycache__/",
    "*.pyc",
    "",
    "# Local ingest ledgers / working databases",
    "08_tools/text/tests/*.db",
    "",
    "# Generated validation/report output",
    "08_tools/text/tests/*_validation.csv",
    "08_tools/text/tests/*_summary.csv",
    "08_tools/text/tests/*_issues.csv",
    "08_tools/text/tests/*_comparison*.csv"
)

$current = if (Test-Path $gitignore) {
    Get-Content $gitignore -Raw
} else {
    ""
}

foreach ($entry in $entries) {
    if ($entry -eq "") {
        continue
    }
    if ($current -notmatch [regex]::Escape($entry)) {
        Add-Content -Path $gitignore -Value $entry
        $current += "`r`n$entry"
    }
}

# ---------------------------------------------------------------------------
# 2. Stage current documentation baseline.
# ---------------------------------------------------------------------------

$docs = @(
    ".\01_docs\Architecture\MusicStewardship_Music_Vocabulary_and_Ingestion_Framework.md",
    ".\01_docs\Implementation\Audio_Asset_Lifecycle_Implementation_Requirement.md",
    ".\01_docs\Implementation\Current_Capabilities_Baseline_2026-08-29.md",
    ".\01_docs\Implementation\Music_Materialization_Workflow.md",
    ".\01_docs\Implementation\TTT_Source_Ingest_Implementation_Notes.md",
    ".\01_docs\Specifications\Reference_Record_Staging_Spec.md"
)

# ---------------------------------------------------------------------------
# 3. Stage current reusable tools.
# ---------------------------------------------------------------------------

$tools = @(
    ".\08_tools\text\ingest_status.py",
    ".\08_tools\text\ingest_ttt_with_ledger.py",
    ".\08_tools\text\validate_ttt_release.py",
    ".\08_tools\text\validate_ttt_tree.py",
    ".\08_tools\text\build_ttt_canonical_staging.py",
    ".\08_tools\text\compare_ttt_tags_to_reference.py",
    ".\08_tools\text\probe_ttt_test_set.py",
    ".\gitignore"
)

foreach ($path in ($docs + $tools)) {
    if (-not (Test-Path $path)) {
        Write-Warning "Not found; skipping: $path"
    }
    else {
        git add -- $path
    }
}

Write-Host ""
Write-Host "Baseline staging complete." -ForegroundColor Green
Write-Host ""
Write-Host "Staged files:"
git diff --cached --name-only
Write-Host ""
Write-Host "Staged summary:"
git diff --cached --stat
Write-Host ""
Write-Host "Remaining working-tree status:"
git status --short
Write-Host ""
Write-Host "NOTE: Historical test iterations and generated outputs were intentionally left unstaged."
Write-Host "NOTE: 99_sandbox/ is now ephemeral and ignored by Git."
