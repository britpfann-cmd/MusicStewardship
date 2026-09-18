# MusicStewardship Candidate Record Construction Rules

**Document ID:** ING-CAND-001  
**Status:** Working design rule  
**Revision:** A  
**Date:** 2026-09-18

## 1. Purpose

This document defines the rules for constructing a **Candidate Record** from preserved source evidence.

The Candidate Record is an intermediate stewardship object. It is **not** a canonical catalog record and it does not perform entity resolution.

The governing distinction is:

> **Evidence says what the source contains.  
> Candidate construction says what those observations might represent.  
> Resolution says what we are ultimately willing to assert.**

## 2. Position in the ingestion pipeline

```text
Explorer Tree
      ↓
Structural Analysis
      ↓
Decoding Plan
      ↓
Evidence Extraction
      ↓
Candidate Record Builder
      ↓
Candidate Records
      ↓
Resolution
      ↓
Canonical Recording
```

The builder therefore consumes observations already produced by earlier stages and assembles them without replacing their source meaning.

## 3. Candidate Record definition

A Candidate Record consists of:

1. **source provenance**
2. **candidate attributes**
3. **residual/uninterpreted evidence**
4. **construction status**
5. **lineage to the observations from which the candidate was assembled**

A Candidate Record begins with exactly one terminal source object.

No candidate may exist without a traceable source object.

## 4. Source-object rule

For each terminal source object encountered by Explorer Tree, create one Candidate Record.

The minimum preserved provenance is:

```text
source_id
source_root
relative_path
filename
extension
entry_type
```

The builder does not rename, move, normalize in place, or otherwise modify the source object.

Directories are not themselves Candidate Records. Their information may become directory evidence attached to a terminal object's candidate.

## 5. Evidence channels

Evidence from different channels remains distinguishable.

The builder may collect:

```text
directory evidence
filename evidence
embedded metadata evidence
technical metadata
source-specific decoded evidence
```

Examples:

```text
directory.artist_candidate
filename.title_candidate
metadata.tag.TITLE
metadata.tag.ARTIST
technical.codec_name
```

Evidence is never merged merely because two observations have the same apparent value.

## 6. Candidate attributes

Observations may be attached to prospective Candidate Record attributes such as:

```text
title
artist
orchestra
singer
recording_identifier
recording_year
recording_date
genre
style
source_album
composer
conductor
```

The list is intentionally provisional and may grow as source grammars require it.

Attaching an observation to an attribute does **not** establish that the observation is correct.

Each candidate attribute therefore contains one or more evidence references.

## 7. Multiple observations

There is no one-value-per-attribute rule.

For example, a Candidate Record may contain:

```text
title
  - metadata.tag.TITLE → "A mí no me interesa"
  - filename.leading_text → "A mi no me interesa"
```

Both observations remain present.

Conflicts are not resolved by the builder.

## 8. Raw-value preservation

Raw source values are retained exactly as observed.

Where mechanical normalization is useful, a normalized value may be added alongside the raw value.

The builder follows:

> **Preserve → Normalize → Interpret**

Normalization is a derived processing value. It never replaces the source value.

## 9. No authority ranking

The builder does not assume:

```text
metadata > filename
filename > directory
directory > metadata
```

or any similar universal authority order.

Evidence authority and conflict resolution belong downstream.

The builder records evidence; it does not adjudicate it.

## 10. Source-specific decoding

A source-specific rule may decode a compound or structured source expression into additional observations.

For example:

```text
CATALOGNUMBER
    ↓
record
matrix
take
```

The original compound observation remains evidence.

Decoding is not deletion.

Decoding is not resolution.

## 11. Missing information

The builder never manufactures information.

If no source evidence supplies a date, no date candidate is invented.

If a directory explicitly encodes an orchestra, that may be retained as directory evidence. If it does not, the builder does not infer one from unrelated context.

## 12. Residual evidence

Evidence that cannot presently be mapped to a candidate attribute remains attached to the Candidate Record as residual/uninterpreted evidence.

Examples include source-specific or technical fields such as:

```text
id3v2_priv.WM/ContentID
iTunNORM
originator_reference
time_reference
encoded_by
```

Residual does not mean useless. It means that the current candidate-construction vocabulary does not assign a prospective catalog meaning to it.

## 13. Technical evidence

Technical observations remain distinguishable from musical assertions.

Examples:

```text
codec_name
sample_rate
channels
duration
bit_rate
file_size
```

Technical facts may be useful for later asset management, validation, or provenance, but they are not automatically musical candidate attributes.

## 14. Evidence lineage

Every candidate attribute observation must retain a pointer to the original evidence observation.

The preferred lineage is:

```text
Candidate Attribute
      ↓
Evidence Observation
      ↓
Source Object
```

For derived observations:

```text
Candidate Attribute
      ↓
Derived Observation
      ↓
Original Observation
      ↓
Source Object
```

## 15. Status

The builder may report a simple construction status:

```text
candidate
candidate_with_conflicts
candidate_incomplete
```

These statuses describe the state of the assembled evidence, not historical truth.

The builder must not decide whether a recording, person, orchestra, or composition is correct.

## 16. Determinism

Given the same inputs, the builder must produce the same Candidate Records.

Inputs should be processed in deterministic order.

Evidence references should be stable within a build.

The builder must not depend on filesystem traversal order or dictionary insertion order for semantic results.

## 17. Unified construction algorithm

```text
FOR each terminal source object:

    create CandidateRecord

    attach source provenance

    collect directory observations
    collect filename observations
    collect embedded metadata observations
    collect technical observations
    collect source-specific decoded observations

    FOR each observation:

        preserve raw observation

        if mechanical normalization is defined:
            create normalized value

        if observation maps to a candidate attribute:
            attach observation to that attribute

        otherwise:
            retain as residual/uninterpreted evidence

    preserve observation → candidate lineage

    do not resolve conflicts

    do not select authoritative values

    do not discard competing observations

    emit CandidateRecord
```

## 18. Separation of concerns

The Candidate Record Builder is responsible for:

- assembling evidence;
- preserving provenance;
- applying already-defined decoding results;
- grouping observations under prospective attributes;
- preserving residual information;
- reporting construction-level conflicts or incompleteness.

It is not responsible for:

- entity resolution;
- deciding canonical names;
- deciding which source is authoritative;
- merging recordings;
- creating or merging people;
- deciding historical correctness;
- changing source files;
- imposing final library organization.

## 19. Relationship to CORE / ASSOCIATED / RESIDUAL

CORE / ASSOCIATED / RESIDUAL describes the semantic role of information.

It is not an authority ranking.

The Candidate Record may therefore contain all three classes while preserving their source lineage.

An observation being ASSOCIATED does not make it less truthful than a CORE observation; it simply means that it is not required for the current ingestion objective.

## 20. Initial attribute mapping

The first implementation uses a deliberately small generic mapping:

| Evidence source | Candidate attribute |
|---|---|
| metadata `TITLE` / `title` | title |
| metadata `ARTIST` / `artist` | artist |
| metadata `ALBUM_ARTIST` / `album_artist` | orchestra_or_album_artist |
| metadata `ALBUM` / `album` | source_album |
| metadata `GENRE` / `genre` | genre |
| metadata `DATE` / `date` | recording_date_or_year |
| metadata `COMPOSER` / `composer` | composer |
| metadata `CONDUCTOR` / `conductor` | conductor |
| filename `leading_text` | title_candidate |
| filename `numeric_component` | recording_identifier_candidate |
| filename `terminal_suffix` | source_suffix |
| directory components | directory evidence, not automatically canonical attributes |

This mapping is intentionally conservative. It creates candidate assertions without claiming semantic authority.

Source-specific plans may add additional mappings later.

## 21. Current implementation boundary

The first builder is deliberately an assembly layer.

It should be considered successful if it can take the current Explorer Tree / Decoding Plan / Candidate Extraction / Metadata Evidence outputs and produce a single inspectable Candidate Record per terminal source object while retaining every input observation.

More elaborate resolution, scoring, confidence aggregation, or canonicalization should not be added until a demonstrated requirement requires them.

## 22. Governing architectural rule

> **A Candidate Record is an assembly of source evidence, not a resolved assertion.**

And:

> **Do not add a new ingestion verb until a new requirement cannot be expressed clearly using the existing verbs, an existing decoder, and rule parameters.**
