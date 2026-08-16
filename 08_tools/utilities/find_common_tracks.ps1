param(
    [Parameter(Mandatory = $true)]
    [string[]]$Root
)

$extensions = @(
    ".flac", ".mp3", ".wav", ".m4a",
    ".alac", ".aiff", ".ape"
)

$ExifTool = "C:\Projects\Utilities\ExifTool\exiftool.exe"

if (-not (Test-Path $ExifTool -PathType Leaf)) {
    Write-Error "ExifTool not found: $ExifTool"
    exit 1
}

Write-Host "Scanning $($Root.Count) collection(s)..."

$files = foreach ($rootPath in $Root) {

    if (-not (Test-Path $rootPath -PathType Container)) {
        Write-Warning "Root not found: $rootPath"
        continue
    }

    Write-Host "  $rootPath"

    Get-ChildItem -Path $rootPath -Recurse -File |
        Where-Object {
            $extensions -contains $_.Extension.ToLowerInvariant()
        }
}

Write-Host ""
Write-Host "Files found: $($files.Count)"
Write-Host "Reading embedded metadata with ExifTool..."
Write-Host ""

$paths = $files.FullName

$ExifArgs = @(
    "-json"
    "-FileName"
    "-Directory"
    "-Title"
    "-Artist"
    "-Album"
    "-AlbumArtist"
    "-Date"
    "-Genre"
    "-Duration"
)

$tempList = [System.IO.Path]::GetTempFileName()

$paths | Set-Content -LiteralPath $tempList -Encoding UTF8

try {
    $metadata = & $ExifTool @ExifArgs "-@" $tempList |
        ConvertFrom-Json -AsHashtable
}
finally {
    Remove-Item $tempList -Force -ErrorAction SilentlyContinue
}

$metadata | Select-Object -First 20 |
    ForEach-Object {
        [PSCustomObject]@{
            Title     = $_['Title']
            Artist    = $_['Artist']
            Album     = $_['Album']
            Directory = $_['Directory']
        }
    } | Format-Table -AutoSize
    
$records = foreach ($item in $metadata) {

    if ($item.Artist) {
        $artist = $item.Artist
    }
    elseif ($item.AlbumArtist) {
        $artist = $item.AlbumArtist
    }
    else {
        $artist = ""
    }

    if ($item.Title) {
        $title = $item.Title
    }
    else {
        $title = ""
    }

    $key = $title.ToLowerInvariant()
    $key = $key -replace '[^a-z0-9]+',' '
    $key = $key.Trim()

    $source = ""

foreach ($rootPath in $Root) {
    $rootFull = [System.IO.Path]::GetFullPath($rootPath).TrimEnd('\')
    $dirFull  = [System.IO.Path]::GetFullPath([string]$item.Directory).TrimEnd('\')

    if ($dirFull.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        $source = Split-Path $rootFull -Leaf
        break
    }
}

    foreach ($rootPath in $Root) {
        if ($item.Directory.StartsWith(
            $rootPath,
            [System.StringComparison]::OrdinalIgnoreCase
        )) {
            $source = Split-Path $rootPath -Leaf
            break
        }
    }

    [PSCustomObject]@{
        Key         = $key
        Source      = $source
        Title       = $title
        Artist      = $artist
        Album       = $item.Album
        AlbumArtist = $item.AlbumArtist
        Date        = $item.Date
        Genre       = $item.Genre
        Duration    = $item.Duration
        FileName    = $item.FileName
        Path        = Join-Path $item.Directory $item.FileName
    }
}

Write-Host "Metadata records: $($records.Count)"
Write-Host "Finding title/artist matches across collections..."
Write-Host ""


    Where-Object { $_.Key.Length -gt 3 } |
    Group-Object Key |
    Where-Object {
        ($_.Group.Source | Sort-Object -Unique).Count -gt 1
    }

foreach ($match in $matches) {

    Write-Host "=== $($match.Group[0].Artist) - $($match.Group[0].Title) ==="

    $match.Group |
        Sort-Object Source |
        Format-Table Source, Title, Artist, Album, Date, Duration, FileName -AutoSize

    Write-Host ""
}

Write-Host ""
Write-Host "SOURCE COUNTS:"
$records | Group-Object Source | Format-Table Name, Count -AutoSize

$matches = $records |
    Group-Object Key |
    Where-Object {
        ($_.Group.Source | Sort-Object -Unique).Count -ge 2
    }

Write-Host ""
Write-Host "Potential cross-collection matches: $($matches.Count)"
Write-Host ""

foreach ($match in $matches | Sort-Object Name) {

    Write-Host "============================================================"
    Write-Host "TITLE: $($match.Name)"
    Write-Host ""

    $match.Group |
        Sort-Object Source |
        Format-List Source, Artist, Album, Duration, FileName, Path
}

$matches |
    ForEach-Object { $_.Group } |
    Select-Object Key, Source, Title, Artist, Album, Duration, FileName, Path |
    Export-Csv ".\cross_collection_candidates.csv" -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "Candidate manifest written to:"
Write-Host (Join-Path (Get-Location) "cross_collection_candidates.csv")