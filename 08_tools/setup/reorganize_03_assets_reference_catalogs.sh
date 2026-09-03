#!/usr/bin/env bash
set -euo pipefail

# Reorganize 03_assets/ReferenceCatalogs into dated external-reference snapshots.
# Run from the MusicStewardship project root:
#   bash ./08_tools/setup/reorganize_03_assets_reference_catalogs.sh
#
# Conservative behavior:
#   * creates the target structure
#   * moves only matching FILES and their companion _files DIRECTORIES
#     from the TOP LEVEL of ReferenceCatalogs
#   * never moves the target TANGO-DJ_AT directory itself
#   * never overwrites an existing destination
#   * never deletes anything

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REF="$ROOT/03_assets/ReferenceCatalogs"
TDJ="$REF/TANGO-DJ_AT/2026-08-28/TTT"
SRC="$TDJ/source"
EXTRACTED="$TDJ/extracted"

if [[ ! -d "$REF" ]]; then
    echo "ERROR: ReferenceCatalogs not found: $REF" >&2
    exit 1
fi

mkdir -p "$SRC" "$EXTRACTED"

echo "Created/verified:"
echo "  $SRC"
echo "  $EXTRACTED"
echo

# Move only files directly inside ReferenceCatalogs.
# This deliberately avoids recursive directory traversal so that an
# already-created TANGO-DJ_AT tree cannot be moved into itself.
while IFS= read -r -d '' f; do
    base="$(basename "$f")"

    case "$base" in
        *TTT*|*"Tango Database"*|*"TANGO-DJ"*)
            if [[ -e "$SRC/$base" ]]; then
                echo "SKIP FILE (destination exists): $SRC/$base"
            else
                mv "$f" "$SRC/$base"
                echo "MOVED FILE:"
                echo "  $f"
                echo "  -> $SRC/$base"
            fi
            ;;
    esac
done < <(find "$REF" -maxdepth 1 -type f -print0)

# Move only matching companion directories directly inside ReferenceCatalogs.
while IFS= read -r -d '' d; do
    base="$(basename "$d")"

    case "$base" in
        *TTT*|*"Tango Database"*|*"TANGO-DJ"*)
            if [[ "$d" == "$REF/TANGO-DJ_AT" ]]; then
                echo "KEEP EXISTING ROOT DIRECTORY: $d"
                continue
            fi

            if [[ -e "$SRC/$base" ]]; then
                echo "SKIP DIR (destination exists): $SRC/$base"
            else
                mv "$d" "$SRC/$base"
                echo "MOVED DIR:"
                echo "  $d"
                echo "  -> $SRC/$base"
            fi
            ;;
    esac
done < <(find "$REF" -maxdepth 1 -mindepth 1 -type d -print0)

echo
echo "Current ReferenceCatalogs tree (max depth 6):"
find "$REF" -maxdepth 6 -print | sort

echo
echo "Done. No files were deleted or overwritten."
