# Common Baseline and Source-Specific Additions

## Decision

Use a two-level translator architecture:

```text
COMMON SOURCE/AUDIO BASELINE
        +
SOURCE-SPECIFIC ADDITIONS
```

The common baseline supplies reusable mechanics and vocabulary. CT and TTT additions supply only the source-specific grammar and semantics.

## Why

The direct CT source-tree test demonstrated that the common machinery can already:

```text
walk the real source tree
classify audio
read embedded metadata with ffprobe
apply filename regexes
preserve source paths and filenames
produce evidence records
```

The CT profile then needed only CT-specific grammar, including two filename date forms and CT identifier interpretation.

TTT already demonstrates a richer source grammar for filename forms, compound catalog representations, comments, artist/performance interpretation, and source media.

## Architectural split

```text
COMMON
  filesystem/source-tree handling
  audio format detection
  ffprobe metadata reading
  normalized reader vocabulary
  provenance/evidence handling
  reusable decoders
  generic Rosetta operations
  external-reference interface

CT ADDITIONS
  monthly release grammar
  CT filename identifier grammar
  CATALOG # semantics
  CT fallback rules
  CT artist/performance interpretation

TTT ADDITIONS
  filename grammar
  Record/Matrix/Take compound interpretation
  composer/author clauses
  comment clause interpretation
  source-media interpretation
```

## Important implementation constraint

The current `source_ingest.py` profile loader is intentionally simple. It accepts flat sections such as:

```text
sources
filename_patterns
metadata_fields
```

It does not yet implement profile inheritance or additive composition.

Therefore the baseline and additions supplied with this checkpoint are **design artifacts**. They should not be wired into the current engine as though inheritance already exists.

A future profile-composition step can materialize:

```text
common baseline
    +
source additions
    ↓
effective source profile
    ↓
current source_ingest / Rosetta processing
```

without changing the conceptual boundary.

## Promotion rule

A capability should graduate from a source addition into the common baseline only when CT and TTT (or another source) demonstrate the same semantics, not merely the same mechanics.

## Reference-provider rule

TANGO-DJ.AT should be a common optional reference provider:

```text
source interpretation
       ↓
common observations
       ↓
reference reconciliation
       ├── TANGO-DJ.AT
       ├── Discogs
       └── future providers
```

It is not part of either CT or TTT filename/audio parsing.

## Current next step

Use these artifacts to guide a comparison of the CT and TTT experimental translator code, then implement the smallest common profile-composition mechanism needed to exercise both sources without duplicating shared behavior.
