# MusicStewardship Development History and Architectural Evolution

**Document ID:** HIST-001
**Status:** Working historical summary
**Revision:** A
**Date:** 2026-09-10

## 1. Purpose

This document records the evolution of MusicStewardship from exploratory experiments in cataloging disparate tango-music sources into the more mature architecture now being developed for uniform catalog construction.

It is a historical and architectural orientation document. It does not replace current requirements, architecture, specifications, or implementation documents. Its purpose is to preserve the reasoning path by which those documents evolved and to make earlier experimental work reusable.

## 2. Starting Problem

The project began with a practical problem: a personal tango music collection had accumulated material from multiple sources, each expressing musical knowledge differently.

Sources could differ in:

- metadata fields and vocabulary;
- filenames;
- directory hierarchy and directory depth;
- embedded compound fields;
- release and recording identifiers;
- dates and historical periods;
- descriptions of orchestras, singers, composers, and other people;
- restoration and transfer notes;
- completeness and reliability.

A simple file-renaming or metadata-cleaning program could improve individual files, but could not provide a durable common catalog without losing source-specific meaning and provenance.

The early work therefore evolved from file processing toward source interpretation and knowledge reconstruction.

## 3. Experimental Source Decoding

The first substantial experiments concentrated on individual source collections and especially on Tango Time Travel (TTT).

The work examined real source records and audio files to discover what information was actually encoded in:

- metadata;
- compound fields;
- filenames;
- folder structures;
- collection organization;
- accompanying documentation;
- source identifiers.

Low-level tools were written and tested against deliberately varied TTT samples. These tests concentrated on boundary conditions and on determining whether individual source constructs could be decoded, decomposed, normalized, or otherwise interpreted.

This work produced empirical knowledge about source grammar before a general ingestion engine existed.

## 4. Recognition of the Source-Specific Grammar Problem

As experimentation expanded, it became clear that different sources could express substantially the same musical reality in different ways.

A source-specific program for every collection would therefore create a growing collection of unrelated special cases.

The architectural turning point was the separation of:

**source-specific interpretation**

from

**common processing machinery**.

The source contributes a grammar and mapping rule set. The common engine supplies reusable operations for applying those rules.

This became the principle:

> **Common model, source-specific interpretation.**

## 5. TTT as the Best-Case Source

TTT became the principal development sample because its cataloging structure is unusually comprehensive and carefully researched.

The TTT experiments demonstrated that useful information is distributed across more than simple track metadata. Compound fields, source identifiers, comments, hierarchy, and associated source material can all carry meaning.

TTT therefore became more than a convenient test source. It became a stress test for whether the architecture is sufficiently expressive to handle a highly detailed source without modifying the common processing machinery.

The intended implication is:

> If the common architecture can faithfully express the information supplied by TTT, less-complete sources should normally require smaller source-specific rule sets rather than special processing machinery.

## 6. Preservation of Source Evidence

A second major architectural development was recognition that translation must not destroy the source representation.

The system distinguishes:

1. what the source actually said;
2. what deterministic processing did to it;
3. what the catalog currently interprets it to mean.

Raw source values remain evidence even when components are extracted or normalized.

This led to the broader principle:

> **Extract facts; preserve evidence.**

Residual information is not discarded merely because it cannot currently be interpreted or is not presently required.

## 7. Emergence of the Common Vocabulary

The project then moved from source decoding toward a common MusicStewardship vocabulary.

The purpose is not to force every source into one mold. Rather, source expressions are translated into interoperable source assertions while preserving source context and provenance.

The model also separates different levels of musical reality. In particular, the system distinguishes concepts such as:

- Person;
- Ensemble;
- Composition;
- Performance;
- Recording;
- Release;
- Audio Asset;
- Source;
- Source Collection;
- Cataloged Instance;
- provenance and evidence.

This prevents repeated appearances of a name or recording description from being mistaken for repeated creation of the same real-world entity.

## 8. Entity Resolution as a Separate Stage

An important architectural boundary emerged between **preparing information for the catalog** and **deciding what entities that information belongs to**.

Ingestion prepares catalog-ready assertions. Entity Management subsequently determines whether a value or entity is:

- already known;
- a synonym or alias for something known;
- previously unknown and therefore requires creation/provisional treatment.

This separation allows source interpretation to remain source-specific while entity management remains common across all sources.

## 9. CORE, ASSOCIATED, and RESIDUAL

The project eventually formalized three mutually exclusive information classes:

### CORE

Information required for ingestion to proceed.

### ASSOCIATED

Useful additional information that should be captured when the current toolset can decode or preserve it.

### RESIDUAL

Information that cannot presently be interpreted, is not presently needed, or otherwise remains outside the current transformation scope.

These classifications describe the semantic role of information, not the processing action applied to it.

They are therefore orthogonal to processing operations, assurance, and provenance.

## 10. Orthogonal Ingestion Universe

The resulting architecture defines several independent dimensions:

- **Information class:** CORE / ASSOCIATED / RESIDUAL;
- **Processing disposition:** extract, decompose, normalize, combine, derive, reference, preserve, etc.;
- **Assurance:** observed/provisional/reconciled/canonical and related states;
- **Provenance:** where the information and resulting assertion came from.

This permits information to be retained even when it cannot presently be interpreted and permits interpretations to improve without rewriting historical source evidence.

## 11. Rosetta Stone Concept

The source-specific rule set became the conceptual **Rosetta Stone**.

For TTT, the Rosetta Stone is intended to describe:

- source grammar;
- field meanings;
- hierarchy semantics;
- decomposition rules;
- vocabulary mappings;
- contextual rules;
- identity cross-reference rules;
- residual dispositions;
- provenance requirements.

The Rosetta Stone is declarative knowledge about the source. It is not the processing engine.

The desired result is a human-readable and machine-readable interpreter CSV that can be inspected for completeness and closure.

## 12. Generic Transformation Engine

The next unbuilt major component is the generic transformation engine.

Its responsibility is to execute the source rule set using reusable operations already explored in the experimental work.

Conceptually:

```text
source observation
       +
source Rosetta Stone rule
       ↓
generic transformation operation
       ↓
catalog-ready source assertion
```

The engine must not contain TTT-specific assumptions that belong in the TTT rule set.

This is the architectural mechanism by which additional sources can be added primarily through source research and mapping rather than new programming.

## 13. Catalog Interchange CSV

The project retained CSV as an important interchange representation because it is:

- human-readable;
- machine-readable;
- portable;
- inspectable;
- archivable;
- suitable for sharing and independent review.

The intended flow is:

```text
Source
  ↓
source-specific Rosetta Stone
  ↓
generic transformation engine
  ↓
catalog interchange CSV
  ↓
reference-library importer
```

The interchange CSV is therefore the boundary between interpretation/transformation and the subsequent construction of the reference catalog.

## 14. Reference Library Construction

The reference-library importer is a separate concern from source interpretation.

It receives uniform catalog interchange records and builds a consistent reference library while managing:

- duplicate entities;
- synonyms and aliases;
- conflicting assertions;
- provisional entities;
- relationships;
- assurance;
- provenance;
- later reconciliation.

External resources such as Discogs and TANGO-DJ.AT can provide corroborating evidence, identifiers, alternate representations, and validation. They do not automatically override the native source or serve as acceptance gates.

## 15. Process Control

The project also evolved from one-shot scripts toward persistent process control.

Processing must be:

- observable;
- resumable;
- auditable;
- non-destructive;
- capable of recording exceptions;
- capable of identifying changed inputs;
- capable of recursively reprocessing affected derived information.

Initially this information can itself be represented with human-readable interchange records such as CSV. A later database can provide richer queries and reporting.

An important architectural insight is that process control is not merely bookkeeping:

> **Process control is the operational state of MusicStewardship. Its machine-readable record is simultaneously the foundation for the human operational interface.**

The same state that allows a machine to resume processing allows a human to see what has happened, what remains, what needs review, and why.

## 16. Development Maturity

The project has therefore progressed through several recognizable stages:

```text
FILE / METADATA EXPERIMENTS
        ↓
SOURCE-SPECIFIC DECODING
        ↓
EMPIRICAL GRAMMAR DISCOVERY
        ↓
SOURCE PRESERVATION + PROVENANCE
        ↓
COMMON VOCABULARY
        ↓
ENTITY / PERFORMANCE SEPARATION
        ↓
ORTHOGONAL INGESTION ARCHITECTURE
        ↓
ROSETTA STONE MODEL
        ↓
[CURRENT DEVELOPMENT]
TTT ROSETTA STONE
        ↓
GENERIC TRANSFORMATION ENGINE
        ↓
CATALOG INTERCHANGE CSV
        ↓
REFERENCE LIBRARY IMPORTER
        ↓
PERSISTENT PROCESS CONTROL / HUMAN INTERFACE
```

## 17. Current Position

The project is currently between experimental discovery and construction of the reusable ingestion machinery.

The low-level TTT experiments have demonstrated many individual transformations and boundary conditions. They have not yet been assembled into the complete coordinated TTT ingestion engine.

The immediate objective is therefore not database insertion.

It is to construct a sufficiently complete TTT Rosetta Stone and use it to drive the generic transformation architecture.

## 18. Historical Material as a Reusable Asset

Earlier experimental documents and scripts should not automatically be discarded when superseded.

They may contain:

- discovered source grammar;
- tested boundary conditions;
- failed approaches;
- vocabulary decisions;
- transformation examples;
- evidence for architectural decisions;
- reusable test cases.

The mature project should distinguish current authoritative specifications from historical exploratory material while retaining both.

The historical corpus is therefore part of the project's research memory.

## 19. Long-Term Architectural Goal

The mature system is intended to make the addition of another source principally a matter of:

1. preserving and surveying the source;
2. discovering its grammar;
3. constructing its source-specific Rosetta Stone;
4. testing the rules;
5. applying the common transformation engine;
6. feeding the resulting catalog interchange records into the common reference-library importer.

The machinery should remain common while the knowledge required to interpret each source remains explicitly represented as source-specific rules.

## 20. Guiding Principle

The development has moved from asking:

> **How do we clean up these files?**

to:

> **How do we reconstruct and preserve the knowledge expressed by many different sources, translate it into a common representational language, and build an evolving reference library without losing the evidence from which our understanding came?**

That change in question is the central evolution of the MusicStewardship project.
