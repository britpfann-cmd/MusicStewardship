# MusicStewardship C → D Interface Specification — Rev B

**Status:** Production-interface baseline candidate  
**Date:** 2026-10-06  
**Supersedes:** Rev A as the intended production contract; Rev A remains prototype history.

## 1. Purpose

This specification defines the interface by which C processing hands accepted source material to D/catalog processing.

The interface is deliberately divided into **two sections**, not two catalog information levels. Catalog Information Levels 0–4 remain a separate architecture.

> **C preserves and describes what the source supplied. D determines compatibility, grouping, reconciliation, and catalog interpretation.**

The interface must permit immediate acceptance of sparse material, useful early catalog operation, and later enrichment without re-ingestion or loss.

## 2. Governing principles

1. **Accept first; enrich progressively.** Research or entity identification is not a prerequisite for admission.
2. **Lose nothing.** Original source evidence, residual material, provenance, and prior interpretations remain preserved.
3. **Source differences are data until proven otherwise.** Source-specific interpretation belongs in Rosetta/control data wherever generic processing capabilities can express it.
4. **Semantic observations are observations, not authority claims.** They may be revised or superseded later.
5. **Absence of semantic information never prevents acceptance.**
6. **Do not make D reconstruct semantic information that C already knew.**
7. **Do not force new C semantics into a new interface revision.** The semantic-observation section is extensible.

## 3. Section 1 — CORE acceptance and provenance

CORE is the minimum contract required to create and retrieve a discrete CatalogedInstance and to reach its preserved evidence.

Rev B makes the following source identity values explicit first-class fields:

- `source_id` — identity of the submitted source population or source type.
- `source_record` — identity/locator of the record within that source population.
- `source_object_id` — durable C identity for the accepted source object.
- `source_object_key` — preserved source-object key where supplied/constructed by C; D must not parse this composite to recover `source_id` or `source_record`.
- `source_record_revision` — source-record revision/version when available.
- C processing/interface revision and lineage sufficient to identify how the submission was processed.
- source asset locator/provenance sufficient to reach the preserved Library Card/source evidence when applicable.

CORE answers:

> **What discrete thing did we accept, where did it come from, and how can its preserved evidence be reached?**

The admission threshold is intentionally low. CORE does **not** require title, artist, date, genre, recording identity, performance identity, work identity, or successful research. A sparse or poorly described music file must still be capable of becoming a discrete, persistent, retrievable CatalogedInstance.

## 4. Section 2 — SEMANTIC OBSERVATIONS

C may supply zero or more semantic observations describing information learned from the source by observation, decoding, standardization, decomposition, or other Rosetta processing.

Common examples include, but are not limited to:

- title and alternate-title representations;
- ensemble/orchestra representations;
- contributor expressions;
- decoded author, composer, singer, conductor, arranger, performer, leader, producer, or other role-bearing expressions;
- recording date or period observations;
- genre/rhythm/style observations;
- source identifiers;
- album/grouping/sequence information;
- filename-derived representations;
- future Rosetta semantic outputs not known when Rev B is issued.

Each semantic observation retains, where applicable:

- semantic term;
- source value;
- decoded/interpreted value;
- source element and source field;
- target semantic context;
- relationship or role context;
- representation level/classification;
- assurance/status;
- evidence basis;
- Rosetta rule/decoder provenance.

The structured semantic-observation collection is the extensibility mechanism. New semantic terms do not require adding a new fixed interface column or issuing a new interface revision merely because C learned something new.

Frequently used values may additionally be projected into convenience fields for efficient Level-1 catalog use. Such projections do not replace the structured observation or its provenance.

## 5. Relationship to catalog Information Levels 0–4

The C → D interface sections are not catalog information levels.

- CORE supplies the information needed to establish **Level 0 — acceptance, identity, and provenance**.
- Useful semantic observations may seed **Level 1 — current operational catalog state** and/or materialize as **Level 2 — structured evidence and corroboration**.
- The immutable Library Card/source evidence remains the preservation home for **Level 3 — preserved source and residual evidence**.
- Later changes to current catalog interpretation are recorded in **Level 4 — catalog revision history**.

Preservation depth and retrieval depth remain independent. Ordinary catalog or DJ queries need not retrieve Level-3 source material merely because it remains durably associated.

## 6. Division of responsibility

### C owns

- faithful preservation of submitted material;
- source provenance and source identity;
- source-specific syntax interpretation through Rosetta/control rules;
- generic decoding/standardization operations;
- structured semantic observations with processing provenance;
- residual/uninterpreted evidence preservation.

### D owns

- representation classification for catalog purposes;
- comparison and compatibility assessment;
- likely-same grouping;
- current operational catalog state;
- reconciliation and identity conclusions;
- creation/association of historical entities where later warranted;
- revision history of catalog conclusions.

A D operation may legitimately classify a valid C contributor expression such as `VARIOUS` as **not name-like** without altering or discarding the C observation.

## 7. Rev-A findings incorporated into Rev B

Population-driven D2/D3 prototyping exposed one clear Rev-A interface defect: C already knows `source_id` and `source_record`, while Rev A requires D to infer source identity from `source_object_key` or other context. Rev B therefore exposes both explicitly in CORE.

The same prototyping found that title representations, filename-derived alternate titles, source identifiers, contributor-role expressions, and Rosetta evidence already cross the interface sufficiently for D-side compatibility/grouping work. They remain semantic observations rather than CORE admission requirements.

## 8. Production-readiness criterion

Rev B is considered adequate when downstream processing no longer routinely has to reconstruct semantic information that C already knew, while still allowing new semantic observations to cross the interface without schema churn.

The practical baseline target is sufficient descriptive quality for DJ use and approximately Tango Time Travel-class catalog usefulness, while preserving evidence and provenance needed for later research and deeper reconciliation.
