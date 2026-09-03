# IMPL-NORM-001 — Cross-Source Normalization Implementation Baseline

**Status:** Implementation plan / verification target  
**Specification:** SPEC-NORM-001  
**Design:** DES-NORM-001  
**Requirement:** REQ-NORM-001

## Implementation boundary

Cross-source normalization SHALL be added without bypassing `EntityGateway`.

```text
source adapter
    ↓
preserved source observation
    ↓
common normalized observation
    ↓
EntityGateway
```

Source-specific adapters may decode source grammar, but canonical entity creation and association remain responsibilities of the common gateway.

## Controlled test corpus

The first implementation test should contain:

1. multiple representations of the same person;
2. multiple representations of the same group;
3. multiple representations of the same song;
4. at least one possessed-music representation;
5. at least one reference-only entity;
6. at least one intentionally distinct pair that normalizes similarly.

The corpus should be small enough for human inspection.

## Constraint

Do not introduce a large fuzzy-matching system merely to make the test pass. Ambiguous cases should remain reviewable.
