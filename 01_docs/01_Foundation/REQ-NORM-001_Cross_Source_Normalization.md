# REQ-NORM-001 — Cross-Source Normalization and Convergence

**Status:** Proposed requirement

## Requirement

Equivalent observations of an entity from different sources SHALL be capable of converging through a common normalization and identity process to the same canonical entity.

This applies to reference-source observations and observations derived from musical assets actually possessed by MusicStewardship.

## Rationale

MusicStewardship receives observations from multiple sources whose naming, field conventions, punctuation, ordering, abbreviations, transliterations, and other representations may differ.

If each source is normalized only within its own vocabulary, the database will accumulate artificial disparities.

## Required behavior

1. Preserve every original source observation.
2. Translate source-specific representations into the common normalized vocabulary.
3. Allow equivalent representations to produce equivalent normalized identity candidates.
4. Perform identity resolution through the common entity-management boundary.
5. Allow supported equivalent observations to associate with one canonical Entity ID.
6. Do not let normalization itself assert identity.
7. Do not force distinct entities together merely because normalized text is similar.
8. Keep reference-source and possessed-music provenance distinguishable.
9. Allow a reference-derived entity to exist before corresponding possessed music.
10. When possessed music is encountered later, evaluate it against existing normalized identity space before creating a duplicate.
11. Preserve conflicting observations for later interpretation.

## Scope boundary

This requirement does not prescribe a matching algorithm, authority service, confidence score, merge policy, or database schema.

## Traceability

`PRN-002 → REQ-NORM-001`
