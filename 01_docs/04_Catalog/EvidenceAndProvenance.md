# Evidence and Provenance

**Status:** Current architectural baseline  
**Version:** V1 — evolving

## Purpose

Defines how MusicStewardship preserves evidence and provenance underlying catalog assertions and identity decisions.

## Preserve the observation

Source information is evidence. Preserve information supplied by a source rather than silently replacing it with the current canonical interpretation.

## Evidence may include

- source catalog records
- source identifiers
- filenames and directory context
- embedded metadata
- recording dates
- record, matrix, and take numbers
- external references
- source release information
- authentication or matching results
- later analytical or acoustic evidence

## CatalogedInstance

A CatalogedInstance represents a source-specific documented representation of a Performance. It supplements Performance identity rather than redefining it.

## Evidence versus interpretation

The catalog should distinguish:

1. what the source said;
2. what deterministic processing changed;
3. what the catalog currently interprets that information to mean.

The interpretation may change without destroying the original evidence.

## Conflicting evidence

Conflicting sources are expected. Retain conflicting claims rather than silently discarding one. The current interpretation may be revised as stronger evidence becomes available.

## Authentication

Authentication status describes the current assessment of evidence. It is not an irreversible declaration of truth.

## Traceability

Where practical, catalog assertions based on external information should permit traceback to the supporting source record or evidence.

## Future evidence

Audio-derived or acoustic evidence may contribute to identifying or associating an Asset with a Performance. Such evidence supplements provenance; it does not replace it.

---

## V2 Addendum — 2026-10-02 CatalogedInstance and Two Histories

The earlier definition of CatalogedInstance as only a source-specific documented representation of a Performance is too narrow for the current working model.

A **CatalogedInstance** is the persistent base catalog object created for an ingested instance. It retains a durable relationship to its originating Library Card/source evidence and carries MusicStewardship's evolving current knowledge about that instance. Its upward associations may initially be incomplete or provisional and may later connect to Recording, Performance, Work, Release, and other entities.

The original Library Card/source submission remains preserved evidence. A Library Item remains the owned file/artifact. Neither is replaced by CatalogedInstance.

Two histories are intentionally distinct:

- **evidence history** preserves what was supplied, observed, or asserted by sources and how it was transformed;
- **catalog revision history** preserves changes in MusicStewardship's interpretation/current state.

Current catalog knowledge may change without rewriting either the original evidence or prior catalog history.

External seed harvesting is also evidence acquisition. A seed's external origin must remain traceable, and seed creation does not make the external source canonical truth.
