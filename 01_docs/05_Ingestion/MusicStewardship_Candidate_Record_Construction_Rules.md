# MusicStewardship Candidate Record Construction Rules

**Document ID:** ING-CAND-001  
**Status:** Working design rule  
**Revision:** C  
**Date:** 2026-09-18

## 1. Purpose

This document defines the rules for constructing a **Candidate Record** from preserved source evidence.

The Candidate Record is an intermediate stewardship object. It is **not** a canonical catalog record and it does not perform entity resolution.

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

## 3. Candidate Record definition

A Candidate Record consists of source provenance, candidate attributes, residual/uninterpreted evidence, construction status, and lineage to the observations from which it was assembled.

A Candidate Record begins with exactly one terminal source object. No candidate may exist without a traceable source object.

## 4. Source-object rule

For each terminal source object encountered by Explorer Tree, create one Candidate Record.

Minimum preserved provenance:

```text
source_id
source_root
relative_path
filename
extension
entry_type
```

The builder does not rename, move, normalize in place, or otherwise modify the source object. Directories are not themselves Candidate Records; their information may become directory evidence attached to a terminal object's candidate.

## 5. Evidence channels

Evidence from different channels remains distinguishable:

```text
directory evidence
filename evidence
embedded metadata evidence
technical metadata
source-specific decoded evidence
```

Evidence is never merged merely because two observations have the same apparent value.

## 6. Candidate attributes

Observations may be attached to provisional attributes such as `title`, `artist`, `orchestra`, `singer`, `recording_identifier`, `recording_year`, `recording_date`, `genre`, `style`, `source_album`, `composer`, `conductor`, `filename_numeric_component`, `filename_leading_text_candidate`, `sequence_number_candidate`, and `source_suffix`.

### Numeric filename components

**A numeric component has no inherent semantic meaning.**

The generic layer records `filename.numeric_component` with its observed value and filename position/context. It must not generically label the value as a recording identifier, track number, year, date, catalog number, or other semantic field.

A later structural analysis or source grammar may derive:

```text
filename.numeric_component
        ↓
sequence_number_candidate
        ↓
track_number
```

but each step is additional interpretation. The original numeric observations remain intact.

Likewise, `filename.leading_text` is not generically declared to be a title.

## 7. Multiple observations are normal

There is **no one-value-per-attribute rule**.

Some candidate attributes are inherently multi-valued at this stage.

In particular:

> **Multiple `filename.numeric_component` observations in one filename are normal and are not, by themselves, a conflict.**

For example:

```text
El 13 9713_RP.aif

filename.numeric_component
  - 13
  - 9713
```

Preservation requirements must not create duplicate candidate observations. If a source fact is already extracted (for example, `filename.terminal_suffix`), preserving that fact means retaining its original evidence and lineage; it does not require a second candidate observation for the same value.

Both observations are retained because both occur in the source filename. The builder does not decide what either number means.

## 8. What constitutes a conflict

A **conflict** is not simply the presence of multiple observations.

A conflict exists when the builder has multiple incompatible observations for an attribute that is expected to be singular under the current candidate vocabulary.

Thus:

```text
filename.numeric_component
  - 13
  - 9713
```

is **not** a conflict. It is two observations of an explicitly multi-valued filename attribute.

The builder reports genuine candidate-level conflicts but never resolves them.

## 9. Raw-value preservation

Raw source values are retained exactly as observed. Where mechanical normalization is useful, a normalized value may be added alongside the raw value.

> **Preserve → Normalize → Interpret**

## 10. No authority ranking

The builder does not assume metadata > filename, filename > directory, directory > metadata, or any similar universal authority order. Evidence authority and conflict resolution belong downstream.

## 11. Source-specific decoding

A source-specific rule may decode a compound or structured source expression into additional observations. The original compound observation remains evidence.

Decoding is not deletion. Decoding is not resolution.

## 12. Missing information

The builder never manufactures information.

## 13. Residual evidence

Evidence that cannot presently be mapped to a candidate attribute remains attached as residual/uninterpreted evidence. Residual does not mean useless.

## 14. Technical evidence

Technical observations remain distinguishable from musical assertions, including codec, sample rate, channels, duration, bit rate, and file size.

## 15. Evidence lineage

Every candidate attribute observation retains a pointer to the original evidence observation:

```text
Candidate Attribute
      ↓
Evidence Observation
      ↓
Source Object
```

## 16. Status

The builder may report:

```text
candidate
candidate_with_conflicts
candidate_incomplete
```

These statuses describe the assembled evidence, not historical truth. `candidate_with_conflicts` means incompatible observations were detected for a currently singular candidate attribute. It does not mean that multiple observations of a multi-valued attribute are erroneous.

## 17. Determinism

Given the same inputs, the builder must produce the same Candidate Records. Inputs should be processed in deterministic order and evidence references should be stable within a build.

## 18. Unified construction algorithm

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
    classify conflicts only where the candidate attribute is expected to be singular
    do not resolve conflicts
    do not select authoritative values
    do not discard competing observations
    emit CandidateRecord
```

## 19. Separation of concerns

The Candidate Record Builder assembles evidence, preserves provenance, applies already-defined decoding results, groups observations under prospective attributes, preserves residual information, and reports construction-level conflicts where appropriate.

It does not perform entity resolution, decide canonical names, select an authoritative source, merge recordings or people, decide historical correctness, change source files, or impose final library organization.

## 20. Relationship to CORE / ASSOCIATED / RESIDUAL

CORE / ASSOCIATED / RESIDUAL describes semantic role, not authority. The Candidate Record may contain all three classes while preserving source lineage.

## 21. Initial attribute mapping

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
| filename `leading_text` | filename_leading_text_candidate |
| filename `numeric_component` | filename_numeric_component |
| filename `sequence_number_candidate` | sequence_number_candidate |
| filename `terminal_suffix` | source_suffix |
| directory components | directory evidence, not automatically canonical attributes |

The generic layer preserves numeric filename material without assigning semantic meaning.

## 22. Sequence evidence

A leading numeric filename component may participate in a sequence. The system may use the **local population of filenames** as structural evidence.

For example, leading values `1, 2, 3, ... 30` in one directory provide evidence of a sequence; `61, 62, ... 80` provide the same kind of structural evidence.

Sequence evidence is a property of a population, not an isolated number. The Decoding Plan Builder may propose:

```text
filename.leading_numeric_component
    → identify_sequence_number_candidate
```

The proposal records structural evidence such as observed range, coverage, and duplicates. It does not decide what the sequence means.

> **The filename provides decoding guidance, but it does not by itself establish semantic meaning.**

> **A numeric component should initially be recorded only as a positional/textual observation. Its meaning—track number, year, date, title component, version, duplicate marker, etc.—must come from filename grammar and/or other evidence.**

## 23. Current implementation boundary

The builder is deliberately an assembly layer. It succeeds when it can take the current Explorer Tree / Decoding Plan / Candidate Extraction / Metadata Evidence outputs and produce one inspectable Candidate Record per terminal source object while retaining every input observation.

Multiple observations explicitly defined as multi-valued are preserved without being misclassified as conflicts.

## 24. Governing architectural rules

> **A Candidate Record is an assembly of source evidence, not a resolved assertion.**

> **Multiple observations are not automatically conflicts. Conflict requires incompatible assertions within a concept that is expected to be singular.**

> **Do not add a new ingestion verb until a new requirement cannot be expressed clearly using the existing verbs, an existing decoder, and rule parameters.**
