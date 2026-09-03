# Audio-Derived Identity Evidence

**Document Type:** Architecture Requirement
**Status:** Planned
**Scope:** MusicStewardship ingestion and identity resolution

---

## 1. Purpose

MusicStewardship shall accommodate audio-derived evidence as an
independent layer of identity resolution.

Textual metadata and filenames provide valuable identity evidence,
particularly in curated collections such as Crackling Tunes. However,
as ingestion expands to less-curated collections, textual identity
information may become incomplete, inconsistent, corrupted, or absent.

Audio characteristics therefore need to become an additional means of
determining whether two files represent the same underlying recording.

---

## 2. Architectural Principle

**Audio identity is an additional evidence layer, not an additional
mandatory processing stage.**

The initial ingestion system may operate using textual and other
non-audio evidence. Audio analysis can subsequently be introduced
without requiring a redesign of the existing identity model.

The audio layer shall supplement, rather than replace, the existing
evidence model.

---


## 3. Requirements

### 3.1 Independent Evidence Layer

Audio-derived evidence shall be represented separately from textual
identity evidence.

The identity model shall not assume that an identity conclusion comes
from a single evidence source.

### 3.2 Incremental Introduction

Audio analysis shall be capable of being introduced after the initial
text-oriented ingestion pipeline is operational.

Existing ingestion and identity records shall remain valid when audio
evidence is subsequently added.

### 3.3 Preservation of Source Evidence

Audio analysis shall supplement, rather than overwrite, the original
textual and source evidence.

Identity resolution shall remain capable of showing the evidence on
which a conclusion was based.

### 3.4 Audio Fingerprinting

The architecture shall support generation and storage of audio
fingerprints or equivalent acoustic identity signatures.

These signatures shall permit comparison of recordings across:

- different files
- different file formats
- different sources
- different collections
- differently named or incompletely identified files

The specific fingerprinting technology is an implementation decision
and is not prescribed by this requirement.

### 3.5 Audio Characteristics

The audio evidence record should retain the characteristics necessary
to interpret the analysis and, where practical, reproduce it.

Potential attributes include:

- audio format/container
- duration
- sample rate
- channel configuration
- bit depth
- encoding characteristics
- fingerprint algorithm
- fingerprint algorithm version
- fingerprint
- analysis status
- analysis timestamp

The ingestion system should distinguish between the file's declared
format and the format determined by examination of the actual audio
content.

### 3.6 Combination of Evidence

Identity resolution shall eventually be able to combine independent
evidence streams, including:

- textual metadata
- filename information
- source/catalog identifiers
- audio fingerprints
- other external evidence as subsequently incorporated

The architecture shall permit additional evidence types to be added
without disrupting the existing identity model.

### 3.7 Confidence and Ambiguity

Audio evidence shall contribute to an identity-resolution assessment
rather than necessarily producing an unconditional identity assertion.

Where audio evidence conflicts with textual or other evidence, the
conflict shall remain visible and available for review.

---

## Identity-Evidence Confidence

Audio fingerprinting is a planned independent identity-evidence layer.

A reliable audio fingerprint match is expected to provide very high-confidence
evidence that two files contain the same underlying audio recording. This
evidence may be used to corroborate or resolve identity when textual metadata
is incomplete, ambiguous, inconsistent, or unreliable.

Audio-derived evidence shall remain independent of the underlying MusicStewardship
identity model. Introducing fingerprinting must not require a change to the
Track, recording, or other core identity objects.

The identity-resolution process should be capable of combining multiple
evidence sources, including:

- textual metadata;
- source and provenance information;
- catalog or release information;
- audio fingerprint evidence.

Confidence thresholds are intentionally not fixed at this stage. They shall be
established empirically after testing fingerprint behavior across different
audio formats, encodings, remasters, trimming, and other transformations.

The system should distinguish between:

- evidence that two files contain equivalent audio; and
- the higher-level conclusion that they represent the same MusicStewardship
  recording identity.

A fingerprint match is therefore evidence for identity resolution, not by
itself a replacement for the identity model.
## 4. Development Progression

The role of audio evidence is expected to change as the collection
becomes less curated.

### Stage 1 — Curated Collections

Collections such as Crackling Tunes generally provide substantial
textual and catalog evidence.

Audio analysis can initially serve primarily as corroborating evidence
and as a means of resolving ambiguities.

### Stage 2 — Mixed-Quality Collections

As ingestion expands beyond highly curated sources:

- textual evidence becomes less consistent
- filenames become less reliable
- metadata may be incomplete
- multiple representations of the same recording become more common

Audio evidence becomes increasingly valuable.

### Stage 3 — Poorly Identified Collections

For files with little or unreliable identity information, audio
fingerprinting may become essential to automated identity resolution.

The architecture should therefore be designed for this eventual case
even though it is not required to make audio analysis a prerequisite
for the current ingestion work.

---

## 5. Relationship to Current Ingestion Work

The current Crackling Tunes work provides an appropriate environment
for developing the identity model because the collection contains
relatively rich source and metadata information.

The initial work should therefore concentrate on understanding and
mapping the available textual and source evidence.

Audio analysis should be introduced as an additional layer when the
ingestion framework is sufficiently stable to support it.

The fact that audio analysis is deferred does not make it optional as
an architectural capability.

---

## 6. Evidence Model

Conceptually, identity resolution should evolve toward a model such as:

    Source Evidence
          │
          ├── Filename / path
          ├── Embedded metadata
          ├── Catalog identifiers
          ├── External references
          │
          └── Audio Evidence
                  ├── Format
                  ├── Technical characteristics
                  └── Fingerprint
                          │
                          ▼
                  Identity Assessment
                          │
                    ┌─────┴─────┐
                    │           │
                 Match       Ambiguous
                    │           │
                 resolved      review

This is an evidence model rather than a prescribed implementation.

---

## 7. Non-Goals

This requirement does not currently specify:

- a particular fingerprinting algorithm
- a particular audio-analysis library
- when every file must be fingerprinted
- whether fingerprints must be generated during initial ingestion
- an automatic identity decision based solely on audio
- replacement of textual metadata with audio-derived identity

Those decisions belong to later implementation and evaluation work.

---

## 8. Future Implementation Considerations

When the audio layer is implemented, testing should include:

- identical recordings in different file formats
- different encodings of the same recording
- files with different metadata but identical audio
- files with misleading filenames
- alternate transfers of the same historical recording
- recordings with similar but non-identical audio
- degraded or incomplete recordings
- duplicate files
- files for which no reliable textual identity can be established

The results of these tests should inform the confidence model and the
rules for combining audio evidence with textual evidence.

---

## 9. Architectural Decision

The MusicStewardship identity architecture shall be designed so that
audio-derived evidence can be added as an independent identity
evidence layer without disrupting the existing ingestion model.

This requirement shall be considered during development of the
text-identity ingestion pipeline, even before audio analysis itself is
implemented.

## Identity-Evidence Confidence

Audio fingerprinting is a planned independent identity-evidence layer.

A reliable audio fingerprint match is expected to provide very high-confidence
evidence that two files contain the same underlying audio recording. This
evidence may be used to corroborate or resolve identity when textual metadata
is incomplete, ambiguous, inconsistent, or unreliable.

Audio-derived evidence shall remain independent of the underlying MusicStewardship
identity model. Introducing fingerprinting must not require a change to the
Track, recording, or other core identity objects.

The identity-resolution process should be capable of combining multiple
evidence sources, including:

- textual metadata;
- source and provenance information;
- catalog or release information;
- audio fingerprint evidence.

Confidence thresholds are intentionally not fixed at this stage. They shall be
established empirically after testing fingerprint behavior across different
audio formats, encodings, remasters, trimming, and other transformations.

The system should distinguish between:

- evidence that two files contain equivalent audio; and
- the higher-level conclusion that they represent the same MusicStewardship
  recording identity.

A fingerprint match is therefore evidence for identity resolution, not by
itself a replacement for the identity model.