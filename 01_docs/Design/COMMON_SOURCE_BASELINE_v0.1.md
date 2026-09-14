# MusicStewardship Common Source Baseline v0.1

**Status:** Working design artifact  
**Date:** 2026-09-14

## Purpose

Define the common source/audio baseline that CT and TTT source additions build upon.

The baseline describes reusable mechanics and shared source representations. It does not define source-specific semantics.

## Common audio formats

```text
.aif
.aiff
.flac
.mp3
.wav
.m4a
.mp4
.ogg
.opus
.wma
.alac
```

## Common metadata vocabulary

```text
title
artist
album
date
composer
conductor
record
matrix
take
genre
source_media
track
album_artist
catalognumber
comment
encoded_by
```

These are normalized reader fields, not canonical entity claims.

## Common source/provenance vocabulary

```text
source_id
source_root
relative_path
filename
directory_path
source_release
source_snapshot
source_row
```

## Common evidence policy

Every extracted value should retain:

- the source representation;
- the origin of the representation (filename, embedded tag, directory context, etc.);
- the interpretation method/rule;
- the resulting interpreted value;
- enough provenance to reproduce the result.

Embedded metadata is evidence, not canonical identity.

## Text handling

Source text is preserved exactly as supplied.

The processing pipeline distinguishes:

```text
source representation
    ↓
decoded/interpreted representation
    ↓
optional normalized representation
```

Baked/mojibake representations are not silently repaired.

## Common transformation capabilities

The common layer may provide:

```text
COPY
DECOMPOSE
EXTRACT
PATH_EXTRACT
STANDARDIZE
DERIVE
REFERENCE
ASSERT
SOURCE_CONTEXT
IGNORE
```

using reusable decoder techniques where applicable:

```text
scalar
compound
clauses
date
regex
regex_findall
regex_boolean
filename
labeled_fields
```

## Representation boundaries

The system distinguishes:

```text
source provenance
source evidence
normalized/decomposed representation
external reference representation
canonical entity representation
```

No source field is promoted to canonical identity merely because its name appears canonical.

## Track boundaries

These are distinct:

```text
source_track_number
release_track_number
external_track_number
```

A numeric value is interpreted together with its representation/context.

## Identifier boundaries

Identifier-like values are retained by source/context.

Examples include:

```text
source catalog identifier
record number
matrix number
take number
publisher/label assertion
external catalog identifier
```

Compound identifiers should be decomposed only when the source grammar establishes that decomposition.

## External reference boundary

External providers are common services, not source-specific parsers.

Examples:

```text
TANGO-DJ.AT
Discogs
future providers
```

A reference match is corroborating/enriching evidence. Lack of a match does not invalidate source ingestion.

## Source profile contract

A source addition should specify only what differs from this baseline:

```text
source identity
filename patterns
source-specific metadata aliases/fields
source-specific compound-field semantics
source-specific fallback rules
source-specific reference keys
```

The current `source_ingest.py` loader accepts flat sections (`sources`, `filename_patterns`, `metadata_fields`). It does not yet implement profile inheritance. Therefore the files below are **architecture candidates**, not drop-in replacements for the current loader until profile composition is added.

