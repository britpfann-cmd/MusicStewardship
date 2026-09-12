# Historical Discovery: Performance Support and Multi-Use Library Requirements

**Project:** MusicStewardship
**Document Type:** Historical Discovery / Requirements Implications
**Status:** Adopted project history
**Date:** 2026-09-12

---

## 1. Purpose

This document records a significant historical discovery in the development of MusicStewardship: the investigation of DJ performance support demonstrated that the project must distinguish the **music library and its catalog** from the applications that consume that library.

The discovery began with an immediate, personal interest in supporting tango DJ performance. It subsequently exposed requirements that are broader than DJ playback and that should influence the architecture of the general-purpose music library.

The conclusion is:

> **Build the library as a general-purpose body of music knowledge, while explicitly anticipating the requirements of multiple consumers so that today's catalog decisions do not foreclose tomorrow's uses.**

DJ performance remains an important anticipated consumer and an original project objective, but it is **not the current center of development**.

---

## 2. Historical Context

The performance investigation was an early and consequential line of inquiry in MusicStewardship development.

The initial practical question was how existing DJ software could support tango performance: music selection, tandas, cortinas, playlists, navigation, and adaptation during an event.

That investigation revealed a more fundamental distinction:

> **The object of interest is the performance, not merely the playback queue.**

Playback applications commonly represent a performance as a flat sequence of playable items. That is adequate for playback, but it can obscure the higher-level structure that gives a performance its meaning: sections, sets, tandas, interludes, transitions, announcements, demonstrations, energy arcs, alternatives, and recovery paths.

The subsequent Performance Model therefore became deliberately broader than any particular playback application. The current model represents an Event as a structured tree containing Arcs, Tandas, Interludes, and references to canonical recordings. It explicitly treats TangoDJ as a downstream operational representation rather than the canonical semantic model. Existing project documentation states that MusicStewardship retains the meaning, relationships, provenance, decisions, observations, and later performance knowledge, while TangoDJ receives the subset and representation needed for playback. fileciteturn7file8L819-L841

The model's recursive Arc concept was an especially important discovery: the same structure can represent a small musical progression, a substantial section of an evening, or an entire event without flattening the relationships. fileciteturn7file9L956-L995

---

## 3. What the Investigation Discovered

### 3.1 A music library has multiple consumers

The music collection should not be designed solely around its first application.

At minimum, anticipated consumers include:

- **DJ performance** — immediate personal interest and an original project objective.
- **Music research and analysis** — examining repertoire, recordings, artists, periods, sources, and relationships.
- **Curation** — creating reusable collections and musical structures.
- **Archival/stewardship use** — preserving source evidence, provenance, decisions, and historical knowledge.
- **Future applications** — uses that cannot yet be specified.

The library therefore needs a stable semantic foundation that can support different applications without allowing any one application to define the underlying model.

### 3.2 Application representations are not canonical meaning

The Performance Model established an important architectural boundary:

```text
MusicStewardship
      |
      | canonical meaning and structure
      v
Performance Model
      |
      | translation / export
      v
Playback Application
      |
      v
Playback
```

The Performance Model is explicitly **not** intended to reproduce TangoDJ's internal organization. Instead, MusicStewardship remains the canonical source for program meaning and structure, while TangoDJ receives an appropriate operational representation. fileciteturn7file1L166-L193

This principle generalizes beyond DJ software.

### 3.3 Structure and identity must survive downstream translation

A downstream application may have a flatter or poorer representation than the source model. Translation must therefore be understood as a **projection or representation**, not as a definition of the underlying objects.

The Structural Markers investigation was one concrete response to this problem. A marker can expose higher-level performance structure inside a system that understands only a linear playlist. The marker is therefore an implementation technique for preserving human orientation when semantic structure cannot be represented directly. fileciteturn7file0L55-L80

The deeper lesson is that useful semantics should not be discarded merely because a current consumer cannot represent them.

---

# 4. Requirements Implications for the Music Library

The historical discovery has direct implications for current catalog development.

## R1. Keep the core catalog application-neutral

The canonical music catalog must not be modeled as a TangoDJ database, playlist database, or DJ-specific filing system.

DJ-specific information may be represented as a consumer-specific layer, but core recording identity and music knowledge must remain reusable.

## R2. Separate music identity from uses of the music

A recording is an entity in the music library independent of the places where it is used.

The same recording may appear in:

- multiple curated tandas;
- multiple programs;
- multiple events;
- research collections;
- other future applications.

The Performance Model already expresses this distinction through Track References: curated elements reference canonical recordings rather than duplicating recording metadata. fileciteturn7file9L924-L952

## R3. Preserve provenance and source evidence

The catalog must preserve evidence about where information came from rather than collapsing all information into a single supposedly authoritative record.

This principle was established independently through ingestion research:

> **Extract facts; preserve evidence.**

Source-specific assertions and MusicStewardship conclusions must remain distinguishable. The Crackling Tunes research, for example, deliberately preserves original source values while treating standardized values as derived outputs. fileciteturn7file6L664-L674

This requirement is especially important because future consumers may need to interpret the same evidence differently.

## R4. Preserve semantic distinctions even when current use does not require them

The catalog should retain distinctions that have plausible downstream significance rather than prematurely collapsing them for convenience.

Examples already discovered include:

- recording identity vs. file identity;
- source assertion vs. MusicStewardship conclusion;
- period vs. exact date;
- canonical recording vs. Track Reference;
- definition vs. use;
- performance structure vs. playback representation.

The general requirement is:

> **Do not destroy semantic information merely because the current application does not need it.**

## R5. Design stable identities for reuse

Core catalog objects require stable identities that can be referenced by multiple consumers and across multiple representations.

This applies to recordings and, where appropriate, releases, artists, curated objects, and other durable entities.

Identity evidence may come from multiple independent sources. The existing architecture deliberately allows additional evidence layers, including future audio-derived evidence, without changing the underlying identity model. fileciteturn7file0L12-L54

## R6. Treat curated structures as reusable knowledge

A curated structure such as a Tanda should not be treated merely as a playlist instance.

It may be defined once and reused in multiple contexts. An event records **where and how it was used**, while the underlying curated object retains its identity and description. fileciteturn7file9L934-L952

This distinction will also support later observations about actual use.

## R7. Anticipate translation into constrained consumers

The core model should assume that some consumers will have less expressive representations than MusicStewardship.

Therefore:

- semantic objects should exist independently of their exported representation;
- translation should be explicit;
- loss of representation should be recognized as a projection, not a loss of canonical meaning;
- application-specific mechanisms such as structural markers may be used where necessary.

## R8. Keep performance support as a consumer layer

Performance support should remain architecturally possible without making it the center of catalog development.

The current priority is:

> **Build a trustworthy music library and catalog.**

The anticipated performance consumer should nevertheless influence requirements wherever its needs expose important general properties of the catalog.

For example, DJ use reinforces the need for:

- reliable recording identity;
- reusable references;
- rich classification;
- provenance;
- ordering and grouping where meaningful;
- distinction between planned and actual use;
- preservation of historical decisions and observations.

These are not inherently DJ-only requirements.

---

# 5. Architectural Principle Derived from the Discovery

The investigation leads to the following project-level principle:

> **MusicStewardship shall maintain a durable, application-neutral body of music knowledge. Applications and workflows consume representations of that knowledge rather than defining the knowledge itself.**

A related development rule is:

> **Anticipate consumers without allowing consumers to dictate the core model.**

This provides a useful test for future design decisions:

**Question:** Is this concept intrinsic to the music and its stewardship, or is it merely a requirement of one current application?

If it is intrinsic, it belongs in the core model.

If it is consumer-specific, it should normally belong in an application, workflow, translation, or presentation layer.

If the answer is uncertain, preserve the underlying semantic distinction rather than prematurely collapsing it.

---

# 6. Relationship to Current Development

This historical discovery does **not** change the immediate development priority.

Current priority:

```text
Build the music library
        |
        v
Build a trustworthy catalog
        |
        v
Preserve identity, provenance, evidence, and semantic richness
        |
        v
Support multiple consumers
```

DJ performance is one important consumer:

```text
                    MUSIC LIBRARY
                         |
             +-----------+-----------+
             |                       |
       CATALOG / IDENTITY       PROVENANCE
             |                       |
             +-----------+-----------+
                         |
                Reusable knowledge
                         |
          +--------------+--------------+
          |              |              |
         DJ          Research       Future uses
          |
     Curation / Performance
          |
       Playback
```

The performance investigation therefore remains a **historical architectural milestone**, not a signal to shift current development toward DJ software.

---

# 7. Historical Significance

This investigation materially changed the understanding of MusicStewardship.

The project began from a practical need to manage a large music collection and support personal tango DJ activity. Investigation of performance support exposed a more general problem: a durable music collection contains knowledge that cannot safely be reduced to files, folders, tags, or playlists.

The resulting architecture now recognizes several layers:

```text
Music / Recordings
       |
       v
Catalog / Identity
       |
       v
Provenance / Evidence
       |
       v
Curated Knowledge
       |
       v
Application-specific Consumers
```

Performance support was therefore not a side project that happened to produce some DJ features. It was a **discovery mechanism** that revealed requirements for the larger stewardship architecture.

That is why it belongs in project history even though the current development focus is elsewhere.

---

# 8. Follow-on Documentation

This historical discovery should be preserved separately from the current Performance Model.

Recommended document roles:

- **History:** why and through what investigation these requirements were discovered.
- **Architecture / Performance Model:** what the current semantic model is.
- **Requirements:** what the catalog must preserve to support current and anticipated consumers.
- **ADRs:** individual architectural decisions made in response to particular discoveries.
- **Research:** experiments and evidence that led to the conclusions.

This separation preserves both the current design and the reasoning that produced it.

---

## 9. Key Statements to Preserve

The following statements summarize the durable conclusions from this period of development:

> **Performance support is an original project objective, not the current center of development.**

> **Build the library as a general-purpose body of music knowledge, while explicitly identifying the requirements of anticipated consumers so today's catalog decisions do not foreclose tomorrow's uses.**

> **Applications consume the library; they do not define it.**

> **Do not destroy semantic information merely because the current application does not need it.**

> **Extract facts; preserve evidence.**
