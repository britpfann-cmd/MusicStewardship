# MusicStewardship — Library Card CSV Public Specification

**Document ID:** ING-CARD-001  
**Status:** Working Specification  
**Revision:** A  
**Date:** 2026-09-20

## 1. Purpose

This specification defines the public CSV artifact produced by the final stage of C in MusicStewardship.

The artifact is the **Library Card** for a source asset.

The Library Card is:
- the final summation of the work performed by C for that asset;
- the formal interchange boundary from C to D;
- human-readable and machine-readable;
- suitable for use by systems outside MusicStewardship;
- sufficiently complete to construct a minimal catalog entry directly from the CSV;
- capable of carrying a better catalog entry when C has additional reliable source information.

C's internal implementation, working records, processing steps, and intermediate representations are not part of this public interface.

## 2. Architectural Boundary

C produces the Library Card.

D consumes the Library Card.

D shall not depend on C's Python implementation, internal working files, Candidate Record structures, Interpretation structures, or other private implementation details.

The public boundary is:

    Source Asset
        |
        v
        C
        |
        v
    Library Card CSV
        |
        +----> Minimal Catalog
        |
        v
        D

The same Library Card may be supplied to an external person or system without requiring access to MusicStewardship internals.

## 3. Definition of a Library Card

A Library Card represents C's complete cataloging result for a source asset at a particular revision of the information available to C.

A Library Card contains:
1. the initial catalog description of the asset;
2. all native provenance information derived from the asset and its source context;
3. source-derived values needed to understand the catalog description;
4. sufficient identity and lineage information to associate the card with its source asset;
5. a revision identity permitting successor cards to be distinguished.

The Library Card does not assert the final historical or canonical identity of a recording. Such assessment belongs to D and subsequent stages.

## 4. One Card Per Source Asset

The normal unit of a Library Card is one source asset.

The source asset may be an audio asset or another source asset that C is capable of cataloging.

A card must remain traceable to its source object.

C shall not require that the source asset already be associated with a known canonical Recording or Entity.

## 5. Native Provenance

The Library Card shall contain all native provenance information derived from the asset and its source context.

Native provenance includes information that is actually present in, or directly associated with, the supplied source material and that contributes to the cataloging result.

Examples include, where present:
- source identity;
- supplied source root;
- source-relative path;
- original filename;
- extension or format;
- directory context;
- source-native identifiers;
- source-native metadata;
- source-native dates;
- source-native artist, ensemble, album, title, composer, or other descriptive values;
- source-specific values decoded from the supplied source;
- distinctions between observed source values and values mechanically derived from them.

The Library Card shall not discard native provenance merely because C cannot assign it a canonical meaning.

## 6. Source Values and Derived Values

The Library Card shall preserve the distinction between **observed source information** and **information derived by C from that source information**.

C may decode, normalize, decompose, or otherwise interpret source information when its rules permit doing so.

Such processing does not replace the original source information.

The governing principle remains:

> Preserve → Normalize → Interpret

The original source value remains recoverable in the Library Card where it contributes to the cataloging result.

## 7. Catalog Sufficiency

The Library Card shall contain enough information to construct a minimal catalog entry directly.

This does not require C to establish:
- canonical historical recording identity;
- definitive entity identity;
- equivalence between recordings;
- final authority of conflicting sources;
- external-reference agreement.

Those matters may be established later by D.

C's responsibility is to produce the best catalog description supported by the information available to C, together with its native provenance.

## 8. Public CSV Interface

CSV is the public interchange format for the Library Card.

The format shall be:
- text-based;
- human-readable;
- machine-readable;
- portable;
- independently parseable;
- documented independently of C's implementation.

The public specification defines the meaning of fields and records, not the internal software used to create them.

JSON, Markdown, Python objects, intermediate Candidate Records, and other C working artifacts are not substitutes for the Library Card CSV.

## 9. Revision and Successor Cards

Library Cards are revision-indexed.

A revision represents the cataloging result produced from a particular available set of C inputs and rules.

When the information available to C is amended, corrected, expanded, or otherwise materially changed, C may produce a successor Library Card.

The successor shall have its own revision identity and shall remain traceable to the preceding card.

The prior card shall not be silently overwritten.

This permits successive refinement of catalog information while preserving the history of the cataloging result.

## 10. Recursive Refinement

Library Cards are designed to support successive and recursive refinement.

An improved body of information may be supplied to C, producing a successor Library Card.

Such improved information may arise from:
- amended source information;
- additional native source information;
- improved source interpretation;
- information supplied through subsequent processing;
- progressive improvement of related entity records;
- other established references that become available as legitimate inputs to a later C process.

Each C run remains responsible for producing a self-contained Library Card representing its result at that revision.

## 11. Relationship to D

D assesses the Library Card's cataloging assertions and their relationships to the growing MusicStewardship knowledge base.

D may use:
- previously cataloged assets;
- established entities;
- entity candidates;
- established relationships;
- source and collection provenance;
- provider/source accuracy assertions;
- external reference information.

D does not silently rewrite the Library Card.

Where D's work results in improved information that is legitimately available as input to a subsequent C process, C may produce a successor Library Card.

Thus:

> C produces catalog cards.  
> D progressively assesses and relates them.  
> Improved knowledge may provide improved inputs for a successor C result.

## 12. External Interchange

The Library Card is intentionally suitable for communication outside MusicStewardship.

An external party shall be able to inspect the CSV and understand:
- what asset is being described;
- what source it came from;
- what native provenance accompanies it;
- what catalog information C extracted or derived;
- what revision of the card is being represented.

External systems do not need to reproduce MusicStewardship's internal architecture in order to consume the artifact.

## 13. Integrity and Reproducibility

For the same source inputs, applicable C rules, and defined processing environment, C should produce the same Library Card content.

A Library Card should therefore be suitable for deterministic comparison with a successor or repeated production of the same revision.

The revision identity must not be used to conceal material changes in the underlying catalog information.

## 14. Field Specification

Revision A defines the public Library Card field set used by the tested C-to-D exchange.

The definitive Rev A field definition is maintained in:

`99_sandbox\MusicStewardship_Library_Card_Field_Definitions_RevA.csv`

That artifact defines, for every public field:

- field name;
- cardinality;
- value form;
- meaning;
- required/optional status;
- native/derived status.

The Rev A public CSV contains **33 fields**.

Fields with cardinality `0..n` or `1..n` are represented in the CSV as compact JSON arrays. This permits CSV to remain the public interchange format while preserving multi-valued information.

In particular:

- `source_grouping_label` is an ordered multi-valued source label field;
- `source_context` is an ordered multi-valued source-context field;
- `evidence_summary` is a compact multi-valued evidence representation;
- `residual_evidence` preserves uninterpreted evidence references;
- `conflicts` preserves C-detected construction conflicts;
- `c_lineage` carries the compact C provenance chain.

The revision fields have distinct meanings:

- `card_revision` identifies the Library Card revision;
- `library_card_interface_revision` identifies the public C-to-D exchange contract;
- `c_processing_revision` identifies the C processing revision that produced the card;
- `source_record_revision` identifies the C Source Record schema revision.

These revisions shall not be conflated.

The Rev A field-definition artifact and the C-to-Library Card translation map together define the tested public field contract. Internal C structures remain implementation details.

No field shall be added merely because it is convenient for an internal implementation.
## 15. Non-Goals

The Library Card does not:
- perform entity resolution;
- establish canonical recording identity;
- merge recordings;
- rank evidence universally;
- silently resolve conflicting source assertions;
- replace native source values with canonical values;
- require external web or database access;
- expose C's internal implementation.

## 16. Governing Principle

The Library Card is the point at which C's work becomes a portable, inspectable cataloging product.

> **C produces the Library Card. The Library Card is the public boundary. D consumes the Library Card.**

The card is sufficiently complete to build a catalog directly, while preserving the native provenance necessary for later assessment, refinement, and reprocessing.




## Addendum — 2026-09-24 Internal Entity Indexing Boundary

The Rev A Library Card remains the common source-to-catalog exchange artifact and does not expose internal entity identity as a user-facing naming system.

After canonical Library Card construction, the catalog may maintain an internal entity index keyed by opaque entity IDs. These IDs are for relationships and indexing only. They are not intended for display to users.

Entity/name association is therefore downstream of source translation. Source names remain on the Library Card; internal entity references may be attached to the managed catalog/index representation.

User-facing preferred and short names are presentation-layer properties and are not replacements for source names.
