$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$tools = Join-Path $root "08_tools"
$text = Join-Path $tools "text"
$retired = Join-Path $tools "retired\text\historical_ingest"

$files = @(
    "build_ttt_canonical_staging.py",
    "compare_ttt_tags_to_reference.py",
    "ingest_ttt_with_ledger.py",
    "probe_ttt_test_set.py",
    "validate_ttt_release.py",
    "validate_ttt_tree.py",
    "build_ingest_evidence.py"
)

New-Item -ItemType Directory -Force -Path $retired | Out-Null

$manifest = @()

foreach ($name in $files) {
    $source = Join-Path $text $name

    if (-not (Test-Path $source)) {
        Write-Warning "Missing: $name"
        continue
    }

    $destination = Join-Path $retired $name

    if (Test-Path $destination) {
        throw "Destination already exists: $destination"
    }

    Move-Item -LiteralPath $source -Destination $destination

    $manifest += [PSCustomObject]@{
        File = $name
        FormerPath = "08_tools/text/$name"
        RetiredPath = "08_tools/retired/text/historical_ingest/$name"
        Reason = "Historical implementation superseded by grammar-driven generic ingestion"
        Status = "RETIRED"
    }

    Write-Host "[RETIRED] $name"
}

$manifestPath = Join-Path $retired "RETIREMENT_MANIFEST.csv"
$manifest | Export-Csv -NoTypeInformation -Encoding UTF8 $manifestPath

@"
# Historical Ingestion Tools

These tools are retired historical implementations from the development
of MusicStewardship's grammar-driven ingestion architecture.

They are retained as regression references and historical evidence.

They are NOT part of the current production ingestion path.

## Retirement principle

A historical implementation is retired only after its relevant behavior
has been baselined or superseded by the generalized architecture.

Files may be restored through Git if historical comparison is required.

## Current successor

The intended production direction is:

    source tree
        ↓
    source grammar
        ↓
    generic ingestion engine
        ↓
    evidence
        ↓
    asset records
        ↓
    optional reconciliation

## Retired files

See RETIREMENT_MANIFEST.csv.
"@ | Set-Content (Join-Path $retired "README.md") -Encoding UTF8

Write-Host ""
Write-Host "Retirement complete."
Write-Host "Retired files: $($manifest.Count)"
Write-Host "Manifest: $manifestPath"
