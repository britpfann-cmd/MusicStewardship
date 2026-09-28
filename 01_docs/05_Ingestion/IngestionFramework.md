# MusicStewardship Music Vocabulary & Ingestion Framework

**Status:** Baseline architecture framework  
**Baseline date:** 2026-08-29  
**Purpose:** Define the common vocabulary, provenance model, source-ingest philosophy, and controlled normalization principles for MusicStewardship.

## 1. Purpose

MusicStewardship creates a durable, trustworthy body of knowledge about music actually possessed by the project. It supports archival preservation, historical research, music analysis, provenance tracking, and practical DJ use.

The system must accommodate multiple sources, source conventions, releases, transfers, files, and external references without confusing any of those with the underlying musical performance.

The governing principle is:

> **Preserve what the source actually says, extract useful information, normalize only where meaning is preserved, use respected external references to improve accuracy and completeness, and never reject possessed music merely because an external reference disagrees or is silent.**

## 2. Source-first ingest

The native source with the stronger provenance is the primary evidence for source-derived canonical data.

External reference systems are secondary evidence used to:

- confirm identity;
- identify missing information;
- identify probable errors or transcription differences;
- add useful identifiers;
- expose alternate representations;
- provide independent validation.

External references must not be treated as acceptance gates.

Therefore:

```text
no external reference match
    ≠
invalid music

external disagreement
    ≠
automatic source correction
```

A discrepancy is recorded for review.

## 3. Performance, recording, release, and asset

The model distinguishes:

```text
Performance / historical recording identity
        ↓
Recording identity
        ↓
one or more digital AudioAssets
        ↓
source/release manifestations
        ↓
derived/materialized destination copies
```

A single performance may have multiple digital assets.

A release is a packaging/distribution context, not the recording identity.

An audio file is an asset, not the recording identity.

## 4. Multiple copies and preferred assets

The catalog shall support multiple digital assets for one performance or recording.

For each recording, one or more assets may be designated:

- `BEST` — strongest known technical/source copy;
- `PREFERRED` — currently preferred for normal use;
- `CONTEXT_PREFERRED` — preferred for a specific destination or purpose;
- or left unpreferred.

Preference is selectable rather than permanent. Playlist construction should normally select from eligible preferred/best assets rather than directly binding playlists to arbitrary source files.

## 5. Common vocabulary

Initial concepts include:

- Performance Event
- Recording
- Take
- Composition
- Person
- Ensemble
- Role
- Release
- Release Copy
- Audio Asset
- Source
- Source Collection
- Source Context
- Provenance
- Restoration
- Media
- Identifier

Supporting concepts include:

- recording date;
- genre;
- dance form;
- singer;
- composer;
- lyricist/author;
- conductor;
- arranger;
- matrix;
- catalog number;
- recording key;
- score key;
- pitch;
- transfer information.

## 6. Source context

Source evidence includes more than embedded metadata.

It may include:

- folder hierarchy;
- filenames;
- release names;
- artwork;
- catalogs;
- release notes;
- documentation;
- distribution information;
- transfer notes.

The project principle is:

> **Extract facts; preserve evidence.**

Source context remains recoverable after materialization and reorganization.

## 7. Controlled transformation types

Source mappings may use:

- `COPY`
- `RENAME`
- `STANDARDIZE`
- `DECOMPOSE`
- `COMBINE`
- `LOOKUP`
- `EXTRACT`
- `PATH_EXTRACT`
- `DERIVE`
- `REFERENCE`
- `IGNORE`
- `SOURCE_CONTEXT`

A transformation rule must identify whether it preserves meaning, derives information, or merely records an external reference.

## 8. Normalization and semantic consistency

Normalization has two levels.

### Mechanical housekeeping

Permitted when presentation-only:

- leading/trailing whitespace;
- repeated spaces/tabs;
- whitespace around punctuation;
- Unicode whitespace variants;
- other deterministic presentation corrections.

### Semantic normalization

Permitted only when a deterministic, meaning-preserving equivalence rule exists.

Examples:

```text
47309-A
    → normalized record identity 47309A

60013 + Take 2
    ↔
60013-2
```

Normalization shall reduce avoidable ambiguity, not manufacture certainty.

For every changed canonical representation, retain:

```text
original_source_value
canonical_value
normalization_rule
normalization_type
```

### Source-semantic boundary

Source grammar may establish a semantic role when that role is reliably encoded by the source itself. For example, a source may encode a principal performer representation, an associated performer representation, or a source recording-year representation.

Source interpretation shall stop where a stronger conclusion requires knowledge external to the source grammar. Entity identity or type (for example, Person versus Ensemble), canonical identity, and more specific participant roles shall be deferred to downstream reference/entity reconciliation unless the source itself provides sufficient evidence.

The governing rule is:

> **Decode what the source encodes; do not use source grammar to manufacture knowledge that belongs to entity or reference reconciliation.**
## 9. External normalization

External systems such as TANGO-DJ may have their own transposition or representation rules.

MusicStewardship does **not** need to reproduce those rules simply to make source values look alike.

Instead:

```text
native source value
    ↓
MusicStewardship canonical representation
    ↓
external reference assertion
    ↓
divergence/reconciliation information
```

Multiple external rows may be retained as separate reference assertions.

## 10. Ingest processing architecture

The operational flow is:

```text
SOURCE
  ↓
DISCOVER
  ↓
PROBE
  ↓
SCREEN
  ↓
SOURCE-SPECIFIC TRANSLATE
  ↓
NORMALIZE / DECOMPOSE
  ↓
REFERENCE / ENRICH
  ↓
RECONCILE
  ↓
CATALOG
  ↓
MATERIALIZE
```

The processing ledger records the operational history independently of lifecycle state.

## 11. Resumable processing

Every ingest asset shall be traceable by:

- stable asset identifier;
- source path;
- current lifecycle state;
- current processing step;
- processing history;
- next action;
- tool/version;
- input/output fingerprints where applicable;
- failure information.

A stopped process shall be restartable from the last successfully completed step.

History must not be rewritten to make a retry appear to be the original attempt.

## 12. Source immutability

External source material is read-only to the ingest pipeline.

Processing creates working or derived representations.

The source file, original metadata, and source context remain recoverable.

## 13. Format policy

For managed/master audio:

- prefer FLAC when the source is lossless;
- retain a lower-quality lossy source as lossy rather than up-converting it merely for appearance of uniformity.

Derived destination copies may use other formats when justified by destination constraints.

Examples include:

```text
MASTER_LOSSLESS
DJ_WINDOWS
DJ_MAC
PHONE
BACKUP
```

The destination profile controls format and metadata policy.

## 14. Acceptance principle

The system's objective is:

> **maximize the accuracy, completeness, usefulness, and provenance of music we actually possess.**

The system must not turn reference gaps into music rejection.


## Addendum — 2026-09-24 Collection Import and CSV Boundary

The initial library-building implementation shall use **one canonical CSV public interface** for all source collections.

Source-specific grammars and translation tables may differ, but every source must be translated into the same canonical CSV field vocabulary. The canonical vocabulary begins with the union of the established Restorer field definitions and is extended only when a demonstrated source requirement cannot be represented without loss.

A source-specific translation table is a reference artifact, preferably CSV, and is part of the auditable source profile. It maps source vocabulary to canonical fields and identifies information that is retained as residual/unparsed source text.

The rule is:

> **No source information is discarded because the current model does not yet know how to interpret it.**

The canonical CSV is therefore the interchange boundary. Downstream library-card construction, indexing, and entity association consume the canonical CSV rather than source-specific structures.

The first end-to-end proving source is Tango Time Travel (TTT), because its dataset is unusually information-rich. TTT is a seed source for names and vocabulary, not an authority source.

The planned initial collection order is:

1. TTT
2. Crackling Tunes (CT)
3. Tango Tunes (TT)
4. the small TS collection
5. fromJae
6. ToTango

A complete source collection import is successful only when every terminal track/object produces a canonical CSV record and the build evidence demonstrates that no source record was silently dropped.
