# Create-ObjectSpecifications.ps1
#
# Generates object specification stubs from the canonical template.
#

$templateFile = ".\01_docs\Specifications\ObjectSpecificationTemplate.md"
$objectList   = ".\01_docs\Specifications\ObjectList.txt"
$targetDir    = ".\01_docs\Specifications"

if (-not (Test-Path $templateFile)) {
    Write-Error "Template file not found: $templateFile"
    exit 1
}

if (-not (Test-Path $objectList)) {
    Write-Error "Object list not found: $objectList"
    exit 1
}

$template = Get-Content $templateFile -Raw

$Objects = Get-Content $objectList |
    ForEach-Object { $_.Trim() } |
    Where-Object {
        $_ -ne "" -and
        -not $_.StartsWith("#")
    }

foreach ($Object in $Objects) {

    $file = Join-Path $targetDir "$Object.md"

    if (-not (Test-Path $file)) {

        $content = $template.Replace('{{ObjectName}}', $Object)

        Set-Content `
            -Path $file `
            -Value $content `
            -Encoding UTF8

        Write-Host "Created $file"
    }
    else {
        Write-Host "Skipped existing $file"
    }
}

Write-Host ""
Write-Host "Object specification generation complete."
