# MusicStewardship — Baseline Understanding

**Date:** 2026-09-13  
**Status:** Working baseline  
**Purpose:** Record the design understanding reached during the TTT whole-corpus cataloging playdate.

## 1. Scope of this baseline

This document records the current understanding of the MusicStewardship catalog/library problem as demonstrated by the Tango Time Travel (TTT) corpus prototype. It is a design baseline, not a final ontology or database schema.

The vocabulary of entities is expected to emerge gradually from source representations, evidence, and the questions the library needs to answer.

## 2. Core design principles

### 2.1 Represent first; abstract second

Capture source representations faithfully before deciding what canonical entity or concept they represent.

A source string, filename, album name, artist string, or compound catalog/matrix/take field is evidence. It is not automatically a canonical entity or identity key.

### 2.2 Preserve source precision

When a source provides unusually precise historical information, retain that precision. TTT may point toward an original source artifact or performance with more detail than many later sources will provide.

Promote a representation into canonical catalog structure when the evidence supports doing so, but preserve the original source representation and attribution.

### 2.3 Identity is separate from representation

Examples:

- a filename is not a performance;
- an album/release is not a performance;
- a record/matrix/take string is not automatically a unique recording;
- an owned FLAC is not the historical performance itself.

### 2.4 Stable primary keys first

The primary navigational thread needs stable unique internal keys. Secondary information can be added, corrected, enriched, or normalized later without disturbing the navigational structure.

### 2.5 Optional information is not a catalog blocker

Required core data establishes a usable catalog object. Optional data is populated when available. Missing optional values are acceptable; extraction errors should be reviewed as extraction problems rather than treated automatically as missing catalog data.

### 2.6 Evidence is first-class

The system must be able to answer not only "what do we currently believe?" but also "where did this information come from?"

Different sources may make different assertions about the same thing. Those assertions should not require overwriting one another.

### 2.7 External sources contribute evidence, mappings, and taxonomy

Sources such as TTT, TANGO-DJ.AT, Discogs, Crackling Tunes, and other curated/commercial sources can contribute evidence and external identifiers. Internal catalog identities remain under MusicStewardship's control.

Discogs is especially useful for release/publication taxonomy and can be used as a reference for release, label, edition, and subsequent-release relationships. It is not assumed to own the internal identity model.

### 2.8 Query/reporting is a core capability

The catalog is intended to support interactive queries and user-generated reports at multiple levels, including collection, release, track, recording/performance, library item, and other levels as the model evolves.

The data model should support arbitrary combinations of criteria rather than a collection of fixed reports.

## 3. Emerging conceptual layers

The current understanding suggests three broad kinds of things, without requiring all of them to become formal entities immediately.

### 3.1 Library/navigation layer

- Acquisition
- Collection
- Release
- Release Track
- Library Item
- Location

These establish the current practical navigation spine.

### 3.2 Musical/historical layer

- Work / composition
- Performance
- Person
- Ensemble
- Recording manifestation / source representation

These concepts are emerging from the need to distinguish a musical work, a singular historical performance event, and the many recording/release paths through which evidence of that performance can reach the library.

### 3.3 Evidence layer

- Source
- Source document/file
- Source assertion / evidence observation
- External identifier / mapping

This layer preserves what a source actually said and supports later reconciliation.

## 4. Performance versus recording manifestation

A **performance** is understood as a singular historical event. If an ensemble performs the same work again, that is a different performance.

A performance can reach the library through multiple recording paths or "shadows": transfers, reissues, remasters, commercial copies, curated collections, or other digital representations.

Therefore the design must eventually distinguish:

```text
Work
  ↓
Performance
  ↓
Recording manifestation / source representation
  ↓
Release / Release Track
  ↓
Library Item
```

The exact vocabulary and entity boundaries remain provisional and will be refined from evidence.

## 5. People and ensembles

People and ensembles are expected to become first-class entities because source strings such as performer/singer/conductor/artist representations may refer to different kinds of participants and roles.

A person may participate in a performance in one or more roles. An ensemble is a distinct entity that can participate in performances.

The initial source representation should be preserved even when later interpreted into Person, Ensemble, and Performance-role relationships.

## 6. Release / publication understanding

Release/publication is distinct from performance.

The emerging release vocabulary includes:

- record label / publisher;
- release or album identity;
- release/catalog number;
- subsequent release / reissue / edition relationships;
- release track.

Many labels can publish material representing the same performance. An orchestra can also create multiple performances of the same work.

A TTT album name is therefore not assumed to be a complete or universal release identity.

## 7. Source-record / matrix / take information

TTT's `CATALOGNUMBER` representation often contains record, matrix, and sometimes take information. This information can vary within one release and can also recur across multiple tracks or files.

Therefore it should initially be treated as a precise source representation/evidence field rather than as a universal unique key.

A future source-occurrence layer may promote parts of this representation into structured fields such as record number, matrix number, take, side, pressing, or other publication/source-artifact details when the evidence warrants it.

## 8. Source media

TTT `SOURCEMEDIA` values are usually consistent within a release, but not universally. The Pedro Laurenz collection contains both `TT/33` and `TT/78` representations.

Therefore `source_media` should not be forced into a single scalar release-level field in the current model. It belongs with the source/material representation until its exact semantic level is established.

## 9. Current TTT prototype — validated counts

The current CSV prototype established the following navigation objects:

| Object | Count |
|---|---:|
| Acquisition | 1 |
| Collections | 13 |
| Releases | 16 |
| Release Tracks | 1,085 |
| Provisional Recordings | 1,085 |
| Library Items | 1,095 |
| Library Item → Release Track links | 1,095 |
| Release Track → Recording links | 1,085 |
| Locations | 1,095 |
| Book metadata rows | 1,095 |
| Library-item evidence observations | 17,779 |

All 1,095 library items were represented in the evidence layer.

The 1,095 library items versus 1,085 release tracks demonstrates that multiple owned files can legitimately represent the same release-track occurrence.

## 10. Current navigation spine

```text
Acquisition
   ↓
Collection
   ↓
Release
   ↓
Release Track
   ↓
Provisional Performance/Recording identity
   ↓
Library Item
   ↓
Location
```

The current recording layer is explicitly provisional. It should not yet be treated as a final historical-performance resolution.

## 11. Book metadata projection

The prototype separates the catalog/navigation structure from the practical metadata written onto an owned library item.

The current Book metadata projection includes:

- title
- artist
- album
- track
- recording date
- composer
- genre

Other values can be added later without changing the navigation structure.

## 12. Provenance approach

The current reliable provenance mechanism is file-level evidence:

```text
Library Item
   ↓
source evidence observations
```

This avoids losing distinctions between multiple owned files that happen to represent the same release track or provisional recording.

A later catalog layer can additionally associate source assertions with promoted catalog entities such as Work, Performance, Release, Person, or Ensemble.

## 13. Acquisition as part of the library process

Acquisition is intentionally included in the model so that the same cataloging process can support both:

1. acquisition in progress; and
2. completed library/catalog records.

The acquisition record can therefore exist before all cataloging and enrichment is complete.

## 14. Development strategy

The CSV prototype is being used as a low-cost relational model before committing to a database implementation.

The intended development sequence is:

```text
Source representations
   ↓
Extraction
   ↓
Intermediate evidence
   ↓
Primary navigation objects
   ↓
Evidence-preserving relationships
   ↓
Promoted entities/attributes when justified
   ↓
Query/reporting views
   ↓
Eventually, database/UI implementation
```

This avoids premature ontology design while still establishing durable identity and relationship rules.

## 15. Working baseline statement

MusicStewardship is being designed as a **queryable, provenance-aware music library catalog** in which:

- source representations are preserved;
- stable internal identities are established conservatively;
- historical performances are distinguished from the many recording/release paths that represent them;
- releases/publications are distinguished from performances;
- owned library files are distinguished from the musical and publication entities they represent;
- people, ensembles, and works emerge as entities from actual evidence and use;
- source precision is promoted when justified rather than discarded;
- external catalogs contribute mappings, taxonomy, and evidence without controlling internal identities; and
- reporting/querying is treated as a fundamental use of the catalog rather than an afterthought.

**Status:** Working baseline for further testing against additional sources and real cataloging cases.
