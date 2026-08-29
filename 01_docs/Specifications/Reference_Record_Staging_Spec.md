# Reference Record Staging Specification

**Status:** Baseline specification  
**Baseline date:** 2026-08-29

## Purpose

A reference/canonical staging record represents a known musical recording and its source-derived information before permanent database cataloging.

It is not the audio file itself.

## Two related objects

### Recording

The underlying performance/recording identity.

### AudioAsset

A digital file representing that recording.

A recording may have multiple AudioAssets.

## Source-first rule

Source-derived canonical values originate from the native source with stronger provenance.

External reference information is retained as separate evidence.

A reference mismatch does not invalidate a possessed source asset.

## Proposed staging fields

### Identity

```text
reference_record_id
title
ensemble
singers
instrumental
recording_date
```

### Source provenance

```text
source
source_snapshot
source_release
source_row
source_file
source_filename
source_catalog_id
source_track_number
source_context
```

### Source evidence

```text
source_original_title
source_original_artist
source_original_album
source_original_date
source_original_catalognumber
source_original_composer
source_original_comment
```

### Normalized/decomposed values

```text
canonical_title
canonical_ensemble
canonical_singers
canonical_record_number
canonical_matrix_number
canonical_take_number
normalization_rule
normalization_type
```

### External references

Multiple external reference assertions may be attached:

```text
reference_source
external_reference_id
external_release
external_track_number
external_title
external_artist
external_recording_date
external_catalog_number
external_matrix_number
external_notes
```

### Reconciliation

```text
identity_status
identity_confidence
divergence_type
divergence_status
review_note
```

## Divergence model

External reference differences should be classified rather than silently corrected.

Examples:

```text
REPRESENTATION
NORMALIZATION
ALTERNATE_TITLE
IDENTIFIER_FORMAT
DATE_PRECISION
DATE_CONFLICT
REFERENCE_GAP
ADDITIONAL_REFERENCE_INFORMATION
```

## Reference assertions

An external catalog may contain several rows representing the same recording in different package/release contexts.

These rows may remain separate external assertions.

The staging layer should not force a one-reference-row-per-recording model.

## Preferred asset

Asset selection belongs to the relationship between Recording and AudioAsset, not to external reference identity.

Possible selection attributes:

```text
BEST
PREFERRED
CONTEXT_PREFERRED
```

## Canonical-value rule

Canonical values are the current MusicStewardship representation for downstream use.

Original source values remain recoverable.

External representations remain separately visible.

## Cataloging boundary

Reference/canonical staging may be complete before permanent database insertion.

Catalog creation is separate from materialization.

Materialization creates a managed destination asset from an already-resolved source asset.
