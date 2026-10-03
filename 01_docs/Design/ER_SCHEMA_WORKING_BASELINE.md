# MusicStewardship — Working E-R Schema Baseline

**Date:** 2026-10-02  
**Version:** E-R v0.1 working baseline  
**Status:** Working / provisional  
**Purpose:** Define the initial entity-relationship model to be represented in the first SQLite implementation and exercised against curated source populations.

## 1. Modeling stance

This is an E-R design instrument, not a final ontology.

Entity boundaries are expected to mature as complete source populations are ingested and reconciled. Entities may be introduced, merged, split, or renamed when evidence and required queries justify the change.

The model must permit incomplete and provisional knowledge. A source observation does not need to be fully identified before it can enter the catalog.

The governing preservation rule is:

> **Lose nothing.**

Source observations, undecoded/residual material, provenance, earlier interpretations, and corrective history remain recoverable even as the current catalog understanding improves.

## 2. Three distinct layers at catalog entry

### Library Card / source submission

The Library Card is the preserved submission/evidence package received from ingestion. It records what came to MusicStewardship and should remain traceable in its submitted form.

It is evidence, not the mutable catalog conclusion.

### CatalogedInstance

A CatalogedInstance is the persistent catalog object created for an ingested instance. It is the base from which discovery/reconciliation builds knowledge upward.

**Candidate key:** `cataloged_instance_id`

A CatalogedInstance has:

- persistent identity;
- an immediately accessible **current state** for normal catalog use;
- a durable relationship to its originating Library Card/source evidence;
- provisional or resolved associations to higher-level catalog entities; and
- revision history sufficient for maintenance, diagnosis, corrective action, and audit.

Ordinary queries should use current state. Revision history must not burden routine catalog use.

### Library Item

A Library Item is a particular owned digital file or library artifact.

**Candidate key:** `library_item_id`

Library Item describes what the project possesses. CatalogedInstance describes the evolving catalog knowledge associated with an ingested instance. The two concepts are related but are not synonymous.

Exact cardinality between Library Card, CatalogedInstance, and Library Item remains subject to population validation.

## 3. Core historical/musical spine

The initial conceptual spine is:

```text
WORK
  |
  | realized as
  v
PERFORMANCE
  |
  | represented by
  v
RECORDING
  |
  | associated with / represented in
  v
CATALOGED INSTANCE
```

The direction shown is ontological/historical. Discovery normally proceeds in the opposite direction: from CatalogedInstance upward toward Recording, Performance, and Work.

Cardinalities are provisional until exercised against real populations, especially for edited, composite, derivative, or otherwise exceptional recordings.

### Work

The underlying musical creation/composition that may be realized by one or more Performances.

**Candidate key:** `work_id`

Title or name is not identity. One Work may have multiple observed titles/names, and distinct Works may share a title.

### Performance

A unique historical realization of a Work by particular performer(s), occurring at a particular time/event or recording session, whether or not all of those facts are currently known.

**Candidate key:** `performance_id`

The current TTT `recordings.csv` remains a provisional source representation and must not be treated as final Performance identity resolution.

### Recording

A recorded representation derived from a particular Performance, distinguishable from other recorded representations of that Performance when evidence justifies the distinction.

**Candidate key:** `recording_id`

This replaces the earlier single provisional `Recording Manifestation` concept as the working entity name for E-R v0.1. Transfer, restoration, remaster, edit, master, reissue, digitization, and related distinctions are not forced into the Recording identity definition until population evidence establishes useful boundaries.

Multiple CatalogedInstances may eventually coalesce on one Recording. Multiple Recordings may represent one Performance.

## 4. Publication, possession, people, and context entities

The following entities remain justified, but they surround the historical/musical spine rather than forming its ontological parent chain.

### Acquisition

An acquisition event/process. **Candidate key:** `acquisition_id`.

### Collection

A coherent group of material within an acquisition/source context. **Candidate key:** `collection_id`.

### Release

A publication/release/album-level representation. **Candidate key:** `release_id`.

### Release Track

A particular track occurrence on a Release. **Candidate key:** `release_track_id`.

Natural identifying context may include `release + track_number`, subject to source validation.

Release and Release Track describe publication context. They do not define Work, Performance, or Recording identity.

### Person

A human participant such as composer, lyricist, singer, conductor, arranger, or instrumentalist when evidence supports person-level identity. **Candidate key:** `person_id`.

### Ensemble

A named performing ensemble/orchestra. **Candidate key:** `ensemble_id`.

### Location

A place or locator at which a Library Item can be found. **Candidate key:** `location_id` or another stable locator identity.

### Source

A source system, publisher, catalog, collection, document, or other evidence origin. **Candidate key:** `source_id`.

### Source Assertion / Evidence Observation

A source-attributed statement or observation about an entity, instance, representation, relationship, or attribute. **Candidate key:** generated evidence/assertion key; exact physical design TBD.

## 5. Provisional identity and coalescence

Catalog construction begins before complete identity resolution.

A newly ingested CatalogedInstance may produce provisional suggestions upward:

```text
CatalogedInstance
      |
      +--> ? Recording
               |
               +--> ? Performance
                          |
                          +--> ? Work
```

As more instances and evidence accumulate, candidates may begin to coalesce. Coalescence may occur independently at different levels: two instances may be recognized as the same Work before their Performance identity is known, or as the same Performance while Recording representation remains uncertain.

D (discovery/reconciliation) therefore performs progressive entity resolution rather than merely filling foreign keys:

```text
create provisional candidates
        -> accumulate evidence
        -> discover commonality
        -> coalesce when justified
        -> retain history/evidence
```

Later evidence must also permit separation of an earlier merge. Coalescence is a change in current interpretation, not destruction of prior evidence.

## 6. Current state and revision history

The operational catalog is optimized for:

> **What do we currently believe?**

CatalogedInstance and other evolving catalog knowledge should expose an immediately accessible current state.

Revision history is a maintenance/audit facility analogous in purpose to source-control history. It should support diagnosis, rollback/correction, and understanding how present state was reached without requiring ordinary queries to traverse history.

The E-R requirement is behavioral, not a commitment to a storage technology. Revision history may later be implemented with snapshots, deltas, an append-only journal, database temporal mechanisms, exported records under source control, or a combination.

Two histories must remain distinguishable:

- **evidence history** — what came to us and from where;
- **catalog revision history** — what MusicStewardship interpreted or changed over time.

Neither overwrites the other.

## 7. Evidence and provenance

The evidence layer surrounds all catalog layers rather than substituting for them.

```text
SOURCE
   |
   v
SOURCE ASSERTION / OBSERVATION
   |
   +--> CatalogedInstance
   +--> Recording
   +--> Performance
   +--> Work
   +--> Release / ReleaseTrack
   +--> Person / Ensemble
   +--> relationships and attributes
```

A source assertion should be able to express, in effect:

> Source S supplied or claims value X about object/relationship O.

Promotion into normalized catalog knowledge does not erase the original source value.

Conflicting evidence is retained. Current interpretation may select or synthesize the best-supported present knowledge while alternatives remain traceable.

## 8. Seed entities and external references

Canonical entities may originate either:

- provisionally from ingested CatalogedInstances; or
- as externally supported **seed entities** created to reduce reconciliation work.

`SeedEntity` is not a separate entity type. Seeded status/origin is provenance of an ordinary Work, Performance, Recording, Person, Release, or other entity.

Origin does not determine authority. A seeded entity remains subject to confirmation, enrichment, merge, split, correction, and revision.

External systems such as Discogs, TANGO-DJ.AT, Tango Time Travel, Crackling Tunes, and other researched references contribute evidence and candidate structure; they do not become MusicStewardship's canonical identities merely because they are convenient or accessible.

## 9. Demand-driven seed harvest

D may use the ingested population to guide economical external research.

A practical sequence is:

```text
CatalogedInstances
      -> provisional candidates
      -> cheap exact/similar population scan
      -> candidate counts/clusters
      -> targeted automated seed harvest
      -> reconciliation/coalescence
      -> smaller difficult residual population
      -> specialized/manual research
```

Discogs is particularly useful for automated first-pass seed acquisition where its interface permits efficient queries. Ease of access is not evidentiary authority. More specialized tango references may provide stronger evidence for particular questions and can be consulted after inexpensive evidence has reduced the unresolved population.

## 10. Whole-population ingestion as model validation

The researched source populations should be ingested broadly rather than limiting development to hand-selected successful examples.

Whole-population ingestion tests whether the provisional E-R model can faithfully represent what the sources actually contain.

Results should distinguish at least:

- represented successfully;
- represented with residual/uninterpreted information;
- failed or forced mappings requiring decoder/grammar remediation;
- recurring structures suggesting E-R remediation.

Failure is diagnostic information, not permission to discard source material.

This produces a separate **model-confidence** dimension from entity/relationship confidence. A mature E-R model must be capable of faithfully representing uncertain identity.

## 11. Initial implementation cycle

E-R v0.1 will be exercised in this order:

1. define and document the provisional E-R model;
2. create a SQLite database structure representing it;
3. create one general loader path using existing source grammars/decoders;
4. exercise the loader with samples from multiple curated collections;
5. run structural validation queries for coverage, residuals, failures, and cardinality surprises;
6. create candidate-set queries reporting exact and similar/common values and combinations;
7. inspect results and remediate the E-R model, grammar, decoder, or loader where indicated;
8. expand toward whole-population ingestion;
9. use resulting candidate populations to drive targeted seed harvesting and later reconciliation.

Automatic coalescence is deliberately **not** required in the first implementation cycle. Candidate reporting comes first so that reconciliation rules are informed by actual populations.

## 12. Candidate-set reporting

Initial queries should report candidate populations without asserting identity. Useful dimensions may include:

- literal title equality;
- comparison-normalized title similarity;
- title + ensemble/orchestra;
- title + ensemble + singer;
- title + approximate date;
- matrix, record, take, catalog number, or other source identifiers;
- combinations suggested by populated source evidence.

Literal observations and comparison forms must remain distinguishable. Comparison normalization must not silently replace source values.

Counts are themselves useful intelligence: repeated constellations across sources identify high-value reconciliation and seed-harvest opportunities.

## 13. Current source-to-E-R mapping

Existing TTT prototype structures remain useful input evidence but are not treated as final ontology:

| Prototype table | E-R v0.1 interpretation |
| --- | --- |
| `acquisitions.csv` | Acquisition |
| `collections.csv` | Collection |
| `releases.csv` | Release |
| `release_tracks.csv` | Release Track |
| `recordings.csv` | provisional evidence toward Recording / Performance; not final identity |
| `library_items.csv` | Library Item |
| `locations.csv` | Location |
| `library_item_tracks.csv` | Library Item ↔ Release Track relationship |
| `release_track_recordings.csv` | source/prototype relationship requiring translation into v0.1 identity layers |
| `library_item_evidence.csv` | source evidence |
| `book_metadata.csv` | derived projection |
| `recording_metadata.csv` | source-attributed secondary metadata |

## 14. Modeling restraint

Do not force every source field into an entity table merely because it exists.

Use the sequence:

```text
source representation
      -> retain as evidence
      -> understand scope
      -> promote when justified
      -> normalize only when useful
```

Likewise, do not introduce a new entity merely to accommodate one source's vocabulary until the distinction proves useful across evidence or required queries.

## 15. Validation targets

The model must be tested against cases including:

1. the same Work with multiple Performances;
2. one Performance appearing on multiple Releases/labels;
3. multiple Recordings/representations of one Performance;
4. multiple CatalogedInstances converging on a shared Recording, Performance, or Work;
5. provisional candidates that later merge or split;
6. release histories, reissues, and subsequent editions;
7. person versus ensemble representations;
8. source documents that describe collections or multiple musical objects;
9. TANGO-DJ and Discogs external identifiers and release taxonomy;
10. Crackling Tunes and other curated/commercial source paths;
11. residual/uninterpreted source information;
12. whole-population ingest failures and recurring exceptions.

**Status:** Ready to drive the first provisional SQLite/loader implementation cycle. It remains a working model subject to population-driven refinement.
