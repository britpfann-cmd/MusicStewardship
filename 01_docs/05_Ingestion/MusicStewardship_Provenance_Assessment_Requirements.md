# MusicStewardship — Provenance Assessment & Entity Association Requirements

**Document ID:** ING-PROV-001  
**Status:** Working requirements  
**Revision:** A  
**Date:** 2026-09-20

## 1. Purpose

This document defines the requirements for the MusicStewardship **Provenance Assessment and Entity Association** stage, referred to as **D**.

D operates after the cataloging and interpretation work of C.

Its purpose is to progressively establish and assess relationships between cataloged source assets and musical entities, using the evidence available within the MusicStewardship library and, where appropriate, external reference sources.

D does not replace or rewrite the cataloging established by C.

## 2. Architectural Boundary

### C — Cataloging

C shall produce a standardized cataloging description, or **catalog card**, for each source asset.

The catalog card shall contain:

- the minimum information necessary to uniquely catalog and retrieve the asset;
- additional cataloging information whenever available;
- source provenance and evidence necessary to understand where the cataloging information came from.

The minimum is a floor, not a target. More cataloging information shall be retained whenever available.

C describes the asset.

### D — Provenance Assessment and Entity Association

D shall cross-reference the C catalog card against:

- previously cataloged assets;
- entity candidates;
- established library entities;
- relationships already established within the library;
- source and collection assertions;
- available external reference sources;
- audio or other technical evidence when available.

D assesses the quality of the resulting relationships.

D establishes authority for the cataloging assertions progressively rather than requiring complete identification at the time of initial cataloging.

## 3. Fundamental Requirement

**REQ-D-001 — Progressive relationship assessment**

D shall progressively establish and assess relationships between cataloged assets and musical entities as additional evidence becomes available.

An assessment shall be capable of becoming stronger, weaker, more specific, or otherwise revised as new evidence enters the system.

The original cataloging and source evidence shall remain preserved.

## 4. Dynamic Knowledge Network

**REQ-D-002 — Dynamic relationship network**

D shall maintain a dynamic, evidence-bearing network of relationships among:

- cataloged assets;
- entity candidates;
- established entities;
- other cataloged assets;
- source collections;
- external reference records.

The network shall permit relationships to be reused as evidence when assessing subsequent assets.

## 5. Asset Independence

**REQ-D-003 — Asset remains independently cataloged**

Every source asset shall retain its own C catalog card regardless of the quality or completeness of its D-level entity associations.

An asset shall not become un-cataloged merely because its relationship to a known musical entity has not yet been established.

## 6. Entity Candidates

**REQ-D-004 — Progressive entity library**

The system shall support the progressive construction of a library of entities from entity candidates.

Entity candidates may arise from:

- cataloged assets;
- source organization;
- source metadata;
- repeated cataloging assertions;
- relationships among assets;
- external reference information.

An entity candidate shall not be represented as an established entity merely because it has been proposed.

## 7. Established Entities

**REQ-D-005 — Established entities as evidence**

An established entity and its established relationships shall be available as evidence when assessing subsequently cataloged assets.

This shall allow the library's accumulated knowledge to improve the assessment of incoming assets.

## 8. Relationship Assertions

**REQ-D-006 — Evidence-bearing assertions**

A relationship between an asset and an entity shall be represented as an assertion rather than as an unexplained assignment.

A relationship assertion shall preserve, at minimum:

- the participating objects;
- the nature of the relationship;
- the evidence supporting the relationship;
- the source of the evidence;
- the current assessment of the relationship.

The implementation shall permit multiple supporting evidence items.

## 9. Evidence Preservation

**REQ-D-007 — Preserve evidence lineage**

Every D assessment shall remain traceable to the evidence on which it is based.

Evidence shall not be discarded merely because a later assessment supersedes, strengthens, weakens, or contradicts an earlier assessment.

## 10. Evidence Sources

**REQ-D-008 — Multiple evidence channels**

D shall be capable of using multiple evidence channels, including, where available:

- names;
- titles;
- ensemble/orchestra information;
- singers;
- dates;
- genre;
- style;
- catalog identifiers;
- source-specific identifiers;
- source collection context;
- relationships to previously cataloged assets;
- established entity relationships;
- audio signatures;
- other technical evidence;
- external reference sources;
- human/source-provider assertions.

The architecture shall not require all evidence channels to be available for every asset.

## 11. Source-Provider Accuracy Assessment

**REQ-D-009 — Preserve supplied accuracy assessment**

An incoming asset group or collection may include an assessment of the accuracy or reliability of its supplied cataloging.

That assessment shall be retained as provenance information.

It shall not automatically become an unquestioned MusicStewardship conclusion.

## 12. External References

**REQ-D-010 — External reference evidence**

D shall be capable of incorporating information from external reference sources when such sources are available and appropriate.

Potential external sources may include:

- Discogs;
- tango-dj.at;
- restorer catalogs;
- published discographies;
- catalogs supplied separately from music collections;
- other documented reference sources.

External assertions shall remain distinguishable from source-derived assertions.

## 13. In-House Knowledge Before External Complexity

**REQ-D-011 — Use established in-house knowledge**

D shall be capable of using previously established MusicStewardship assets and entities as reference evidence before requiring more complex external research.

Established in-house relationships should provide reusable evidence for subsequent assessments.

## 14. Low-Hanging-Fruit Principle

**REQ-D-012 — Progressive implementation**

The implementation shall initially address relationships that can be established using readily available, high-value evidence.

The system shall not require sophisticated matching, external research, or audio analysis before simple relationships can be established.

Implementation shall proceed incrementally as actual source material demonstrates the need for additional methods.

## 15. Evidence Attribution

**REQ-D-013 — Evidence remains attributable**

D shall preserve the type, origin, and context of evidence.

The architecture shall not require a universal ranking of all evidence sources before implementation begins.

## 16. Conflicting Evidence

**REQ-D-014 — Preserve conflicting assertions**

When credible evidence supports different relationships or values, D shall preserve the competing assertions and their supporting evidence.

D shall not silently discard conflicting evidence merely to produce a single answer.

Resolution of conflicts shall be an explicit operation.

## 17. Progressive Reassessment

**REQ-D-015 — Reassessment**

A previously assessed relationship shall be capable of reassessment when:

- a new asset is cataloged;
- a new entity is established;
- an existing entity gains additional evidence;
- an external reference becomes available;
- an audio signature becomes available;
- source information is corrected or supplemented;
- conflicting evidence is discovered.

Reassessment shall preserve the history and evidence underlying previous assessments.

## 18. Relationships Between Assets

**REQ-D-016 — Asset-to-asset relationships**

D shall support relationships directly between cataloged assets.

Examples include:

- possible same recording;
- established same recording;
- alternate source representation;
- related source representation;
- corroborating asset;
- source/reference counterpart.

The initial relationship vocabulary shall remain limited and shall be expanded only when demonstrated by requirements.

## 19. Recording Versus AudioAsset

**REQ-D-017 — Preserve the distinction**

D shall preserve the distinction between:

- an individual AudioAsset; and
- the musical Recording or other entity that the asset may represent.

Multiple AudioAssets may ultimately be associated with one Recording.

An association shall not require treating each AudioAsset as a separate musical recording.

## 20. Cataloging Is Not Identity Resolution

**REQ-D-018 — C/D separation**

D shall not require C to establish the historical or canonical identity of the musical recording represented by an asset.

C shall provide a usable catalog card.

D shall assess the relationship between that cataloged asset and entities represented in the growing MusicStewardship knowledge network.

## 21. Authority Is Progressive

**REQ-D-019 — Authority attaches to assertions and relationships**

D shall progressively establish the quality of individual cataloging assertions and relationships.

Authority shall not be represented solely as a single undifferentiated quality value for an entire asset.

Where practical, different assertions concerning the same asset shall be capable of having different evidentiary support.

## 22. No Destructive Correction

**REQ-D-020 — Preserve original cataloging**

A D assessment shall not overwrite or destroy the C catalog card or the underlying source evidence.

If D establishes that a C assertion is questionable or requires reinterpretation, the original assertion shall remain recoverable and the D assessment shall record the additional evidence and resulting relationship assessment.

## 23. Growth of Library Knowledge

**REQ-D-021 — Knowledge compounds**

The system shall support the principle that each sufficiently established asset/entity relationship can become evidence for the assessment of later assets.

The progressive workflow is:

```text
Catalog asset
      ↓
Generate entity candidates
      ↓
Assess relationships
      ↓
Establish entities / relationships
      ↓
Use established knowledge on later assets
      ↓
Strengthen and expand the network
```

## 24. Implementation Boundary

The first implementation shall demonstrate the architecture using readily available evidence.

The initial implementation should favor:

1. existing C catalog cards;
2. existing cataloged assets;
3. obvious textual correspondence;
4. explicit identifiers;
5. established source/context relationships.

More sophisticated techniques such as fuzzy matching, audio signatures, and extensive external reference research shall be added only after the simpler methods have been demonstrated and their limitations are understood.

## 25. Governing Principles

> **Catalog first; assess relationships progressively.**

> **The minimum cataloging information is the floor, not the target.**

> **Every relationship carries its evidence.**

> **Established knowledge becomes evidence for future assessment.**

> **Preserve source assertions, external assertions, and MusicStewardship assessments as distinguishable information.**

> **Take the low-hanging fruit first.**

> **Do not add sophisticated resolution machinery until actual evidence demonstrates that it is needed.**

> **Never discard the evidence merely because our interpretation improves.**
