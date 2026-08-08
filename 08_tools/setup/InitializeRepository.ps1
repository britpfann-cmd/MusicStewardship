<#
.SYNOPSIS
    Restructure the MusicStewardship repository.

.DESCRIPTION
    Creates the standard repository layout and relocates selected files
    into their canonical locations.

    Safe to run multiple times.
#>

$ProjectRoot = Get-Location

Write-Host ""
Write-Host "Music Stewardship Repository Layout"
Write-Host "Root: $ProjectRoot"
Write-Host ""

# --------------------------------------------------------------------
# Create top-level directories
# --------------------------------------------------------------------

$directories = @(
    "assets",
    "assets\audio",
    "assets\artwork",
    "data",
    "docs",
    "docs\Architecture",
    "docs\Decisions",
    "docs\Implementation",
    "docs\Notes",
    "docs\Reference",
    "docs\Research",
    "docs\Specifications",
    "docs\Specifications\Appendices",
    "examples",
    "generated",
    "generated\flac",
    "generated\mp3",
    "generated\manifests",
    "generated\reports",
    "src",
    "tests",
    "tools"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

# --------------------------------------------------------------------
# Move known documentation files
# --------------------------------------------------------------------

function Move-IfExists {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (Test-Path $Source) {
        if (-not (Test-Path $Destination)) {
            Write-Host "Moving $Source"
            Move-Item $Source $Destination
        }
        else {
            Write-Host "Skipping $Source (destination exists)"
        }
    }
}

Move-IfExists `
    "Appendix A – Initial Vocabulary.md" `
    "docs\Specifications\Appendices\AppendixA-InitialVocabulary.md"

# --------------------------------------------------------------------
# Create placeholder files
# --------------------------------------------------------------------

$placeholders = @(
    "data\PerformanceObjects.csv",
    "data\ExportProfiles.csv",
    "assets\audio\.gitkeep",
    "generated\.gitkeep",
    "examples\.gitkeep",
    "tests\.gitkeep",
    "tools\.gitkeep"
)

foreach ($file in $placeholders) {

    if (-not (Test-Path $file)) {
        New-Item -ItemType File -Path $file | Out-Null
    }

}

# --------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------

Write-Host ""
Write-Host "Repository structure complete."
Write-Host ""

tree /F