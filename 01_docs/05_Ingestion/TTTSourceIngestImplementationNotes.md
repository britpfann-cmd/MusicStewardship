# TTT Source Ingest — Implementation Notes

**Status:** Baseline validated implementation notes  
**Validation date:** 2026-08-29  
**Source:** Tango Time Travel (TTT) audio collections  
**Reference:** TANGO-DJ.AT TTT snapshot captured 2026-08-28

## 1. Conclusion

TTT has been validated as a viable direct source for MusicStewardship ingest.

The source itself supplies enough embedded information to support direct canonical staging without using TANGO-DJ as the primary metadata supplier.

The operational pattern is:

```text
TTT audio file
    ↓
TTT source-specific extraction/decomposition
    ↓
MusicStewardship canonical staging
    ↓
external reference comparison
    ↓
reconciliation / annotation
```

## 2. Embedded TTT metadata observed

The tested files contain:

- `TITLE`
- `ARTIST`
- `album_artist`
- `ALBUM`
- `GENRE`
- `DATE`
- `COMPOSER`
- `CONDUCTOR`
- `CATALOGNUMBER`
- `SOURCEMEDIA`
- `track`
- `COMMENT`
- `ENCODED-BY`

Compound fields are significant source evidence rather than simple display labels.

## 3. TTT compound fields

`ARTIST` may combine:

```text
ensemble / singer
ensemble / Instr.
ensemble / singer / singer
```

The source translator may decompose these into:

- ensemble;
- singer/performer;
- instrumental status;
- performance note.

The raw ARTIST value remains preserved.

`COMPOSER` may contain composer, lyricist, and other credit material.

The raw value remains preserved while recognizable components may be decomposed.

`CATALOGNUMBER` may contain:

```text
Record
Matrix
Take
```

in one source field. These may be decomposed into separate canonical concepts while retaining the original compound value.

`COMMENT` contains meaningful transfer and historical information including pitch, key, score key, instrumentation, arrangement, and restoration observations.

## 4. TTT reference snapshot

The 2026-08-28 TANGO-DJ TTT query snapshot contained:

```text
2,770 recording rows
678 albums
781 unique titles
```

It was saved as two non-overlapping date ranges:

```text
1930–1942    1,450
1943–2027    1,320
-----------------
             2,770
```

The HTML pages are historical source snapshots. The extracted CSV is the machine-readable reference snapshot.

## 5. Direct validation results

A 33-file regression set produced:

```text
33 TTT files
32 matched
0 ambiguous
1 no-reference
```

A complete Edgardo Donato release produced:

```text
42 examined
42 authenticated
0 missing
0 ambiguous
0 probe errors
```

A complete Orquesta Típica Victor release produced 239 examined files. The matching experiments showed that TANGO-DJ may contain multiple reference representations for one TTT performance, including TTT and TTT-Transfer records.

This led to the architectural decision to treat external rows as reference assertions, not as the recording identity.

## 6. Whole-tree baseline

After excluding macOS AppleDouble sidecar files (`._*`), the full TTT tree scan found:

```text
Audio files examined:                 1,095
Probe errors:                             0
Missing required metadata:               0
TANGO-DJ reference candidates:        1,070
No TANGO-DJ reference candidate:         25
```

Therefore the scanned TTT tree is technically and structurally ready for direct ingest.

The 25 reference gaps are not source-ingest failures.

## 7. Source/artifact distinction

The scanner recognizes actual audio formats rather than assuming FLAC is the only valid input.

Current recognized formats include:

```text
FLAC
WAV
MP3
M4A
ALAC
AIFF / AIF
CAF
OGG
OPUS
```

Known filesystem artifacts such as:

```text
._*
.DS_Store
```

are excluded from audio-asset discovery.

Real non-FLAC audio remains eligible for ingest.

## 8. Provenance rule

TTT native values are primary.

TANGO-DJ is used to:

- confirm;
- enrich;
- identify divergences;
- expose omissions;
- provide external identifiers;
- support later human review.

A missing TANGO-DJ reference does not reject a valid TTT file.

## 9. Normalization rule

TTT source values may receive deterministic housekeeping and semantic normalization.

The goal is:

> semantic consistency with reduced ambiguity, while retaining original source evidence.

External TANGO-DJ transposition conventions are not reverse-engineered merely to force agreement.

## 10. Whole-tree source structure

The TTT tree contains nested release packaging and multiple release representations.

Examples include nested Pedro Laurenz release directories and multiple Pugliese releases.

Directory hierarchy is source context and provenance; it should not be flattened destructively.

## 11. Current implementation capability

Current tested tooling supports:

```text
ffprobe-based audio inspection
TTT metadata extraction
TTT compound-field decomposition
reference snapshot extraction
source/reference comparison
whole-tree validation
per-release validation
canonical staging
resumable processing ledger
human-readable ledger export
```

## 12. Current boundary

The validated implementation stops before permanent database catalog creation.

Current next action after reconciliation is:

```text
CATALOG
```

Materialization is a separate downstream operation.
