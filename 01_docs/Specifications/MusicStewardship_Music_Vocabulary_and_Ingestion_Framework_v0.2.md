# MusicStewardship Music Vocabulary & Ingestion Framework

**Version:** 0.2 — Agreed Clarifications
**Date:** 2026-09-03

## Purpose

MusicStewardship is intended to create a durable, trustworthy body of knowledge about a music collection that can serve several purposes: archival preservation, historical research, music analysis, provenance tracking, and practical DJ use.

The difficulty is that the music arrives from many different sources, each with its own vocabulary, metadata conventions, file naming, folder organization, level of detail, and assumptions about what matters.

The purpose of this effort is therefore to establish a **common MusicStewardship vocabulary and a repeatable method for translating source collections into it**.

The objective is not to force every source into one mold. Instead, the system should:

> **preserve what the source actually says, extract useful information from it, translate that information into a common vocabulary where possible, and retain enough provenance to know where the information came from.**

For DJ libraries in particular:

> **Common model, source-specific interpretation.**

Each DJ library is treated as a knowledge-bearing source system with its own "personality": the characteristic ways its creator organized and expressed musical knowledge. Source-specific rules preserve those differences while producing interoperable source assertions.

This creates a foundation on which increasingly sophisticated uses of the collection can be built.

---

# 1. Why a common vocabulary is necessary

A historical tango recording may arrive as:

- a FLAC or WAV restoration;
- an MP3 with sparse metadata;
- a commercial CD;
- a digital download;
- a folder hierarchy;
- a filename containing several pieces of information;
- a restoration catalog;
- a Discogs release;
- a DJ's personally organized collection;
- or a combination of all of these.

The same musical item may therefore be described several different ways.

Without an explicit vocabulary and mapping system, each new source would require another ad-hoc interpretation.

The vocabulary framework turns this into a controlled process.

### Source assertions

A source assertion is the common unit of interpreted source knowledge. It conceptually contains:

```text
subject
property / relationship
value
source
evidence location
interpretation rule
assertion context/type
uncertainty, where applicable
```

A source assertion is not automatically a canonical fact. It preserves the distinction between what a source says and what MusicStewardship concludes.

---

# 2. Why Discogs is an important reference

MusicStewardship should remain connected to the larger music universe rather than becoming an isolated tango database.

Discogs provides a broad vocabulary covering releases, artists, labels, formats, identifiers, credits, genres/styles, track listings, images, and related release information.

Therefore MusicStewardship will generally maintain an **explicit correlation to Discogs concepts**, even where its own terminology is more appropriate for historical tango.

This does **not** mean that MusicStewardship must reproduce Discogs.

For example, a recording can be useful to a DJ even when we do not yet know which particular physical release it came from. If later research establishes the release, MusicStewardship should be able to attach that information without changing the identity of the recording.

Discogs therefore serves as an **interoperability anchor and external reference**, rather than the complete MusicStewardship ontology.

---

# 3. Why tango-specific sources are necessary

General music cataloging does not capture everything important about historical tango.

The source research has already identified concepts such as:

- recording/take distinctions;
- orchestra;
- singer;
- composer;
- conductor;
- arranger;
- matrix;
- recording date;
- musical/historical period;
- recording key;
- score key;
- transfer speed;
- restoration information;
- source-copy selection.

Historical sound-recording cataloging confirms that these distinctions are meaningful.

Consequently, the MusicStewardship vocabulary should be **tango-centric where tango requires greater precision**, while maintaining explicit mappings to the broader music vocabulary.

---

# 4. The research worksheet

The **Music Vocabulary / Source Survey** is the research instrument behind the framework.

It records, source by source:

- what fields and concepts the source provides;
- what terminology it uses;
- what information is contained in files;
- what information is encoded in filenames;
- what information is encoded in folder hierarchy;
- what information is supplied in release notes or documentation;
- what Discogs concept corresponds to it, if any;
- what TTT or other tango terminology corresponds to it;
- what MusicStewardship concept we believe it represents;
- and what information is **not represented by Discogs**.

The worksheet is therefore both a **research record and a design record**.

It prevents important decisions from disappearing into individual scripts or one-off transformations.

---

# 5. The vocabulary

The resulting **MusicStewardship Vocabulary** establishes the concepts that the database will work with.

The initial vocabulary includes such entities as:

- Performance Event
- Recording
- Take
- Composition
- Person
- Ensemble
- Role
- Release
- Release Copy
- Source Asset
- Source
- Source Collection
- Source Context
- Provenance
- Restoration
- Media
- Identifier

and supporting concepts such as:

- Recording Date
- Genre
- Dance Form
- Singer
- Composer
- Author/Lyricist
- Conductor
- Arranger
- Matrix
- Catalog Number
- Recording Key
- Score Key
- Pitch
- Transfer Speed

The vocabulary intentionally distinguishes **the historical musical object from its manifestations and from the information about those manifestations**.

For example:

> **Performance Event → Recording → Release → Release Copy → Source Asset**

This allows several restorations, releases, copies and files to refer to the same underlying historical music without pretending they are the same object.

---

# 6. Period and Date are distinct concepts

Tango music commonly carries meaningful temporal information at more than one level.

**Date** refers to a specific calendar date or date precision supported by the evidence.

**Period** is a separate semantic concept. A period may be:

- a date range, such as `1939–1942`;
- a named historical or musical period, such as `Guardia Viejo`;
- another source-defined temporal expression.

Both date and period shall be preserved where supplied or reasonably extracted.

A period shall not automatically be converted into an exact date or year. A date shall not automatically be reduced to a period label.

---

# 6. Source context is part of the evidence

Metadata fields are not the only information available during ingestion.

A source collection may communicate important information through:

- folder hierarchy;
- filenames;
- collection names;
- ordering and sequence;
- artwork;
- accompanying documents;
- release notes;
- catalogs;
- distribution notes;
- and other contextual material.

The framework therefore treats this whole envelope as **Source Context**.

For DJ sources, the original hierarchy is always evaluated as evidence. It is not automatically given precedence over filename or metadata evidence; source-specific rules determine how each evidence layer contributes.

The guiding principle is:

> **Extract facts; preserve evidence.**

If a folder hierarchy tells us that a file came from a TTT collection, we may extract an orchestra or collection classification from that hierarchy where justified. But we also preserve the original source context.

This is particularly important because collections from TTT, Jae, restorers, DJs, and other sources may later be reorganized into the canonical MusicStewardship library.

The original context must not disappear when the files move.

---

# 7. Transposition rules turn research into implementation

The vocabulary by itself is not enough.

Every source needs an **ingest specification** explaining how its information becomes MusicStewardship information.

The framework therefore defines controlled transformation types:

- **COPY** — direct value transfer
- **RENAME** — same concept, different field name
- **STANDARDIZE** — normalize representation
- **DECOMPOSE** — split a merged source value into multiple concepts
- **COMBINE** — combine multiple source fields
- **LOOKUP** — map through an authority or controlled vocabulary
- **EXTRACT** — obtain information from an artifact such as artwork or documentation
- **PATH_EXTRACT** — obtain information from folder/path hierarchy
- **DERIVE** — calculate or explicitly infer a value
- **REFERENCE** — retain an external identifier rather than duplicate its information
- **IGNORE** — deliberately exclude a source item from the canonical model
- **SOURCE_CONTEXT** — preserve source organization as provenance
- **ASSERT** — preserve an interpreted source assertion with its evidence and provenance

This is important because many sources will be simple:

> `Title → Title`

while others will require actual interpretation:

> `Record / Matrix / Take → three separate concepts`

or:

> `Folder hierarchy → Source Collection + Ensemble`

---

# 8. Implementation tools

The research framework feeds directly into the implementation tools already being developed.

### Source mapping CSVs

Each source can have a mapping/transposition CSV describing how its fields map into MusicStewardship.

### Transformation scripts

The common transformer implements the rules defined by those mappings.

This means the Python code becomes a **generic transformation engine**, rather than a collection of source-specific programs.

### Validation

The transformed CSV is validated before ingestion.

Validation checks include:

- record counts;
- required fields;
- duplicate source IDs;
- missing values;
- date structure;
- other integrity conditions.

### Ingest processing

The ingest process then records:

- source;
- source snapshot;
- input;
- record counts;
- validation status;
- Git provenance;
- processing status;
- and other provenance information.

---

# 9. Why this separation matters

Without this framework, the database would gradually become a mixture of:

> Discogs terminology + TTT terminology + Tango Tunes terminology + whatever happened to be in an MP3 tag + whatever a particular script assumed.

That would eventually become difficult to understand and almost impossible to maintain.

With the framework:

```text
SOURCE
   ↓
Source Survey
   ↓
Vocabulary Crosswalk
   ↓
Transposition Rule
   ↓
Mapping CSV
   ↓
Generic Transformer
   ↓
Validation
   ↓
Ingest
   ↓
MusicStewardship
```

Each step is inspectable.

A future contributor can determine **why** a field ended up where it did.

---

# 10. DJ use without making the database DJ-only

The underlying music information has many uses.

A historian may want:

- original recording chronology;
- musicians;
- matrices;
- takes;
- source evidence.

A researcher may want:

- releases;
- restorations;
- recording technology;
- provenance.

A preservationist may want:

- source copies;
- technical properties;
- quality assessments.

A DJ may want:

- orchestra;
- singer;
- period;
- dance form;
- useful recordings;
- tanda suitability;
- personal ratings;
- performance observations.

These should **not all clutter the same presentation**.

The core music information should support multiple views.

DJ-specific knowledge can therefore be held in **supporting DJ tables/layers**, attached to the underlying music entities.

This allows a DJ to add increasingly sophisticated knowledge without redefining the canonical music record.

---

# 11. Long-term benefit

The immediate benefit is better ingestion.

The larger benefit is **durability**.

Once the vocabulary and rules are established, adding another collection becomes primarily a research and mapping exercise rather than a new programming project.

It also means that improvements can propagate.

If we discover a better authority for orchestra names, for example, we can improve the authority mapping without changing the original ingested value or losing its provenance.

If we discover that a source's filename contains three useful concepts, we can add a decomposition rule rather than manually correcting thousands of files.

If another DJ later contributes a useful classification system, it can become another supporting vocabulary or knowledge source without contaminating the canonical model.

---

# 12. Future visibility and collaboration

MusicStewardship and TangoMusicDB should remain **distinct but visibly connected**.

MusicStewardship defines the stewardship model, vocabulary, provenance principles, research findings, and intended behavior.

TangoMusicDB provides the concrete implementation capability: schemas, transformation programs, validators, ingest tools, test databases, and eventually export mechanisms.

The relationship should be documented rather than left implicit:

```text
MusicStewardship
    │
    │ defines / researches
    ▼
Vocabulary + Rules + Decisions
    │
    │ implemented by
    ▼
TangoMusicDB
    │
    ├── mapping CSVs
    ├── transformers
    ├── validators
    ├── ingest processors
    └── database
```

In the longer term, the work should be made understandable and reusable outside either project.

A possible eventual public form is a **MusicStewardship Wiki / Toolbox** containing:

- the vocabulary;
- source crosswalks;
- ingest rules;
- mapping templates;
- examples;
- implementation tools;
- provenance practices;
- research notes;
- and documentation explaining how others can contribute.

The goal would not necessarily be to create another centralized music database. It could instead provide a **reusable stewardship framework and toolkit** that other collectors, DJs, researchers, restorers, and developers can adopt.

That also leaves open the possibility of future collaboration: contributors could add source mappings, improve vocabulary definitions, document specialized tango knowledge, or develop new implementations without requiring all of that knowledge to be incorporated into the core system.

---

# 13. Fundamental design principle

The entire effort can ultimately be summarized in four rules:

> **Preserve the source.**  
> **Normalize what we understand.**  
> **Reference authoritative knowledge rather than duplicating it unnecessarily.**  
> **Keep specialized knowledge in specialized layers.**

The result is intended to be simultaneously:

- historically meaningful;
- technically maintainable;
- interoperable with the larger music world;
- useful to tango specialists;
- usable by DJs;
- open to future research;
- and capable of improving as our knowledge improves.
