(.venv) PS C:\Projects\MusicStewardship> Get-Content .\01_docs\05_Ingestion\MusicStewardship_Provenance_Assessment_Design.md
# MusicStewardship — Provenance Assessment & Entity Association Design

**Document ID:** ING-PROV-002  
**Status:** Initial design  
**Revision:** B  
**Date:** 2026-09-20

## 1. Purpose

This document defines the first implementable design for D: Provenance Assessment and Entity Association.

The design deliberately implements only the lowest-hanging-fruit relationship methods first.

D operates on catalog cards produced by C and progressively builds an evidence-bearing network of relationships among cataloged assets, entity candidates,established entities, and external references.

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

## 14. Library Card Exchange Standard

C shall define and publish a versioned Library Card CSV exchange standard for each interface revision.

A Library Card data exchange consists of:

1. a revision-coded data artifact containing the Library Card CSV data; and
2. the corresponding revision-coded exchange standard defining how that data is encoded and interpreted.

The standard and data artifact shall be explicitly paired by revision.

The physical packaging of the pair is implementation-dependent. A workbook containing both the standard and the Library Card data is a suitable reference exchange package and is readily portable to external users. Equivalent separate-file or other rudimentary packaging is permitted provided that the pairing is unambiguous.

C shall:

- define the exchange standard;
- publish the standard for each interface revision;
- produce/export Library Card data conforming to that revision; and
- identify the applicable interface revision with the exchanged data.

D shall:

- receive the revision-coded data artifact together with its corresponding standard;
- import the data in accordance with that published revision;
- not infer the exchange format from C's internal processing structures; and
- preserve the applicable interface revision as part of its import provenance.

The interface revision describes the public exchange contract. It is distinct from the C processing revision and from any D processing revision.

The exchange shall carry three distinct revision identities where applicable:

```text
C processing revision
        ↓
Library Card interface revision
        ↓
D processing revision
```

These revisions describe different things:

- **C processing revision** identifies the C processing implementation/schema revision that produced the exchanged card information.
- **Library Card interface revision** identifies the public exchange contract used to encode and interpret the Library Card data.
- **D processing revision** identifies the D processing implementation that imported and assessed the exchange. It is assigned by D and is not supplied by C as part of the Library Card contract.

The Library Card exchange must explicitly identify the C processing revision and the Library Card interface revision. D shall record its own processing revision when the exchange is imported. No one of these revision identities shall be used as a substitute for another.

For the initial implementation, the exact field names and placement of these revision identities are part of the Rev A Library Card exchange test. They shall not be treated as finally baselined until the end-to-end C export → D import → D verification test has succeeded.

Each interface revision shall have an end-to-end verification test demonstrating:

```text
C processing
    ↓
C export
    ↓
revision-coded Library Card data
    +
corresponding revision-coded standard
    ↓
D import
    ↓
D verification
```

The test shall verify that the exported data conforms to the published standard and that D imports the information represented by that standard without unintended loss or reinterpretation.

The same approach shall be used for subsequent interface revisions. A new interface revision is a new published exchange contract; prior revisions remain identifiable for the data exchanged under them.

## 15. External References

External reference information shall be represented as a separate evidence source.

The first implementation does not need to query external services automatically.

It must, however, leave room for external evidence to be attached later without changing the core relationship model.

## 16. Source Accuracy Assertions

An incoming collection may carry an assessment supplied by its provider concerning cataloging accuracy.

That assessment should be represented as source/collection evidence.

It shall not be silently converted into an established entity relationship.

## 17. Progressive Reassessment

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

## Collection Assessment Context

D processing may operate on a related collection of Library Cards rather than treating each Library Card as an independent assessment subject.

A Collection Assessment Context provides D with information about the collection-level provenance and processing conditions applicable to the supplied group of Library Cards.

The Collection Assessment Context is a D-side processing input. It is not part of the C processing result and is not embedded in the Library Card.

### Collection-Level Provenance

A collection may have a documented provenance assessment that applies to some or all of the Library Cards within that collection.

The provenance assessment shall be represented separately from the individual Library Cards.

At minimum, a collection-level provenance assertion should be capable of identifying:

    collection_id
    provenance_assertion_id
    provenance_level
    provenance_basis
    provenance_scope
    asserted_by
    assertion_reference

The exact field structure and provenance vocabulary may be refined as actual collections demonstrate requirements.

The provenance level is an assertion about the collection and its documented provenance. It is not an intrinsic property of an individual Library Card or AudioAsset.

### Provenance Scope

A collection-level provenance assertion shall identify the scope to which the assertion applies.

A collection may have strong provenance concerning source identity, source organization, source cataloging conventions, source-specific interpretation rules, or catalog metadata without thereby establishing the authenticity or historical identity of every individual audio asset.

D shall not extend a collection-level provenance assertion beyond its stated scope.

### Collection Processing Policy

Collection provenance may affect how D assesses the Library Cards in the collection.

A provenance assessment may therefore be associated with a D processing policy specifying which assessment work may be reduced, bypassed, or satisfied by the collection-level evidence.

The provenance assertion and the processing policy are distinct concepts:

> Provenance establishes why the collection is considered authoritative for a defined scope. Processing policy establishes what D is consequently permitted to do differently.

A high-provenance collection may therefore enter an express processing path without requiring C to perform different processing.

The express path shall not alter the Library Cards, alter C processing, discard provenance evidence, bypass required source-integrity checks, establish facts outside the provenance scope, or prevent later reassessment.

### Collection Membership

Library Cards processed under a Collection Assessment Context shall retain their individual source identity and provenance.

The collection context provides additional assessment evidence; it does not replace the individual card's source provenance.

A relationship established using collection-level provenance shall remain traceable to:

    Library Card
         |
         v
    Collection membership
         |
         v
    Collection provenance assertion
         |
         v
    Processing policy
         |
         v
    Relationship assessment

### Idempotent Collection Provenance

Collection-level provenance assertions shall be idempotent.

Repeated D processing of the same collection with the same provenance assertion shall recognize the existing collection-level assertion rather than create a duplicate assertion.

The same collection-level provenance assertion may therefore apply to any number of Library Cards within its defined scope.

If the provenance assessment changes materially, D shall create a new provenance assertion or revision rather than silently replacing the previous assertion.

This permits a collection's provenance history to remain visible while allowing its current assessment to improve or change.

### Architectural Boundary

Collection Assessment Context belongs to D.

It shall not be added to the Library Card merely to communicate D-side provenance judgments back into C.

The boundary remains:

    C
     |
     v
    Library Card
     |
     v
    D
     +-- Collection Assessment Context
     +-- Existing Assets
     +-- Existing Entities
     +-- Entity Candidates
     +-- Existing Relationships
     +-- External References

Thus:

> C produces Library Cards independently of provenance level. D assesses related Library Cards in the context of the provenance and knowledge available to the collection at the time of D processing.



## 18. Low-Hanging-Fruit Implementation Order

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

## 19. Determinism

For identical inputs and identical existing knowledge, the first matching implementation shall produce identical relationship candidates and evidence.

Processing order shall be deterministic.

Stable identifiers shall be used for assets, entities, candidates, assertions, and evidence records.

## 20. Idempotence

Repeated processing of an unchanged catalog population shall not create duplicate relationship assertions merely because the same evidence was encounteredagain.

The system shall recognize previously established assertion/evidence identity.

## 21. Preservation

D shall never:

- modify source assets;
- rewrite C catalog cards merely to obtain a match;
- discard source assertions;
- discard unsuccessful matches;
- silently replace one entity with another;
- collapse conflicting external references into one assertion.

## 22. First Test Target

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

## 23. Architectural Rule

> **D adds knowledge about relationships; it does not replace the cataloging produced by C.**

## 24. Future Expansion

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

(.venv) PS C:\Projects\MusicStewardship>


