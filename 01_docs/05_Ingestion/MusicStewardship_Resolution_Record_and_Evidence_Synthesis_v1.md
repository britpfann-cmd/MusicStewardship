# MusicStewardship Resolution Record and Evidence Synthesis — v1

## Purpose

Resolution synthesizes all available evidence associated with a source object and its source context to propose semantic facts, while preserving every underlying observation and its provenance.

Resolution is downstream of Candidate Record construction. It does not replace, rewrite, normalize away, or discard Candidate Record evidence.

## Pipeline

Explorer Tree → Semantic Map → Decoding Plan → Candidate Extraction → Candidate Record → Resolution → Entity/Value Resolution

## Core principle

**Use everything we know, but do not pretend we know more than the evidence supports.**

Resolution may use:

- complete directory ancestry and directory semantics
- complete original filename and decoded filename observations
- embedded metadata
- technical/audio metadata
- source-specific decoded evidence
- relationships to sibling or otherwise related source objects when available

Directory context is semantic evidence as well as provenance.

## Resolution Record

One Resolution Record is associated with one Candidate Record/source object.

### Structure

```text
ResolutionRecord
├── source
│   └── candidate_record_id
├── context
│   ├── source_root
│   ├── ancestor directories
│   ├── sibling/related source objects
│   └── source collection context
├── evidence
│   ├── directory
│   ├── filename
│   ├── embedded_metadata
│   ├── technical
│   └── source_specific
├── evidence_sets
├── propositions
└── resolution_status
```

## Evidence Set

An Evidence Set is a defined collection of observations considered together when resolving one or more semantic attributes.

Evidence Sets do not merge or erase observations. Each member retains its original evidence identifier and source locator.

An Evidence Set may combine:

- directory observations
- filename observations
- embedded metadata observations
- technical observations
- source-specific observations
- contextual observations from related source objects

## Semantic Proposition

A Semantic Proposition is an assertion about a candidate semantic attribute derived from one or more preserved observations.

Minimum structure:

```text
Proposition
├── proposition_id
├── attribute
├── value
├── status
├── supported_by[]
├── context_used[]
├── derivation
└── notes
```

### Status

- `resolved` — available evidence supports one specific interpretation within the current source context.
- `ambiguous` — multiple interpretations remain plausible.
- `unresolved` — available evidence is insufficient for a semantic interpretation.

`resolved` does not necessarily mean resolved to a canonical entity. Canonical entity/value matching is a later concern.

## Important distinction

### Interpretation

What does the source evidence appear to mean?

Example:

```text
9713
→ possible TangoTunes catalog/matrix identifier
```

### Resolution

Which canonical value/entity does that interpretation refer to?

Example:

```text
TangoTunes identifier 9713
→ canonical source identifier record
```

These are separate stages.

## Evidence use

Evidence is not assigned a universal authority ranking.

Instead, resolution considers:

1. directness of the evidence
2. source-specific grammar
3. consistency among independent observations
4. directory context
5. filename context
6. embedded metadata
7. relationships among source objects
8. known source behavior

A proposition should record *why* its supporting evidence was considered relevant.

The system must not implement a generic rule such as "metadata beats filename."

## Combining track and context

Resolution must be able to reason over the complete source object rather than resolving each field in isolation.

Example:

```text
Directory:
    BIAGI-ALL
    A000865-AIF

Filename:
    El 13 9713_RP.aif

Embedded metadata:
    title        = El 13
    artist       = Andrés Falgás
    album_artist = Rodolfo Biagi
    date         = 1940
    comment      = 1940-04-12
```

The filename's `13` should not be assigned meaning from the number alone.

The combined evidence can support a proposition concerning the title because:

- the embedded title supplies `El 13`
- the filename supplies `El`, `13`
- the directory supplies `BIAGI-ALL`
- the complete source object supplies the relationship among these observations

The original filename observations remain intact.

## Absence

Resolution must distinguish:

- known absence
- unknown/not observed

Lack of an observation must not be converted into a negative semantic fact.

## Residual evidence

Evidence that is not used by a proposition remains preserved as residual evidence.

Resolution must never discard unexplained evidence merely because it is not currently useful.

## Conflicts

Resolution may identify conflicting propositions or incompatible observations.

It must not silently select one and discard the other.

A conflict should retain:

- competing values
- supporting evidence for each
- context
- unresolved status

## Multi-valued observations

Attributes known to be multi-valued may have multiple observations without constituting a conflict.

This follows the Candidate Record rule already established for `filename_numeric_component`.

## Relationship to Candidate Record

Candidate Record is the preserved evidence assembly.

Resolution is an interpretation layer over that record.

Therefore:

```text
Candidate Record = evidence boundary
Resolution Record = semantic interpretation boundary
```

The Resolution Record must retain lineage back to the Candidate Record and ultimately to the source object.

## v1 scope

The first prototype deliberately does NOT:

- perform fuzzy matching
- query MusicBrainz or other external authorities
- choose canonical artist identities
- infer musical meaning from numeric values alone
- replace source values with canonical values
- rank evidence using a universal authority hierarchy
- attempt broad cross-source entity resolution

It DOES:

- load Candidate Records
- preserve source and context
- group evidence by channel
- identify directly usable metadata propositions
- retain filename/directory observations as contextual evidence
- build explicit Evidence Sets
- attach provenance to propositions
- expose unresolved/ambiguous evidence rather than guessing

## Verified v1 Baseline

The v1 prototype was verified against the TangoTunes `BIAGI-ALL/A000865-AIF` sample on 2026-09-18.

### Candidate Record baseline

- Candidate Records: **42**
- Candidate Record observations: **1,254**
- Conflicted Candidate Records: **0**
- Incomplete Candidate Records: **1**
- The one incomplete record is the preserved `.DS_Store` artifact.

The metadata evidence set contained **1,006 observations for 40 audio files**. The Candidate Record builder was corrected so that source-object identity is based on the complete normalized source path rather than an exact `(source_root, relative_path)` pair. This permits evidence generated from a narrower source root to attach to records generated from the original collection root.

Original metadata `evidence_id` values are preserved through Candidate Record construction, maintaining direct lineage to the metadata evidence decoder.

### Resolution baseline

- Resolution Records: **42**
- Semantic propositions: **362**
- Proposition status: **362 `resolved`**
- Records with 9 propositions: **38**
- Records with 10 propositions: **2**
- Records with 0 propositions: **2**
- Zero-proposition records: `.DS_Store` and `BIAGI01.jpg`

The 40 audio files all produced semantic propositions. The non-audio artifacts remained preserved without being incorrectly interpreted as musical objects.

### Verified evidence behavior

For `El 13 9713_RP.aif`:

- 32 observations were assembled.
- Channels were:
  - metadata: 25
  - filename: 4
  - directory: 2
  - source-specific: 1
- Metadata propositions included title, artist, album, album artist, genre, comment, composer, publisher, and date.
- Filename numeric observations remained separate and were not assigned musical meaning merely from their numeric form.
- Directory and filename evidence remained available as contextual evidence.
- No conflict was created.

### Baseline architectural result

The verified chain is:

**Explorer Tree → Semantic Map → Decoding Plan → Candidate Extraction → Candidate Record → Metadata Evidence → Resolution Record / Semantic Propositions**

The test demonstrates the intended separation:

> **Candidate Record = preserved evidence boundary**

> **Resolution Record = semantic interpretation boundary**

The test also demonstrates the governing principle:

> **Extract facts; preserve evidence.**

### Freeze status

**TangoTunes A000865 Resolution v1 is a frozen working baseline as of 2026-09-18.**

No further changes to the working ingestion or resolution code should be made merely to improve this sample. Future changes should be driven by cross-source testing or a demonstrated requirement that cannot be expressed within the existing architecture.

## Next expansion

After the v1 prototype is verified, add source-specific interpretation rules.

For TangoTunes, those rules can investigate the meaning of:

- `A000865-AIF`
- numeric filename components such as `13` and `9713`
- terminal suffixes such as `RP` and `TT`

using the observed directory grammar, filename grammar, embedded metadata, and broader source samples.

Only after those interpretations are established should canonical entity/value resolution be introduced.
