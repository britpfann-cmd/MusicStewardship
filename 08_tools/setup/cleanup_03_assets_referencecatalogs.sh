#!/usr/bin/env bash
set -euo pipefail

# Clean up legacy 03_assets/ReferenceCatalogs layout.
#
# Current intended structure:
#   03_assets/ReferenceCatalogs/
#     TANGO-DJ_AT/
#       2026-08-27/CracklingTunes/source/
#       2026-08-28/TTT/source/
#     CracklingTunes/
#     TangoTimeTravel/
#     TangoTunes/
#     ToTango/
#     TangoSparks/
#
# This script only moves the known legacy TANGO-DJ saved pages/directories.
# It never overwrites or deletes files.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REF="$ROOT/03_assets/ReferenceCatalogs"
LEGACY="$REF/Tango.DJ-AT"

CRACK="$REF/TANGO-DJ_AT/2026-08-27/CracklingTunes/source"
TTT="$REF/TANGO-DJ_AT/2026-08-28/TTT/source"

if [[ ! -d "$REF" ]]; then
    echo "ERROR: ReferenceCatalogs not found: $REF" >&2
    exit 1
fi

mkdir -p "$CRACK" "$TTT"

move_safe() {
    local src="$1"
    local dest_dir="$2"
    local base
    base="$(basename "$src")"

    if [[ ! -e "$src" ]]; then
        return 0
    fi

    if [[ -e "$dest_dir/$base" ]]; then
        echo "SKIP (destination exists): $dest_dir/$base"
        return 0
    fi

    mv "$src" "$dest_dir/$base"
    echo "MOVED:"
    echo "  $src"
    echo "  -> $dest_dir/$base"
}

# Legacy Crackling Tunes saved page + companion folder.
move_safe \
    "$LEGACY/Crackling Tunes query - TANGO-DJ.AT » Tango Database, Bernhard Gehberger.htm" \
    "$CRACK"

move_safe \
    "$LEGACY/Crackling Tunes query - TANGO-DJ.AT » Tango Database, Bernhard Gehberger_files" \
    "$CRACK"

# TTT full-result saved page from 2026-08-28.
# The companion _files directory, if any, is moved as well.
move_safe \
    "$LEGACY/TANGO-DJ_TTT_2026-08-28_all-query_1500.html" \
    "$TTT"

move_safe \
    "$LEGACY/TTT files in TANGO-DJ.AT » Tango Database.htm" \
    "$TTT"

# If the legacy directory is now empty, remove the EMPTY directory only.
if [[ -d "$LEGACY" ]]; then
    if [[ -z "$(find "$LEGACY" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
        rmdir "$LEGACY"
        echo "REMOVED EMPTY DIRECTORY:"
        echo "  $LEGACY"
    else
        echo
        echo "LEGACY DIRECTORY STILL CONTAINS OTHER FILES:"
        find "$LEGACY" -maxdepth 2 -print | sort
        echo
        echo "Nothing else was moved or deleted."
    fi
fi

echo
echo "Resulting ReferenceCatalogs structure:"
find "$REF" -maxdepth 6 -print | sort

echo
echo "Done. No files were overwritten; only the empty legacy directory may have been removed."
