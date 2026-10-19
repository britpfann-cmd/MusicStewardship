# Verified research backup utility

`research_backup.py` uses only Python's standard library and the installed Git CLI.
It preserves the working project, including ignored research/runtime/transfer data,
and the complete standalone `.git` directory. It never fetches or pushes.

## Before the first real backup

The architect must supply the actual expected UNC share root for `Z:` (for example,
`\\NAS-name\share-name`; this is a placeholder, not an established destination).
The utility checks Windows' drive mapping and requires an exact, case-insensitive
UNC-root match. This verifies the mapping, not the hardware identity of a Synology
device. Confirm share ownership, permissions, free space, and server identity first.

Stop all project editors/automation, ingestion, SQLite writers, and Git operations.
Capture consistency across files/databases depends on this quiescent window.
The utility compares complete source inventories before/after capture and before
completion, but these comparisons are not a filesystem snapshot or an exclusive lock.

The command-line destination is fixed to `Z:\`. Each real invocation creates a new
directory directly beneath it:

```text
Z:\MusicStewardship_<UTC timestamp>_<random suffix>\
    payload\project\...        working files and full .git; SQLite snapshots
    raw_sqlite\...             original DB bytes and any WAL/SHM/journal companions
    git\repository.bundle     all Git refs
    metadata\capture.json      source inventory, timestamps, refs, exclusions, DB checks
    metadata\manifest.json     artifact sizes/SHA-256 and directory inventory
    metadata\manifest.sha256   manifest checksum
    metadata\verification.json
    COMPLETE.json              created last, only following successful restoration
```

No parent `MusicStewardship_Backups` directory is added. Existing backup directories
and files are never reused, overwritten, pruned, or deleted. Failed NAS transfers
remain incomplete for human investigation; the utility does not clean them up.
Only its own disposable local capture/restore directories are automatically cleaned.

## Dry-run

After the actual share has been identified, the following is a template command:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
.\.venv\Scripts\python.exe -B .\08_tools\maintenance\research_backup.py --expected-share '\\NAS-name\share-name' --dry-run
```

Dry-run checks mapping/accessibility, inventories/hashes included source files,
identifies SQLite headers, and prints the complete intended inventory as JSON.
It creates no directories, reports, bundles, or database snapshots. It does not test
write permissions, free-space sufficiency, SQLite integrity, or restoration.
No actual NAS dry-run or real backup was performed during implementation.

For an explicitly authorized real capture, remove `--dry-run` and add `--quiesced`
only after writers have stopped. The flag is operator confirmation, not an automatic
writer shutdown mechanism. Do not run a real backup until the first-run questions
above are resolved.

## Included and excluded information

`.gitignore` is not used as a backup exclusion list. Source evidence, runtime logs,
reports, ZIP transfer packages, historical `.bak` files, and empty directories are
included. Untracked virtual environments identified by `pyvenv.cfg`, untracked
`__pycache__` and `.pytest_cache` directories, and untracked `.pyc`/`.pyo` files
are excluded. A research directory merely named `env` is retained. Tracked content takes
precedence over cache-directory exclusions. Python environments are reconstructed
separately; the verified development baseline is Python 3.12.5 and pytest 9.1.1.

Links/reparse points and nonregular entries abort capture instead of silently
omitting evidence or traversing external music/network collections. Linked Git
worktrees, Git alternates, and nested `.git` pointer files require separate handling.
Local Git locks abort capture. File timestamps are retained where supported;
directory names/empty directories are restored, but ACLs, alternate data streams,
and complete Windows filesystem security metadata are not backed up by this utility.

## SQLite consistency and verification

The live source databases are never opened with SQLite. Their exact bytes and any
sidecars are first copied into an isolated capture and checked against source hashes.
SQLite's backup API then operates on another disposable copy, allowing local WAL
recovery without altering source evidence or the retained raw capture. Each logical
snapshot gets integrity, schema, row-count, and foreign-key checks. Integrity/schema/
count failures abort. Existing foreign-key violations are reported without repair;
they do not silently change evidence or automatically invalidate an otherwise
faithful preservation set.

Snapshots are restored at their original project-relative paths. Raw sidecars are
kept outside the restored project to prevent accidental replay against transformed
snapshots. Do not manually combine raw WAL files with logical snapshot databases.

Every artifact is hashed locally and checked again on the destination. Restoration
reads back from the mock/real destination into a separate temporary local directory,
checks hashes and empty directories, runs Git fsck on the copied repository, verifies
and mirror-clones the local bundle, checks refs/HEAD, and validates restored SQLite
schema/counts/integrity. No production project is used as a restoration target.

`COMPLETE.json` records the manifest and verification-report checksums. Its presence
alone is insufficient: it must be valid JSON and its referenced checksums must match.
SHA-256 detects corruption, not malicious replacement of both data and manifests.
Restrict NAS access and keep a separately protected/offsite copy or trusted manifest
hash. Mapped-drive checks cannot prevent all disconnect/remapping races; interrupted
or unverifiable writes fail rather than being accepted as successful backups.

## Resource requirements and tests

Allow generous temporary local disk space: the implementation holds a raw capture,
publication stage, disposable SQLite working copies, and a restored verification
copy. NAS space must accommodate all prior independent sets plus the new set, raw
database evidence, and bundle. No retention policy or scheduler is implemented.

Tests use temporary Git repositories, databases, and mocked share mappings:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider 07_tests/maintenance/test_research_backup.py
```

The tests never access `Z:` or persistent project research. Actual Windows mapping,
SMB permissions/durability, NAS snapshots, and an on-device restoration rehearsal
remain first-run acceptance checks. No Dropbox, synchronization, or scheduling is
configured.
