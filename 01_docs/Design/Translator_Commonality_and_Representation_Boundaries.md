# MusicStewardship — Translator Commonality & Representation Boundaries

**Date:** 2026-09-14  
**Status:** Working design baseline

## 1. Purpose

This document records the current architectural understanding developed through the Tango Time Travel (TTT) and Crackling Tunes (CT) experiments.

The central principle is:

> The vocabulary of canonical entities should emerge gradually from the representations and evidence we encounter.

The ingestion system therefore preserves source representations and interpretations rather than forcing source material immediately into canonical entities.

## 2. Processing Architecture

```text
ORIGINAL SOURCE MATERIAL
        ↓
SOURCE-TREE INVENTORY
        ↓
COMMON AUDIO / FILE EXTRACTION
        ↓
SOURCE-SPECIFIC TRANSLATOR / GRAMMAR
        ↓
GENERIC ROSETTA ENGINE
        ↓
DURABLE OBSERVATIONS + PROVENANCE
        ↓
REFERENCE RECONCILIATION
        ├── TANGO-DJ.AT
        ├── Discogs
        └── other providers
        ↓
CANDIDATE / PROMOTED CANONICAL ENTITIES
```

Source-specific grammar interprets source representations. The Rosetta engine performs generic rule execution and durable evidence processing.

## 3. Source Material and Output Roots

The source tree is authoritative input.

For Crackling Tunes:

```text
M:\CracklingTunes
```

The tree contains monthly releases and may contain audio plus release notes, graphics, and other collateral.

Development processing may write generated artifacts beneath:

```text
99_sandbox\...
```

Operational processing may write generated state/results beneath:

```text
06_runtime\...
```

Therefore:

> **Source trees are inputs; output roots are parameters.**

A sandbox run and a production run should differ primarily in destination and operational policy, not in the source interpretation logic.

## 4. Source Asset Classes

A release directory may contain:

```text
Release
├── Audio Asset
├── Documentation Asset
├── Graphic Asset
└── Other Source Asset
```

The audio-ingestion path processes audio assets. Documentation and graphics remain source material and should still be inventoried.

The CT corpus demonstrated this distinction: the complete filesystem contained more files than the audio corpus, while the historical CT transition contained the same number of audio files as the current source tree.

## 5. Common Source / Audio Layer

The current `source_ingest.py` provides substantial common functionality.

### 5.1 Filesystem representation

The source-tree analyzer records source root, relative path, filename, directory hierarchy/context, and audio classification.

Directory names are evidence, not canonical identity.

### 5.2 Audio-format support

The current ingest layer recognizes:

```text
.aif  .aiff  .flac  .mp3  .wav  .m4a  .mp4
.ogg  .opus  .wma  .alac
```

The interface is format-independent. The present implementation uses `ffprobe` for embedded metadata. A format-specific executable such as `metaflac` should be treated as an implementation detail rather than the architecture's definition of audio extraction.

### 5.3 Common metadata vocabulary

The current reader can retrieve normalized fields including:

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

The source profile decides which fields matter for a source.

Raw source values must remain available and should not be silently converted into canonical entities.

## 6. Source-Specific Grammar Layer

The common reader answers:

> What tags and file properties are present?

The source grammar answers:

> What does this source's filename or compound field mean?

### Crackling Tunes

CT-specific interpretations include:

```text
CT monthly release naming
CT identifier syntax
filename date forms
CATALOG # semantics
filename fallback for CT identifiers
artist-string decomposition
instrumental representation
source-specific release/track representations
```

### Tango Time Travel

TTT-specific interpretation includes:

```text
filename release-track forms
artist / performer interpretation
composer compound fields
Record / Matrix / Take
comment clauses
source media
release / album
track
```

### Commonality rule

Where CT and TTT require the same transformation technique, use a common decoder or generic Rosetta operation.

Where the meaning comes from source grammar, keep it in the source profile/rules.

## 7. Common Decoder Layer

Historical repository work already contains a reusable decoder package:

```text
04_src/ingestion/decoders/
    base.py
    scalar.py
    compound.py
    clauses.py
    date.py
```

with tests under:

```text
07_tests/ingestion/decoders/
```

Demonstrated reusable techniques include:

- scalar copy;
- compound decomposition;
- clause preservation;
- date interpretation.

These are transformation techniques, not source-specific entity definitions.

## 8. Representation Boundaries

Historical staging explicitly distinguishes several levels.

### 8.1 Source provenance

Examples:

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

These represent what a source supplied or how an item was located.

### 8.2 Source evidence

Examples:

```text
source_original_title
source_original_artist
source_original_album
source_original_date
source_original_catalognumber
source_original_composer
source_original_comment
```

These preserve source assertions.

### 8.3 Normalized / decomposed representations

Examples:

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

These are downstream interpretations and must not overwrite the source evidence.

### 8.4 External references

External source assertions have their own representation:

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

An external reference is evidence from another source, not automatically a canonical fact.

## 9. Track Number Boundaries

The CT/TTT evidence demonstrates that track-like values occur at different representation levels:

```text
source_track_number
release_track_number
external_track_number
```

These should not be conflated.

### Source track

`source_track_number` belongs to source provenance/staging. Its exact CT semantics are not assumed beyond the documented staging role.

### Release track

An embedded `TRACK` field is a strong candidate for the source release's track position.

### External track

A provider such as TANGO-DJ may supply its own release-track position.

Therefore:

> A track number is meaningful together with the representation/context that supplied it.

## 10. Identifier Boundaries

A tested CT file contained both:

```text
CATALOG #     = CT1898-B1
CATALOGNUMBER = Label 1A-0752-B, matrix S-004844
```

and the filename also contained:

```text
[CT1898-B1]
```

All ten files in the tested 21.08 release showed exact filename / embedded `CATALOG #` agreement.

These are distinct source representations.

Therefore:

> Common vocabulary should describe the kind of representation; source grammar supplies its semantics.

## 11. Raw, Decoded, and Normalized Text

The source experiments exposed filenames containing baked character representations such as:

```text
Lili├ín
Orquesta Ti╠üpica
```

The correct progression is:

```text
SOURCE REPRESENTATION
        ↓
DECODED / INTERPRETED REPRESENTATION
        ↓
OPTIONAL NORMALIZED REPRESENTATION
```

The source value remains available.

Normalization may be justified later, but an inferred normalized value must not replace the source representation.

## 12. Crackling Tunes Real-Source Test

The direct real-source test used:

```text
M:\CracklingTunes\21.08 Releases
```

The release contained ten audio files.

The source-tree and common audio-ingest path produced:

```text
10 audio records
10 filename-rule matches
10 embedded-metadata records
0 rejected assets
```

For all ten files:

```text
filename CT identifier = embedded CATALOG # CT identifier
```

The historical CT transition contained the same ten audio records.

The fresh source ingest reproduced core title, artist, album-artist, date, track, composer, genre, and other available metadata while preserving the raw filenames separately.

## 13. What the Old CT Translator Still Contributes

Much of the old CT extraction work is now common infrastructure:

```text
filesystem walk
audio detection
embedded metadata extraction
basic filename matching
source-relative paths
raw source preservation
```

The CT-specific layer still contributes:

```text
CT identifier interpretation
CT release semantics
CT-specific filename grammar
CT-specific fallback rules
source-specific artist/performance interpretation
```

Historical CT transition artifacts remain valuable as:

- regression fixtures;
- documented source knowledge;
- evidence for source-specific rules;
- edge-case examples.

They need not remain the production pipeline input.

## 14. Common Reference Services

TANGO-DJ should be a **common optional reference provider**, not a source-specific dependency.

```text
CT interpretation ─┐
TTT interpretation ├──→ common observations
other sources ─────┘
                         ↓
                 reference reconciliation
                    ├── TANGO-DJ
                    ├── Discogs
                    └── future providers
```

A source can request corroboration or enrichment, but ingestion should remain valid when a provider has no match.

Reference assertions remain distinguishable from source assertions and canonical interpretations.

## 15. Reconciliation and Conflict

When independent representations agree, record the agreement as corroborating evidence.

When they disagree, preserve the alternatives and surface a resolution problem.

Do not silently select one representation merely because it came from a familiar provider.

This applies to title, artist, date, identifiers, matrices, track positions, and ensemble representations.

## 16. Tentative Commonality Matrix

| Capability | CT | TTT | Destination |
|---|---|---|---|
| Source-tree walk | Yes | Yes | Common |
| Audio-format detection | Yes | Yes | Common |
| Embedded audio metadata | Yes | Yes | Common |
| Raw filename preservation | Yes | Yes | Common |
| Regex filename matching | Yes | Yes | Common |
| Scalar copying | Yes | Yes | Common |
| Compound decomposition | Yes | Yes | Common |
| Clause preservation | Possible | Yes | Common |
| Date interpretation | Yes | Yes | Common |
| Catalog/identifier preservation | Yes | Yes | Common representation family |
| CT identifier semantics | Yes | No | CT profile |
| TTT Record/Matrix/Take semantics | No | Yes | TTT profile |
| CT filename fallback | Yes | No | CT profile |
| Reference lookup | Yes | Yes | Common reference layer |
| TANGO-DJ reconciliation | Yes | Yes | Common reference provider |

This matrix remains provisional. A source-specific capability should graduate into the common layer only when its semantics are demonstrably shared.

## 17. Design Rules Established

1. **Preserve source representations.** Never replace source values merely because a normalized value exists.

2. **Separate representation from meaning.** A source value is evidence; interpretation is a separate operation.

3. **Use common mechanics, not common assumptions.** Shared decoder techniques belong in common infrastructure; source semantics belong in source profiles.

4. **Keep provenance levels distinct.** Source, canonical, and external representations remain distinguishable.

5. **Do not conflate track representations.** `source_track_number`, `release_track_number`, and `external_track_number` remain distinct until demonstrated otherwise.

6. **Treat external references as evidence.** TANGO-DJ and other providers corroborate or enrich; they are not mandatory ingestion dependencies.

7. **Preserve agreement and disagreement.** Agreement is corroborating evidence; disagreement becomes a resolution problem.

8. **Let entity vocabulary emerge.** Do not create canonical entities merely because a source field has a plausible name.

9. **Prefer real source trees for integration tests.** When accessible, use real source trees with sandbox output instead of copied source fixtures.

10. **Keep output destination configurable.** Sandbox and production should use the same processing architecture with different destinations and operational controls.

## 18. Open Questions

Still intentionally open:

- exact historical semantics of CT `source_track_number`;
- final common audio metadata abstraction;
- whether `CATALOG #` is CT-specific or should join a broader metadata vocabulary;
- final source-profile organization;
- complete CT multi-release grammar coverage;
- complete CT/TTT common translator-module extraction;
- implementation of common TANGO-DJ reference-provider services;
- rules for promotion from observations to canonical Work, Person, Ensemble, Performance, Release, and related entities.

These should be resolved by evidence and tests rather than premature schema decisions.

## 19. Recommended Development Sequence

```text
1. Real CT source-tree test — completed for 21.08
2. Compare fresh CT representation to historical transition
3. Recover/refine CT-specific grammar
4. Analyze CT vs TTT translator commonality
5. Consolidate reusable common decoder/audio modules
6. Make TANGO-DJ a common reference provider
7. Run full CT directory walk
8. Run broader CT ingestion
9. Graduate verified artifacts from sandbox
```

## 20. Baseline Conclusion

The CT and TTT experiments support a common architecture based on:

```text
real source material
    ↓
common source/audio extraction
    ↓
source-specific grammar
    ↓
generic Rosetta processing
    ↓
durable observations and provenance
    ↓
common reference reconciliation
    ↓
gradual canonical promotion
```

The strongest current conclusion is:

> **Build the system around representations and evidence first, with source-specific translators expressing meaning and common infrastructure providing the mechanics.**

Canonical entities should emerge from repeated, corroborated representations rather than being assumed in advance.
