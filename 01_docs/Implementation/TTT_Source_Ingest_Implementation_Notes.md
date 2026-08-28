# TTT Source Ingest — Implementation Notes

**Status:** Validated against real TTT files and a complete TANGO-DJ/TTT reference snapshot  
**Validation date:** 2026-08-28  
**Source:** Tango Time Travel (TTT) FLAC collections  
**Reference:** TANGO-DJ.AT snapshot captured 2026-08-28

## Purpose

TTT has now been tested as a direct source for MusicStewardship ingestion.

The governing pattern is:

```text
TTT audio file
    ↓
source-specific TTT translator
    ↓
MusicStewardship canonical staging record
    ↓
independent reference authentication
    ├── TANGO-DJ.AT
    ├── other trusted sources
    └── acoustic matching when necessary
```

TANGO-DJ.AT is **not** the primary metadata supplier for a TTT ingest. It is an independent reference used to authenticate identity, discover omissions, and expose discrepancies.

## Evidence from the TTT files

A 33-file regression set was probed directly from the TTT audio collection. The files contained these embedded tags:

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

The tags carry substantially more information than simple playback labels.

### Compound fields

`ARTIST` is a source-specific compound field. Examples include:

```text
Aníbal Troilo / F. Fiorentino y A. Mandarino
Carlos Di Sarli / Roberto Rufino
Rodolfo Biagi / Instr. (solo de piano)
```

The translator therefore treats the field as evidence from which to derive:

- ensemble / primary performing entity
- vocalist or other performer(s), when present
- instrumental indication
- performance note

`album_artist` is retained separately as the primary ensemble/leader representation.

`COMPOSER` may contain more than the composer. Examples include:

```text
Antonio Bonavena, Lyrics: Lito Bayardo
Miguel Bucino, Lyrics: Miguel Bucino
M. Mores - P. Cour - Vers. cast.: A. L. Martínez
```

The translator therefore preserves the raw value while deriving composer, lyricist, and other credit information where recognizable.

`CATALOGNUMBER` is not a simple catalog-number field in the TTT files. It commonly bundles several pieces of recording evidence:

```text
Record: 39299-B, Matrix: 39981, Take: 1
```

or:

```text
Record: LDS 103 (55539), Matrix L.D. 35015 (18024/1)
```

The translator derives:

- record number
- matrix number
- take number

while retaining the original compound value as source evidence.

### COMMENT is structured source evidence

TTT `COMMENT` is not merely miscellaneous notes. The tested files contain:

- transfer pitch (`A4:435Hz`, `A4:440Hz`, `A4:442Hz`)
- key
- score key
- solo/instrumentation information
- arrangement/tempo observations
- recording-context observations
- historical notes and qualifications

The implementation therefore preserves `COMMENT` verbatim and extracts selected structured observations such as pitch and key.

## Reference authentication

A complete TTT/TANGO-DJ reference snapshot was captured on 2026-08-28.

The original TANGO-DJ TTT query reported:

```text
2,770 results
678 albums
781 unique titles
```

The result was captured as two non-overlapping date ranges because the display limit was 1,500 records:

```text
1930–1942    1,450 records
1943–2027    1,320 records
-------------------------
             2,770 records
```

The two saved HTML pages are the immutable source snapshots. The extracted 2,770-row CSV is a machine-readable validation snapshot.

## Authentication result

The 33-file TTT regression corpus produced:

```text
TTT files:                 33
Authenticated:             32
Ambiguous references:       0
No reference record:        1
```

The full Edgardo Donato 1940–1945 TTT release was then validated:

```text
Files examined:            42
Authenticated:             42
No reference record:        0
Ambiguous references:       0
Probe errors:               0
Date transpositions:        0
```

This is sufficient evidence to treat the basic TTT translator as a viable direct-ingest implementation, subject to continued regression testing.

## Reference differences are not automatically errors

The tests show that source and reference representations can legitimately differ.

Examples:

```text
TTT:
Aníbal Troilo / Alberto Marino

TANGO-DJ:
Orquesta Aníbal Troilo con Alberto Marino
```

and:

```text
TTT:
Record: 39299-B, Matrix: 39981,Take: 1

TANGO-DJ:
39299B
```

These are representation differences and should not cause the source-derived canonical record to be overwritten.

The canonical model should preserve the richer source evidence and represent the underlying concepts separately.

## Date discrepancy rule

A tested example:

```text
TTT:      1938-07-03
TANGO-DJ: 1938-03-07
```

This is consistent with a month/day transposition.

The implementation therefore flags:

```text
DATE_TRANSPOSITION_SUSPECTED
```

but does **not** silently change the TTT value.

The record retains:

```text
recording_date       = TTT value
reference_date       = TANGO-DJ value
authentication_flag  = DATE_TRANSPOSITION_SUSPECTED
```

Human review can establish the eventual authoritative interpretation.

A precision difference is handled differently. For example:

```text
TTT:      1968-12-01
TANGO-DJ: 1968
```

is not treated as a conflict merely because one source supplies greater date precision.

## Alternate titles

TANGO-DJ can contain title enrichment not present in the TTT file.

Example:

```text
TTT:      Nació en Pompeya
TANGO-DJ: Nací en Pompeya (Nació en Pompeya)
```

and:

```text
TTT:      Por la güella
TANGO-DJ: Por la güella (Por la huella)
```

These should be represented as alternate/reference title evidence, not used to overwrite the TTT source title.

## Reference gaps

One TTT regression file, `Chiqué`, had no TANGO-DJ record in the 2,770-record TTT snapshot.

This does **not** invalidate the TTT source record. It identifies a gap in the reference database that should be recorded for follow-up/errata work.

## Provenance requirements

Every source ingest should retain:

- original source file path
- original filename
- source/provider
- source release/package
- original embedded values
- deterministic corrections, if any
- derived canonical values
- reference assertions
- reference snapshot identifier
- authentication result
- review flags
- date of processing

Original source values must never be silently replaced.

## Processing stages

An audio asset may move through several physical/logical locations during its life:

```text
1. New-file ingest location
       ↓
2. Purgatory / absorption staging
       ↓
3. Cataloged asset
       ↓
4. DJ reference / playable structure
```

The database record is persistent even when the physical audio file changes location.

A file may therefore change its "clothing" while retaining its identity and historical breadcrumbs.

Source processing must be non-destructive to the original source audio.

## TTT translator implementation

The current reusable TTT translator is:

```text
08_tools/text/build_ttt_canonical_staging.py
```

Supporting tools:

```text
08_tools/text/probe_ttt_test_set.py
08_tools/text/compare_ttt_tags_to_reference.py
08_tools/text/validate_ttt_release.py
```

The test corpus is:

```text
08_tools/text/tests/TTT_test_set.csv
```

The complete TTT/TANGO-DJ reference snapshot is:

```text
03_assets/ReferenceCatalogs/TANGO-DJ_AT/2026-08-28/TTT/
    source/
    extracted/TTT_TANGO-DJ_2026-08-28.csv
```

## Design conclusion

TTT is suitable for direct population of MusicStewardship canonical staging records.

The preferred architecture is:

```text
                  ┌──────────────────────┐
                  │    TTT audio file    │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   TTT translator    │
                  │  source-specific    │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ canonical staging    │
                  │      record          │
                  └──────────┬───────────┘
                             │
            ┌────────────────┼─────────────────┐
            ▼                ▼                 ▼
      TANGO-DJ          other sources     acoustic match
      reference         / authorities     when needed
            │                │                 │
            └────────────────┼─────────────────┘
                             ▼
                  ┌──────────────────────┐
                  │ authentication /    │
                  │ exception handling  │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ MusicStewardship    │
                  │ catalog + asset     │
                  │ + DJ overlay        │
                  └──────────────────────┘
```

The reference systems authenticate and enrich the record; they do not become the source-of-truth for the TTT ingest itself.

## Next validation

Before applying the translator to the entire TTT collection, run another complete-release test using an early acoustic-oriented collection, such as:

```text
M:\TangoTimeTravel\Todos de la Orquesta Típica Victor 1925-1930
```

This provides a different historical and recording-medium case and tests whether the rules generalize beyond the successful Donato release.
