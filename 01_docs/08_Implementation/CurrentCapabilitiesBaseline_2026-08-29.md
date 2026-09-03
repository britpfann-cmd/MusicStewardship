# MusicStewardship — Current Capabilities Baseline

**Baseline date:** 2026-08-29  
**Purpose:** Record the tested capability level at the end of the current TTT ingest-development cycle.

## 1. Source collection baseline

The TTT source tree currently scanned contains:

```text
1,095 recognized audio files
0 probe errors
0 missing required metadata files
```

The scanner recognizes real audio formats including FLAC, WAV, MP3, M4A, ALAC, AIFF/AIF, CAF, OGG, and OPUS.

Known macOS filesystem artifacts such as `._*` and `.DS_Store` are excluded from audio discovery.

## 2. TTT metadata handling

Tested capability includes direct reading of:

```text
TITLE
ARTIST
album_artist
ALBUM
GENRE
DATE
COMPOSER
CONDUCTOR
CATALOGNUMBER
SOURCEMEDIA
track
COMMENT
ENCODED-BY
```

Compound TTT fields can be decomposed into useful canonical concepts while the raw field remains source evidence.

## 3. Reference snapshot capability

A complete TANGO-DJ TTT snapshot was captured on 2026-08-28:

```text
2,770 rows
678 albums
781 unique titles
```

The snapshot was captured in two non-overlapping HTML queries and extracted to CSV.

## 4. TTT validation results

Validated examples include:

```text
33-file regression set
32 matched
0 ambiguous
1 no reference

Edgardo Donato release
42 / 42 authenticated
0 probe errors

Orquesta Típica Victor release
239 files examined
0 missing reference records
```

The Victor tests established that TANGO-DJ may contain multiple reference representations of the same TTT recording.

## 5. Whole-tree reference coverage

Whole-tree reference scan:

```text
1,095 audio files
1,070 with TANGO-DJ candidates
25 without TANGO-DJ candidates
```

The 25 are a reference-coverage/reporting issue, not an ingest rejection condition.

## 6. Provenance architecture

Established rule:

```text
native source = primary evidence

external reference = confirmation/enrichment/divergence evidence
```

No requirement exists to reproduce TANGO-DJ's internal transposition method.

## 7. Normalization architecture

Established distinction:

```text
housekeeping normalization
    ↓
semantic normalization
    ↓
source/reference comparison
```

Normalization may reduce ambiguity when the rule is deterministic and meaning-preserving.

Original source values remain recoverable.

## 8. Processing ledger

A SQLite-backed processing ledger has been built and successfully tested.

Proven behavior:

```text
asset registration
PROBE
SCREEN
TRANSLATE
REFERENCE_CHECK
RECONCILE
current lifecycle state
next action
event history
retry attempt structure
```

The automated three-file TTT test completed:

```text
3 processed
3 complete
0 failed
```

One asset history demonstrated:

```text
PROBE            SUCCESS
SCREEN           SUCCESS
TRANSLATE        SUCCESS
REFERENCE_CHECK  SUCCESS
RECONCILE        SUCCESS

current state = RECONCILED
next action    = CATALOG
```

## 9. Human-readable ledger

The ledger now supports Markdown output containing:

```text
overall summary
current lifecycle summary
next-action summary
exception summary
per-asset detail
processing history
```

SQLite is the operational store; Markdown is the human-readable view.

## 10. Materialization architecture

Current design supports the concept of:

```text
one Recording
    ├── source AudioAsset
    ├── managed/master AudioAsset
    ├── DJ destination AudioAsset
    └── phone/other destination AudioAsset
```

The materialization workflow is manifest-driven and non-destructive.

The preferred managed/master format is FLAC when the source is lossless.

Purpose-specific derived formats are permitted.

## 11. Multi-copy selection

The architecture now explicitly supports multiple copies of one performance and selection of:

```text
BEST
PREFERRED
CONTEXT_PREFERRED
```

Playlist construction is intended to select an appropriate AudioAsset rather than making the filename or external reference row the identity.

## 12. Not yet production-complete

The following remain future implementation work:

- permanent database catalog creation;
- batch/job-level ledger dashboard;
- automated full-tree ingestion into the production ledger;
- complete divergence/feedback reporting;
- destination profile registry and implementation;
- best/preferred asset scoring/selection rules;
- final canonical filename and metadata policies;
- full materialization execution/validation;
- broader multi-source ingestion beyond the currently tested source workflows.

## 13. Baseline decision

At this baseline, TTT direct ingest is considered **technically validated for continued development**.

The next work should concentrate on:

```text
ledger-backed whole-tree ingest
        ↓
canonical staging
        ↓
reference annotation
        ↓
catalog
        ↓
materialization
```

without making external reference matching a gate for possessed music.
