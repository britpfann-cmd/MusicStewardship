# MusicStewardship — Provenance Assessment & Entity Association Design

**Document ID:** ING-PROV-002  
**Status:** Initial design  
**Revision:** A  
**Date:** 2026-09-20

## 1. Purpose

This document defines the first implementable design for D: Provenance Assessment and Entity Association.

The design deliberately implements only the lowest-hanging-fruit relationship methods first.

D operates on catalog cards produced by C and progressively builds an evidence-bearing network of relationships among cataloged assets, entity candidates, established entities, and external references.

## 2. Design Boundary

C produces a catalog card for each source asset.

D does not replace that catalog card.

D adds relationships and provenance assessments around it.

```text
Source Asset
     ↓
C
     ↓
Catalog Card
     ↓
D
     ├── Entity Candidate
     ├── Existing Entity
     ├── Other Cataloged Asset
     └── External Reference
```

## 3. Initial Design Scope

The first implementation shall support:

1. loading catalog-card information;
2. representing entity candidates;
3. representing established entities;
4. comparing catalog-card values with established information;
5. creating an evidence-bearing relationship assertion;
6. retaining the evidence used by that assertion;
7. allowing the assertion to be reassessed later.

The first matcher shall use only readily available, deterministic evidence.

No fuzzy matching, machine learning, external web search, or audio fingerprinting is required for the first implementation.

## 4. Core Objects

### 4.1 Cataloged Asset

The C-level representation of a source asset.

A Cataloged Asset retains its source identity and cataloging assertions.

At minimum it must remain traceable to the underlying source object.

### 4.2 Entity Candidate

A provisional representation of a musical entity suggested by one or more cataloged assets or other evidence.

An Entity Candidate is not yet an established entity.

It may accumulate supporting catalog cards and evidence.

### 4.3 Entity

An established library entity.

An Entity may be established from an Entity Candidate when the available evidence meets whatever establishment rule is subsequently defined.

An Entity becomes reusable evidence for future D assessments.

### 4.4 Relationship Assertion

An evidence-bearing statement that two library objects have a defined relationship.

Initial examples:

```text
Cataloged Asset → represents → Entity
Cataloged Asset → possibly_represents → Entity Candidate
Cataloged Asset → corresponds_to → Cataloged Asset
Cataloged Asset → corroborates → Cataloged Asset
```

The initial vocabulary should remain small.

## 5. Assertion Structure

The first implementation should support an assertion structure equivalent to:

```text
assertion_id
subject_id
subject_type
relationship_type
object_id
object_type
assessment_status
evidence[]
created_at
updated_at
```

Each evidence item should identify:

```text
evidence_id
evidence_type
evidence_source
source_reference
observed_value
method
notes
```

The exact persistent schema may be refined during implementation.

## 6. Assessment Status

The first design should distinguish at least:

```text
candidate
supported
established
rejected
superseded
```

These describe the state of the relationship assertion, not a universal numerical confidence score.

A relationship may move between states as additional evidence becomes available.

## 7. Evidence-Bearing Relationships

A relationship must never exist only as an unexplained match.

For example:

```text
Asset A
   │
   └── represents ──► Entity X

Evidence:
   title exact match
   orchestra exact match
   source context compatible
```

The implementation must retain enough information to explain why the relationship exists.

## 8. First Matching Method

The first matching method shall be deterministic controlled textual correspondence.

Initial candidate fields may include:

- title;
- artist/orchestra/ensemble;
- singer;
- recording identifier;
- source catalog identifier;
- recording date where explicitly available.

The first implementation shall prefer exact or controlled-normalized correspondence over fuzzy similarity.

Mechanical normalization may include such operations as:

- case folding;
- whitespace normalization;
- Unicode normalization;
- controlled punctuation handling.

Normalization shall never replace the original value.

## 9. Matching Does Not Equal Resolution

A textual match shall create evidence for an association.

It shall not silently convert a source assertion into a canonical fact.

For example:

```text
source title
     │
     ▼
textual correspondence
     │
     ▼
relationship evidence
     │
     ▼
D assessment
```

The original source value remains preserved.

## 10. Entity Candidate Construction

When an asset contains useful cataloging information but no established entity matches it, D may create or contribute evidence to an Entity Candidate.

The candidate should preserve:

- originating asset(s);
- originating assertions;
- source provenance;
- evidence supporting the candidate;
- any conflicting evidence.

Entity candidates may subsequently be merged, split, established, or left unresolved by later D operations.

## 11. Existing Entity Reuse

Before creating a new entity candidate, D should search the existing entity population using the simplest applicable deterministic methods.

This is the first mechanism by which the knowledge accumulated by the library improves later ingestion.

## 12. Asset-to-Asset Relationships

The design shall permit one cataloged asset to refer to another cataloged asset as evidence.

Example:

```text
Asset A
   │
   └── corresponds_to ──► Asset B

Evidence:
    matching title
    matching orchestra
    compatible source context
```

If Asset B already has an established relationship with Entity X, that relationship may become secondary evidence for Asset A.

The provenance chain shall remain visible.

## 13. Evidence Chains

D shall permit evidence to form chains.

Example:

```text
Asset A
   │
   └── correspondence ──► Asset B
                              │
                              └── represents ──► Entity X
```

The second relationship does not automatically become direct proof of the first.

Instead, it is additional evidence whose provenance remains explicit.

## 14. External References

External reference information shall be represented as a separate evidence source.

The first implementation does not need to query external services automatically.

It must, however, leave room for external evidence to be attached later without changing the core relationship model.

## 15. Source Accuracy Assertions

An incoming collection may carry an assessment supplied by its provider concerning cataloging accuracy.

That assessment should be represented as source/collection evidence.

It shall not be silently converted into an established entity relationship.

## 16. Progressive Reassessment

A relationship assertion shall be re-evaluable when new evidence arrives.

Examples:

```text
Initial:
    candidate

Later:
    established asset provides corroboration

Later:
    external reference agrees

Later:
    audio signature agrees
```

The system should retain the evidence history rather than replacing the original assessment without trace.

## 17. Low-Hanging-Fruit Implementation Order

Implementation should proceed approximately as follows:

### D1 — Existing entity exact correspondence

Use obvious catalog-card fields to find an established entity.

### D2 — Existing asset correspondence

Use catalog-card fields to connect incoming assets to already cataloged assets.

### D3 — Entity candidate accumulation

Group repeated compatible assertions into entity candidates.

### D4 — Established entity formation

Define and implement the minimum evidence required to promote an entity candidate.

### D5 — Additional evidence

Add source-specific identifiers, richer text methods, external references, and audio evidence as actual collections demonstrate their value.

This order is intentionally provisional and may change when empirical testing demonstrates a better sequence.

## 18. Determinism

For identical inputs and identical existing knowledge, the first matching implementation shall produce identical relationship candidates and evidence.

Processing order shall be deterministic.

Stable identifiers shall be used for assets, entities, candidates, assertions, and evidence records.

## 19. Idempotence

Repeated processing of an unchanged catalog population shall not create duplicate relationship assertions merely because the same evidence was encountered again.

The system shall recognize previously established assertion/evidence identity.

## 20. Preservation

D shall never:

- modify source assets;
- rewrite C catalog cards merely to obtain a match;
- discard source assertions;
- discard unsuccessful matches;
- silently replace one entity with another;
- collapse conflicting external references into one assertion.

## 21. First Test Target

The first implementation should use a small set of already cataloged material for which the C output is understood.

The test should demonstrate:

```text
catalog cards
     ↓
existing entity population
     ↓
simple deterministic matching
     ↓
relationship assertions
     ↓
evidence trail
     ↓
repeat run without duplicate assertions
```

The initial test should include both:

- positive obvious matches; and
- assets for which no established relationship should be created.

## 22. Architectural Rule

> **D adds knowledge about relationships; it does not replace the cataloging produced by C.**

## 23. Future Expansion

The design deliberately leaves room for:

- additional entity types;
- additional relationship types;
- source-specific evidence;
- external reference connectors;
- audio fingerprints/signatures;
- human review;
- relationship conflict management;
- provenance propagation;
- entity merging and splitting.

None of these are prerequisites for the first implementation.

