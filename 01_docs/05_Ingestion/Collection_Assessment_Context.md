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

