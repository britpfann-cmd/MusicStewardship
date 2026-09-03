# Audio Asset Lifecycle — Implementation Requirement

**Status:** Baseline implementation requirement  
**Baseline date:** 2026-08-29  
**Applies to:** MusicStewardship ingest, cataloging, materialization, and DJ-library tooling

## Requirement

The implementation shall treat **recording identity**, **audio asset**, **lifecycle state**, **physical location**, and **representation** as separate concerns.

A file may move, be renamed, retagged, converted, copied, or rematerialized without creating a new recording identity.

## Recording and asset

A `Recording` identifies the underlying musical performance/recording.

An `AudioAsset` identifies one digital representation of that recording.

One recording may have many audio assets.

## Lifecycle

At minimum support:

```text
RECEIVED
SCREENED
IDENTIFIED
RECONCILED
CATALOGED
READY_FOR_MATERIALIZATION
MATERIALIZED
PUBLISHED_TO_DJ
MAINTAINED
ARCHIVED
SUPERSEDED
```

Operational step names may be more granular than lifecycle states. For example:

```text
PROBE
SCREEN
TRANSLATE
REFERENCE_CHECK
RECONCILE
```

The lifecycle state is not the processing log.

## Processing ledger

The implementation shall maintain a resumable processing ledger with:

```text
asset_id
recording_id
source
source_path
current_state
current_step
status
created_at
updated_at
next_action
```

and an event history containing:

```text
event_id
asset_id
step
attempt
started_at
completed_at
result
tool
tool_version
input_fingerprint
output_fingerprint
error_code
error_message
notes
```

The history is append-oriented: retries create new attempts rather than erasing prior attempts.

## Human-readable ledger

The operational ledger shall have a human-readable Markdown representation containing:

1. overall summary;
2. lifecycle summary;
3. next-action summary;
4. exception summary;
5. per-asset details;
6. per-asset processing history.

SQLite is the operational store; Markdown is the human-readable operational view.

## Source immutability

External source audio and source metadata shall not be modified in place.

All processing is non-destructive.

## Normalization and semantic consistency

The implementation shall distinguish:

### Mechanical housekeeping

- whitespace;
- Unicode whitespace;
- repeated spaces/tabs;
- presentation-only punctuation spacing;
- other deterministic, meaning-preserving cleanup.

### Semantic normalization

Meaning-preserving canonicalization is permitted when the equivalence rule is deterministic.

Examples:

```text
47309-A → 47309A
60013 + Take 2 ↔ 60013-2
```

Normalization shall reduce ambiguity, not invent certainty.

Preserve:

```text
original_source_value
canonical_value
normalization_rule
normalization_type
```

## External references

External references are evidence, not acceptance gates.

The native source with stronger provenance remains primary for source-derived canonical values.

External references may:

- confirm;
- enrich;
- correct through a separate reviewed decision;
- identify alternate representations;
- expose divergences;
- expose missing reference coverage.

Multiple external reference rows may remain separate assertions.

## Multiple digital assets and preferred copies

One recording may have multiple digital assets.

Assets shall support selection attributes such as:

```text
BEST
PREFERRED
CONTEXT_PREFERRED
```

A playlist may select the preferred/best eligible asset without changing the recording identity or other assets.

## Format policy

Managed master representation:

```text
lossless source → prefer FLAC
lossy source    → retain lossy source quality
```

Do not up-convert lossy audio merely for container uniformity.

Destination-specific materializations may use other formats.

Examples:

```text
MASTER_LOSSLESS
DJ_WINDOWS
DJ_MAC
PHONE
BACKUP
```

The destination profile controls output format and metadata policy.

## Acceptance criteria

The implementation satisfies this requirement when it can:

1. preserve source audio unchanged;
2. record provenance;
3. maintain stable recording identity across asset transformations;
4. maintain independent lifecycle and location history;
5. record processing checkpoints and retries;
6. resume from completed steps;
7. represent multiple assets for one recording;
8. record external reference assertions and divergences;
9. select preferred/best assets for downstream use;
10. materialize destination-specific copies without altering source evidence.
