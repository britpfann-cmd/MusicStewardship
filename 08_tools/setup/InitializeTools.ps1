<#
------------------------------------------------------------------------------
InitializeTools.ps1

Creates the standard Music Stewardship tools directory.

Safe to run multiple times.
------------------------------------------------------------------------------
#>

$ProjectRoot = Get-Location
$ToolsRoot = Join-Path $ProjectRoot "08_tools"

Write-Host ""
Write-Host "Initializing Tools Repository..."
Write-Host ""

# ---------------------------------------------------------------------------
# Standard directories
# ---------------------------------------------------------------------------

$Directories = @(
    "setup",
    "maintenance",
    "import",
    "export",
    "utilities"
)

foreach ($dir in $Directories)
{
    $path = Join-Path $ToolsRoot $dir

    if (!(Test-Path $path))
    {
        New-Item -ItemType Directory -Path $path | Out-Null
        Write-Host "Created $dir"
    }
}

# ---------------------------------------------------------------------------
# README generator
# ---------------------------------------------------------------------------

function New-Readme
{
    param($Folder)

    $Readme = Join-Path $Folder "README.md"

    if (!(Test-Path $Readme))
    {
        $Name = Split-Path $Folder -Leaf

@"
# $Name

## Purpose

Describe the purpose of this directory.

---

## Contents

| File | Purpose |
|------|---------|

---

## Notes

Additional stewardship notes.

"@ | Set-Content $Readme

        Write-Host "Created README.md in $Name"
    }
}

# Root README
New-Readme $ToolsRoot

foreach ($dir in $Directories)
{
    New-Readme (Join-Path $ToolsRoot $dir)
}

# ---------------------------------------------------------------------------
# Placeholder scripts
# ---------------------------------------------------------------------------

$Scripts = @(
    "setup\InitializeRepository.ps1",
    "setup\InitializeDocumentation.ps1",
    "setup\Initialize02-Data.ps1",
    "setup\Initialize03-Assets.ps1",

    "maintenance\ValidateRepository.ps1",
    "maintenance\RebuildGeneratedFiles.ps1",
    "maintenance\UpdateReadmeFiles.ps1"
)

foreach ($script in $Scripts)
{
    $Path = Join-Path $ToolsRoot $script

    if (!(Test-Path $Path))
    {
@"
<#
------------------------------------------------------------------------------

$(Split-Path $script -Leaf)

Purpose:

TODO

------------------------------------------------------------------------------
#>

Write-Host "TODO"

"@ | Set-Content $Path

        Write-Host "Created $script"
    }
}

Write-Host ""
Write-Host "Tools repository initialized."