# Canonical Data Model

## CSV Public Interface

CSV datasets are a deliberate public and interchange representation of
MusicStewardship catalog state.

They are intended to be human-readable, machine-readable, portable,
inspectable, archivable, and usable independently of the internal
implementation.

The project experience with decoded external representations, including
tango-dj.at HTML, has demonstrated the practical value of flat CSV datasets
as a transfer and reuse interface.

CSV is therefore a public interface, not merely an incidental output format.

Internal processing may use other representations when those better support
processing, querying, validation, or relationship management. Examples
include JSON, SQLite, and in-memory structures. Such internal representations
do not replace the CSV public interface.

## Current State and History

Published CSV catalog datasets represent a current snapshot of catalog state
at the time they are produced.

CSV snapshot tables should remain simple and should not be burdened with
historical state merely because the catalog itself evolves.

Historical evolution of catalog assertions and associations is retained
separately and should be readily accessible when needed.

Ordinary catalog use should answer:

> What do we currently believe?

without requiring the user to examine how that conclusion was reached.

History should be available to the curious without burdening routine use.

## Stable Identity

Every canonical entity shall possess a stable identifier that remains
constant throughout its lifetime.

Identifiers shall never encode implementation details.

Identifiers remain independent of:

- filenames
- export formats
- playback applications
- database implementations

## Schema Design

Schemas should favor:

- explicit fields
- normalized information
- stable terminology
- deterministic interpretation

Fields should describe canonical meaning rather than application behavior.

## Relationships

Canonical datasets may reference one another through stable identifiers.

Relationships should express semantic meaning rather than storage structure.

## Enumerated Values

Controlled vocabularies should be used whenever practical.

Examples include:

- Status
- Category
- Genre
- Placement
- AudioType

Enumerations should be documented and versioned independently.

## Versioning

Canonical datasets evolve over time.

Changes should preserve historical meaning whenever possible.

Breaking schema changes require documentation and migration guidance.

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

## Human Readability

Canonical datasets should remain understandable to knowledgeable users.

Where practical:

- field names should be descriptive
- terminology should follow repository conventions
- comments and documentation should accompany complex datasets

Human readability is considered a design objective rather than an
implementation constraint.

## Implementation Independence

Canonical datasets shall not contain:

- application-specific filenames
- software-specific identifiers
- user interface state
- implementation logic

Such information belongs to export profiles or generated artifacts.

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

## Addendum — 2026-10-02 Current Operational State and Revision History

The first database implementation shall optimize normal catalog use for an immediately accessible **current state**. Current state answers: **What do we currently believe?**

Catalog evolution is retained separately as maintenance/audit history. Revision history must be sufficient for diagnosis, corrective action, rollback/reconstruction where practical, and explanation of how present catalog knowledge was reached. Ordinary catalog queries should not require traversal of revision history.

Evidence history and catalog revision history are distinct. Evidence history preserves what came from sources; catalog revision history preserves how MusicStewardship's interpretation changed.

The physical history mechanism is an implementation decision and is not fixed by the canonical model.
