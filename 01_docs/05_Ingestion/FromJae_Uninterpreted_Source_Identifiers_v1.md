# FromJae — Uninterpreted Source Identifiers

## Purpose

This note records the interpretation boundary established during initial FromJae source exploration.

FromJae contains filename and directory information that may reflect a source-specific library or cataloging system. MusicStewardship shall preserve that information without assigning canonical meaning that cannot be supported by the available source evidence.

## Established principle

> **Uninterpreted source identifiers:** Numeric or coded filename components may represent identifiers from a source-specific library or cataloging system. Unless the source's reference system is available, MusicStewardship shall preserve the observed value and its location but shall not assign an external or canonical meaning to it.

## Evidence observed

The FromJae collection contains explicitly named `TANDA` directories. Examples examined include:

- `TANDA CALO BERON`
- `TANDA CARABELLI`
- `TANDA FRESEDO INSTRUMENTAL`
- `TANDA MILONGAS TROILO`

The examined TANDA directories contained four MP3 files with generic sequential filenames such as:

- `Track01.mp3`–`Track04.mp3`
- `Track21.mp3`–`Track24.mp3`
- `Track26.mp3`–`Track29.mp3`

A metadata survey of `TANDA FRESEDO INSTRUMENTAL` found 52 observations for four source objects, all technical metadata, with no extraction errors. The descriptive identity of those four files therefore came from source organization rather than embedded descriptive tags.

## Interpretation boundary

For a filename such as:

`Track21.mp3`

the following are safe observations:

- original filename: `Track21.mp3`
- numeric component: `21`
- numeric component position within the filename
- complete source path and directory context

The following interpretations are **not established** by the available evidence:

- track number
- recording number
- catalog number
- source catalog identifier
- database identifier
- any other canonical identifier

The observed numeric component may be retained as a candidate sequence/identifier observation for later interpretation, but its meaning remains unresolved.

## Relationship to source preservation

The absence of a known interpretation is itself an important stewardship boundary. MusicStewardship must not discard or overwrite the original value merely because its meaning is unknown.

The information flow is:

**Observe → Preserve → Candidate extraction → Interpret when supported → Resolve when possible**

not:

**Observe → Guess → Normalize → Discard the original**

## TANDA implication

A directory explicitly named with `TANDA` is source evidence that the source creator organized the contained recordings as a named grouping. The complete directory name should be preserved.

The name may be used to produce source-specific candidate observations, but the remainder of the name should not automatically be mapped to orchestra, singer, tanda identity, style, period, or another canonical attribute without supporting evidence.

## External reference boundary

If the source owner's catalog, index, database, reference list, or other explanatory material becomes available later, the preserved filename, directory, and source-object provenance provide the evidence needed to revisit these unresolved observations.

Until such reference material is available, MusicStewardship should not attempt to reconstruct the source owner's numbering system.

## Design consequence

The initial FromJae decoding profile should remain deliberately narrow:

1. Preserve source path and directory hierarchy.
2. Preserve original filenames.
3. Detect explicitly named `TANDA` directories as source-structural observations.
4. Preserve the complete TANDA directory name.
5. Extract observable filename numeric components without assigning canonical meaning.
6. Preserve technical metadata.
7. Preserve all unexplained source information as evidence/residual.
8. Do not infer catalog, recording, or track identifiers from `TrackNN`.
9. Do not infer canonical musical attributes solely from directory position.
10. Defer entity resolution and external-reference interpretation.

This is a source-specific decoding boundary, not a statement about the eventual canonical meaning of the collection.
