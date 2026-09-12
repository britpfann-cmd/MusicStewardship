param(
    [ValidateSet("01","02","03","04","05","ALL")]
    [string]$Subject = "ALL",
    [string]$Revision = "A"
)

$ErrorActionPreference = "Stop"
$root = "C:\Projects\MusicStewardship"
$out = Join-Path $root "_to_chat"
$legacyZip = Join-Path $out "02_ALL_TTT_MATERIAL.zip"
$temp = Join-Path $env:TEMP ("MusicStewardship_TTT_Archaeology_" + [guid]::NewGuid().ToString("N"))

New-Item -ItemType Directory -Force $out | Out-Null
New-Item -ItemType Directory -Force $temp | Out-Null

try {
    # The consolidated TTT package is treated as historical source material.
    if (Test-Path $legacyZip) {
        Expand-Archive -LiteralPath $legacyZip -DestinationPath $temp -Force
    }

    $subjectDefs = [ordered]@{
        "01" = @{
            Name = "SOURCE_ARCHAEOLOGY"
            Files = @(
                "TTT_source_root.txt",
                "TTT_root_contents.txt",
                "TTT_top_level.txt",
                "TTT_structure.txt",
                "TTT_collection_profile.txt",
                "TTT_audio_locations.txt",
                "ttt_files.txt",
                "ttt_genres.txt",
                "TTT_Anibal_Troilo_structure.txt",
                "TTT_Troilo_structure.txt",
                "TTT_Troilo_documents.txt",
                "TTT_Troilo_discography.pdf",
                "TangoTimeTravel_v3_baseline.yaml"
            )
        }
        "02" = @{
            Name = "GRAMMAR_ARCHAEOLOGY"
            Files = @(
                "ttt_old_grammar_sample.txt",
                "ttt_old_rule_summary.txt",
                "TTT_grammar_ingest_v2_baseline.csv",
                "TTT_comment_classification.xlsx",
                "TTT_compound_field_analysis.xlsx",
                "TTT_other_clause_analysis.xlsx",
                "TTT_unclassified_clause_analysis.xlsx",
                "TTT_pattern_transformations.xlsx",
                "TTT_full_transformation_pass.xlsx"
            )
        }
        "03" = @{
            Name = "TRANSFORMATION_ARCHAEOLOGY"
            Files = @(
                "ttt_old_staging_core.txt",
                "TTT_pattern_transformations.xlsx",
                "TTT_full_transformation_pass.xlsx",
                "TTT_grammar_ingest_v2_baseline.csv",
                "Crackling_Tunes_Rosetta_Stone.md",
                "Source_Ingestion_and_Transformation_Architecture.md",
                "New-IngestionFramework.ps1",
                "crackling_tunes_rosetta.csv",
                "TangoTimeTravel.yaml",
                "TangoTunes.yaml",
                "tango_sources.yaml"
            )
        }
        "04" = @{
            Name = "SEMANTIC_ARCHAEOLOGY"
            Files = @(
                "TTT_compound_field_analysis.xlsx",
                "TTT_comment_classification.xlsx",
                "TTT_other_clause_analysis.xlsx",
                "TTT_unclassified_clause_analysis.xlsx",
                "TTT_Anibal_Troilo_structure.txt",
                "TTT_Troilo_structure.txt",
                "TTT_TANGO-DJ_2026-08-28.csv",
                "CanonicalDataModel.md",
                "EntityIdentity.md",
                "NameAndAliasModel.md",
                "DateModel.md",
                "PerformanceModel.md"
            )
        }
        "05" = @{
            Name = "EVIDENCE_AND_PROVENANCE_ARCHAEOLOGY"
            Files = @(
                "TTT_TANGO-DJ_2026-08-28.csv",
                "TTT_Troilo_discography.pdf",
                "TTT_Troilo_documents.txt",
                "TangoTimeTravel_v3_baseline.yaml",
                "EvidenceAndProvenance.md",
                "ReferenceRecordStaging.md",
                "Audio_Derived_Identity_Evidence.md",
                "TraceabilityTaggingStandard.md",
                "TraceabilityReview_2026-09-01.md"
            )
        }
    }

    function Find-Candidate {
        param([string]$FileName)

        $roots = @(
            $temp,
            (Join-Path $root "01_docs"),
            (Join-Path $root "02_data"),
            (Join-Path $root "03_assets"),
            (Join-Path $root "08_tools")
        ) | Where-Object { Test-Path $_ }

        foreach ($r in $roots) {
            $hit = Get-ChildItem -LiteralPath $r -Recurse -File -Filter $FileName -ErrorAction SilentlyContinue |
                   Select-Object -First 1
            if ($hit) { return $hit.FullName }
        }
        return $null
    }

    $keys = if ($Subject -eq "ALL") { @("01","02","03","04","05") } else { @($Subject) }

    foreach ($key in $keys) {
        $def = $subjectDefs[$key]
        $stage = Join-Path $temp ("SUBJECT_" + $key)
        New-Item -ItemType Directory -Force $stage | Out-Null

        $manifest = New-Object System.Collections.Generic.List[string]
        $manifest.Add("MusicStewardship TTT Exploratory Discovery Package")
        $manifest.Add("Subject: $key - $($def.Name)")
        $manifest.Add("Transfer revision: $Revision")
        $manifest.Add("Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
        $manifest.Add("")
        $manifest.Add("Purpose: historical/exploratory discovery material recovered from earlier TTT/tango.dj-at work.")
        $manifest.Add("Disposition: REFERENCE / REUSE / INCORPORATE / SUPERSEDE will be determined during archaeology review.")
        $manifest.Add("Nothing in this package is presumed to be current architecture merely because it is included.")
        $manifest.Add("")
        $manifest.Add("Files requested:")

        foreach ($name in $def.Files) {
            $src = Find-Candidate $name
            if ($src) {
                $safeName = Split-Path $src -Leaf
                $dest = Join-Path $stage $safeName
                Copy-Item -LiteralPath $src -Destination $dest -Force
                $manifest.Add("INCLUDED  $name  <=  $src")
            } else {
                $manifest.Add("NOT FOUND $name")
            }
        }

        # Include the current architecture statement as context only for subject 03.
        if ($key -eq "03") {
            $arch = Join-Path $root "01_docs\02_Architecture\Orthogonal_Ingestion_Universe.md"
            if (Test-Path $arch) {
                Copy-Item $arch (Join-Path $stage "Orthogonal_Ingestion_Universe.md") -Force
                $manifest.Add("CONTEXT   Orthogonal_Ingestion_Universe.md")
            }
        }

        $manifest | Set-Content (Join-Path $stage "PACKAGE_MANIFEST.txt") -Encoding UTF8

        $zipName = "0${key}_TTT_DISCOVERY_$($def.Name)_$Revision.zip"
        $zipPath = Join-Path $out $zipName

        if (Test-Path $zipPath) {
            Remove-Item $zipPath -Force
        }

        Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $zipPath -CompressionLevel Optimal

        $sizeMB = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)
        Write-Host ("CREATED  {0}  ({1} MB)" -f $zipName, $sizeMB)
    }
}
finally {
    if (Test-Path $temp) {
        Remove-Item $temp -Recurse -Force -ErrorAction SilentlyContinue
    }
}
