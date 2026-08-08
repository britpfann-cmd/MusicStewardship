<#
------------------------------------------------------------------------------
Initialize02-Data.ps1

Creates the standard Music Stewardship canonical data repository.

Safe to run multiple times.

------------------------------------------------------------------------------
#>

$ProjectRoot = Get-Location
$DataRoot = Join-Path $ProjectRoot "02_data"

Write-Host ""
Write-Host "Initializing Canonical Data Repository..."
Write-Host ""

#------------------------------------------------------------------------------
# Helper Functions
#------------------------------------------------------------------------------

function Ensure-Directory
{
    param([string]$Path)

    if (!(Test-Path $Path))
    {
        New-Item -ItemType Directory -Path $Path | Out-Null
        Write-Host "Created directory: $Path"
    }
}

function Ensure-File
{
    param(
        [string]$Path,
        [string]$Content = ""
    )

    if (!(Test-Path $Path))
    {
        Set-Content -Path $Path -Value $Content
        Write-Host "Created file: $Path"
    }
}

#------------------------------------------------------------------------------
# Directory Structure
#------------------------------------------------------------------------------

$Directories = @(
    "01_dictionary",
    "02_vocabularies",
    "03_entities",
    "04_models",
    "05_exports"
)

foreach ($dir in $Directories)
{
    Ensure-Directory (Join-Path $DataRoot $dir)
}

#------------------------------------------------------------------------------
# Root README
#------------------------------------------------------------------------------

Ensure-File `
    (Join-Path $DataRoot "README.md") `
@"
# Canonical Data Repository

This directory contains the canonical data assets used throughout
Music Stewardship.

## Directory Layout

01_dictionary
: Canonical data definitions.

02_vocabularies
: Controlled vocabularies.

03_entities
: Canonical entity datasets.

04_models
: Object and relationship models.

05_exports
: Export profile definitions.

"@

#------------------------------------------------------------------------------
# Dictionary
#------------------------------------------------------------------------------

Ensure-File `
    (Join-Path $DataRoot "01_dictionary\README.md") `
@"
# Dictionary

Authoritative definitions of every canonical data element.

Files

- DataDictionary.csv
- DataTypes.csv
- ObjectTypes.csv
"@

Ensure-File `
    (Join-Path $DataRoot "01_dictionary\DataDictionary.csv") `
"CanonicalID,Domain,ObjectType,FieldName,DisplayName,ParentObject,DataType,Required,Cardinality,Vocabulary,Units,DefaultValue,Example,Description,ValidationRule,IntroducedVersion,DeprecatedVersion,Status,Notes"

Ensure-File `
    (Join-Path $DataRoot "01_dictionary\DataTypes.csv") `
"DataType,Description"

Ensure-File `
    (Join-Path $DataRoot "01_dictionary\ObjectTypes.csv") `
"ObjectType,Description"

#------------------------------------------------------------------------------
# Controlled Vocabularies
#------------------------------------------------------------------------------

Ensure-File `
    (Join-Path $DataRoot "02_vocabularies\README.md") `
@"
# Controlled Vocabularies

Authoritative lists of allowable values.

Files

- Genres.csv
- Languages.csv
- MediaFormats.csv
- SourceTypes.csv
"@

Ensure-File `
    (Join-Path $DataRoot "02_vocabularies\Genres.csv") `
"CanonicalID,Genre,Description"

Ensure-File `
    (Join-Path $DataRoot "02_vocabularies\Languages.csv") `
"CanonicalID,Language,ISOCode"

Ensure-File `
    (Join-Path $DataRoot "02_vocabularies\MediaFormats.csv") `
"CanonicalID,MediaFormat,Description"

Ensure-File `
    (Join-Path $DataRoot "02_vocabularies\SourceTypes.csv") `
"CanonicalID,SourceType,Description"

#------------------------------------------------------------------------------
# Entities
#------------------------------------------------------------------------------

Ensure-File `
    (Join-Path $DataRoot "03_entities\README.md") `
@"
# Canonical Entities

Definitions of real-world entities.

Suggested datasets

- People.csv
- Organizations.csv
- Works.csv
- Sources.csv
"@

Ensure-File `
    (Join-Path $DataRoot "03_entities\People.csv") `
"CanonicalID,DisplayName"

Ensure-File `
    (Join-Path $DataRoot "03_entities\Organizations.csv") `
"CanonicalID,OrganizationName"

Ensure-File `
    (Join-Path $DataRoot "03_entities\Works.csv") `
"CanonicalID,Title"

Ensure-File `
    (Join-Path $DataRoot "03_entities\Sources.csv") `
"CanonicalID,SourceName"

#------------------------------------------------------------------------------
# Models
#------------------------------------------------------------------------------

Ensure-File `
    (Join-Path $DataRoot "04_models\README.md") `
@"
# Canonical Models

Object models derived from the canonical dictionary.

Files

- PerformanceObjects.csv
"@

Ensure-File `
    (Join-Path $DataRoot "04_models\PerformanceObjects.csv") `
"CanonicalID,ObjectName,ObjectType,ParentObject,Description"

#------------------------------------------------------------------------------
# Export Profiles
#------------------------------------------------------------------------------

Ensure-File `
    (Join-Path $DataRoot "05_exports\README.md") `
@"
# Export Profiles

Mappings from the canonical model to external applications.
"@

Ensure-File `
    (Join-Path $DataRoot "05_exports\ExportProfiles.csv") `
"ProfileName,TargetApplication,Description"

Write-Host ""
Write-Host "Canonical data repository initialized successfully."
Write-Host ""