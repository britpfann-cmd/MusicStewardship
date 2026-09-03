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
