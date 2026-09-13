# MusicStewardship — Working E-R Schema Baseline

**Date:** 2026-09-13  
**Status:** Working / provisional  
**Purpose:** Provide an initial entity-relationship model derived from the design rules and TTT prototype.

## 1. Modeling stance

This is an E-R design instrument, not a final ontology.

The vocabulary of entities is expected to emerge gradually from source representations and required queries. Entity boundaries may be introduced, merged, split, or renamed as additional sources are reconciled.

## 2. Core entities currently justified

### Acquisition
Represents an acquisition event/process. It may exist before all cataloging is complete.

**Candidate key:** `acquisition_id`

### Collection
A coherent group of material within an acquisition/source context.

**Candidate key:** `collection_id`

### Release
A publication/release/album-level representation. Label/publisher and external release identifiers may belong here or in associated publication relationships as the model matures.

**Candidate key:** `release_id`

### Release Track
A particular track occurrence on a release.

**Candidate key:** `release_track_id`

Natural identifying context is presently `release + track_number`, subject to validation where the source provides additional distinctions.

### Performance
A singular historical performance event of a Work.

**Candidate key:** `performance_id`

The current TTT `recordings.csv` is a provisional stand-in for this concept and should not yet be treated as final historical identity resolution.

### Work
The underlying musical work/composition.

**Candidate key:** `work_id`

This entity is anticipated but has not yet been fully extracted/normalized in the TTT prototype.

### Person
A human participant, composer, lyricist, singer, conductor, etc., when the evidence supports person-level identity.

**Candidate key:** `person_id`

### Ensemble
A named performing ensemble/orchestra.

**Candidate key:** `ensemble_id`

### Recording Manifestation
A particular source/recording representation or path by which a performance is available to us, such as a transfer, remaster, reissue representation, or curated source manifestation.

**Candidate key:** `manifestation_id`

This concept is intentionally provisional and may later be split into publication/source-artifact/recording-transfer concepts as evidence requires.

### Library Item
A particular owned digital file or library artifact.

**Candidate key:** `library_item_id`

### Location
A place or locator at which a library item can be found.

**Candidate key:** `location_id` (or another stable locator identity).

### Source
A source system, publisher, catalog, collection, document, or other evidence origin.

**Candidate key:** `source_id`

### Source Assertion / Evidence Observation
A source-attributed statement or observation about an object or representation.

**Candidate key:** a generated evidence/assertion key; exact design TBD.

## 3. Core relationship sketch

```text
                         ┌──────────────┐
                         │  ACQUISITION │
                         └──────┬───────┘
                                │ 1:M
                                ▼
                         ┌──────────────┐
                         │  COLLECTION  │
                         └──────┬───────┘
                                │ 1:M
                                ▼
                         ┌──────────────┐
                         │   RELEASE    │
                         └──────┬───────┘
                                │ 1:M
                                ▼
                         ┌────────────────┐
                         │  RELEASE_TRACK │
                         └───────┬────────┘
                                 │ represents
                                 ▼
                         ┌────────────────┐
                         │   PERFORMANCE  │
                         └───────┬────────┘
                                 │ is realization of
                                 ▼
                         ┌──────────────┐
                         │     WORK     │
                         └──────────────┘

PERFORMANCE
     │
     │ represented by / available through
     ▼
┌─────────────────────────┐
│ RECORDING_MANIFESTATION │
└────────────┬────────────┘
             │
             │ may appear in / support
             ▼
        RELEASE_TRACK

RELEASE_TRACK
     │
     │ represented by / owned as
     ▼
┌────────────────┐
│  LIBRARY_ITEM  │
└───────┬────────┘
        │ located at
        ▼
┌──────────────┐
│   LOCATION   │
└──────────────┘
```

## 4. People and ensembles

The model should support role-bearing relationships rather than requiring complex participant strings to become canonical identifiers.

```text
PERSON ───────┐
              ├── participates in ──► PERFORMANCE
ENSEMBLE ─────┘
```

Potential roles include singer, conductor, composer, arranger, instrumentalist, and other roles discovered from source evidence.

A specific role model will be introduced only when actual data and query needs require it.

## 5. Evidence and provenance

The evidence layer surrounds the other layers rather than becoming a substitute for them.

```text
SOURCE
   ↓
SOURCE ASSERTION / OBSERVATION
   ↓
CATALOG OBJECT or REPRESENTATION
```

A source assertion should eventually be able to say, in effect:

> Source S represents/claims/value X about object O.

The original source value should remain available even after a value has been promoted into a normalized catalog entity or attribute.

## 6. Publication/release layer

The publication side should distinguish at least:

```text
Label / Publisher
        ↓
Release / Album
        ↓
Release Track
```

It should also permit relationships for subsequent releases, reissues, editions, and other publication histories.

Exact Discogs-style taxonomy is a reference point for this layer, while MusicStewardship maintains its own internal identities.

## 7. Source artifact / historical representation

TTT demonstrates that a single release may contain many record/matrix/take values, and a single raw catalog representation may recur across multiple tracks.

Therefore:

```text
record + matrix + take
```

is not a universal identity key.

It should initially be retained as source evidence and may later be promoted into a structured source-artifact relationship.

## 8. Important cardinality patterns

### Multiple library items for one release track

```text
RELEASE_TRACK 1 ───── M LIBRARY_ITEM
```

The TTT prototype demonstrates this directly: 1,095 owned files correspond to 1,085 distinct release tracks.

### One performance represented by multiple releases

Eventually expected:

```text
PERFORMANCE 1 ───── M RELEASE_TRACK
```

This is central to distinguishing the historical performance from its many publication paths.

### One work with multiple performances

Eventually expected:

```text
WORK 1 ───── M PERFORMANCE
```

This supports the distinction between the same song performed/recorded multiple times.

### Multiple external sources describing one internal entity

Eventually expected:

```text
INTERNAL ENTITY 1 ───── M SOURCE ASSERTION
```

This permits TTT, TANGO-DJ, Discogs, Crackling Tunes, and other sources to contribute independently.

## 9. Current TTT-to-E-R mapping

| Current prototype table | Working E-R concept | Status |
|---|---|---|
| `acquisitions.csv` | Acquisition | current |
| `collections.csv` | Collection | current |
| `releases.csv` | Release | current |
| `release_tracks.csv` | Release Track | current |
| `recordings.csv` | Provisional Performance | temporary/provisional |
| `library_items.csv` | Library Item | current |
| `locations.csv` | Location | current |
| `library_item_tracks.csv` | Library Item ↔ Release Track | current relationship |
| `release_track_recordings.csv` | Release Track ↔ provisional Performance | current relationship |
| `library_item_evidence.csv` | Source Evidence | current relationship |
| `book_metadata.csv` | Derived metadata projection | view/projection |
| `recording_metadata.csv` | Source-attributed secondary metadata | prototype/enrichment |

## 10. Key design restraint

Do not force every source field into an entity table merely because it exists.

The correct progression is:

```text
source representation
       ↓
retain as evidence
       ↓
understand its scope
       ↓
promote when justified
       ↓
normalize only when useful
```

## 11. Query implications

The eventual query/report layer should be able to traverse multiple levels and combine conditions across them.

Representative future query:

> Show all tracks in a selected collection, with release, title, ensemble, singer, performance date, label, source representation, owned file, and location, filtered by any combination of those values.

This is a requirement on the eventual data model, not a requirement to build the UI now.

## 12. Next validation targets

The working E-R model should be tested against additional real cases before database implementation, especially:

1. the same Work with multiple performances;
2. one Performance appearing on multiple releases/labels;
3. multiple recording manifestations of one Performance;
4. release histories/reissues/subsequent editions;
5. person versus ensemble representations;
6. source documents that describe collections or multiple musical objects;
7. TANGO-DJ and Discogs external identifiers and release taxonomy;
8. Crackling Tunes and other curated/commercial source paths.

**Status:** Ready for iterative validation and refinement; not yet a final database schema.
