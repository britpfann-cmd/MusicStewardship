# Canonical Data Model

## Purpose

This document defines the principles governing canonical data within the
Music Stewardship architecture.

Canonical data represents the authoritative description of music,
performances, performance objects, observations, knowledge, and related
entities maintained by the repository. All implementation software,
generated artifacts, exports, and client applications derive their
information from these canonical datasets.

The purpose of the canonical data model is to ensure that information is
represented once, preserved consistently, and reused across multiple
applications without duplication or loss of meaning.

---

## Scope

This specification establishes:

- canonical data principles
- dataset organization
- identifier requirements
- schema conventions
- relationship modeling
- lifecycle management
- implementation independence

It applies to every canonical dataset maintained by Music Stewardship.

---

## Design Principles

Canonical data shall:

- exist independently of implementation software
- represent meaning rather than presentation
- avoid unnecessary duplication
- preserve stable identity
- support multiple export targets
- remain understandable to both humans and software
- evolve without invalidating historical information

---

## Architectural Context

Canonical data occupies the central layer of the Music Stewardship
architecture.

```
Documentation
        │
        ▼
Canonical Data
        │
        ▼
Implementation
        │
        ▼
Generated Artifacts
        │
        ▼
Client Applications
```

Documentation describes the model.

Canonical data embodies the model.

Implementations transform the model.

Generated artifacts deliver the model.

---

## Canonical Dataset Characteristics

Every canonical dataset should possess:

- a clearly defined purpose
- stable schema
- documented ownership
- version history
- validation rules
- machine-readable representation

Datasets should remain implementation-independent.

---

## Dataset Organization

Canonical datasets are maintained within the repository data directory.

Typical examples include:

```
02_data/

    PerformanceObjects.csv

    ExportProfiles.csv

    Genres.csv

    Applications.csv

    Observations.csv
```

Future implementations may migrate to SQLite, JSON, XML, or other
storage formats without changing the conceptual model.

---

## Canonical Identity

Every canonical entity shall possess a stable identifier that remains
constant throughout its lifetime.

Identifiers shall never encode implementation details.

Identifiers remain independent of:

- filenames
- export formats
- playback applications
- database implementations

---

## Schema Design

Schemas should favor:

- explicit fields
- normalized information
- stable terminology
- deterministic interpretation

Fields should describe canonical meaning rather than application
behavior.

---

## Relationships

Canonical datasets may reference one another through stable identifiers.

Relationships should express semantic meaning rather than storage
structure.

Examples include:

- Recording belongs to Collection
- Performance Object annotates Musical Unit
- Observation references Recording
- Edition derives from Recording

---

## Enumerated Values

Controlled vocabularies should be used whenever practical.

Examples include:

- Status
- Category
- Genre
- Placement
- AudioType

Enumerations should be documented and versioned independently.

---

## Versioning

Canonical datasets evolve over time.

Changes should preserve historical meaning whenever possible.

Breaking schema changes require documentation and migration guidance.

---

## Validation

Every canonical dataset shall support automated validation.

Validation may include:

- required fields
- uniqueness
- identifier integrity
- relationship integrity
- controlled vocabulary verification
- schema compliance

Invalid canonical data shall not be exported.

---

## Human Readability

Canonical datasets should remain understandable to knowledgeable users.

Where practical:

- field names should be descriptive
- terminology should follow repository conventions
- comments and documentation should accompany complex datasets

Human readability is considered a design objective rather than an
implementation constraint.

---

## Implementation Independence

Canonical datasets shall not contain:

- application-specific filenames
- software-specific identifiers
- user interface state
- implementation logic

Such information belongs to export profiles or generated artifacts.

---

## Extensibility

New canonical datasets should follow the conventions established by this
specification.

Future datasets may describe:

- musical works
- recordings
- performances
- musical units
- performance objects
- observations
- analytical results
- editorial knowledge
- provenance
- experience

without requiring changes to the overall architecture.

---

## Relationship to Other Specifications

This document establishes the general principles governing canonical
data.

Individual specifications define particular canonical datasets.

Examples include:

- CanonicalMetadata.md
- PerformanceObjects.md
- ExportModel.md
- PerformanceModel.md

Those specifications inherit the principles defined here while providing
the domain-specific semantics for their respective datasets.