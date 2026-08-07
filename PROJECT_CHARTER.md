# Music Stewardship Project Charter

> *Music collections are more than audio files. They embody history,
> editorial judgment, provenance, relationships, and accumulated
> experience. Music Stewardship exists to preserve that knowledge
> independently of any particular software application so that it
> remains understandable, reusable, and transferable across
> generations.*

---

# Executive Summary

Music Stewardship is an open reference architecture for the long-term
stewardship of recorded music and musical knowledge.

The project recognizes that recordings are only one component of a
musical collection. Metadata, provenance, editorial decisions,
relationships between recordings, performance practice, and accumulated
experience are equally valuable and deserve long-term preservation.

Rather than creating another music player or library manager, Music
Stewardship provides a canonical framework from which many different
applications may derive the representations they require.

The architecture is intentionally application-independent, allowing
today's software to evolve or be replaced without losing the knowledge
accumulated over decades of musical stewardship.

---

# Mission

Music Stewardship exists to preserve recorded music as a living body of
knowledge.

The project provides a canonical framework for organizing recordings,
metadata, provenance, performance assets, analytical observations,
relationships, and accumulated experience independently of any software
application.

Applications such as TangoDJ, MediaMonkey, foobar2000, MusicBee, Mixxx,
or future tools consume representations appropriate to their own
capabilities but do not own the canonical information.

Music Stewardship remains the authoritative source.

---

# Vision

Create a long-lived, extensible stewardship environment that:

- Preserves recordings without unnecessary duplication.
- Maintains accurate, verifiable metadata.
- Documents provenance and editorial history.
- Captures relationships among recordings, performances, and collections.
- Supports preparation for live performance.
- Preserves observations and accumulated experience.
- Exports appropriately to many client applications.
- Remains independent of any individual software platform.

The objective is not merely to organize music, but to preserve musical
knowledge for future generations.

---

# Audience and Intent

Music Stewardship is intended as an open technical resource for anyone
interested in the stewardship of recorded music.

The project welcomes participation from:

- Collectors
- Archivists
- Librarians
- Musicians
- DJs
- Software developers
- Researchers
- Educators
- Students

Although the first implementation focuses on Argentine Tango and the
TangoDJ ecosystem, the underlying concepts are intended to be broadly
applicable to other musical traditions and software environments.

Readers are encouraged to study, adapt, extend, and implement these
concepts within their own collections and applications.

The goal is not to prescribe a single workflow but to provide a common
conceptual framework that encourages collaboration while preserving
compatibility among diverse implementations.

---

# Scope

Music Stewardship encompasses:

- Canonical music repository
- Metadata management
- Ingest and validation
- Provenance tracking
- Duplicate detection
- Audio analysis
- Performance Objects
- Performance preparation
- Knowledge management
- Observations
- Experience
- Export to client applications

---

# Guiding Principles

1. Every recording has one canonical representation.

2. Metadata belongs to the recording rather than the application.

3. Knowledge is distinct from metadata.

4. Applications consume translated representations rather than canonical
   data.

5. Performance Objects are first-class canonical entities.

6. Editorial decisions should be documented and reproducible.

7. Knowledge accumulates over time and should never be discarded without
   reason.

8. Long-term stewardship takes precedence over short-term convenience.

---

# Architectural Philosophy

Music Stewardship separates permanent knowledge from temporary
implementation.

```
Canonical Repository
        │
        ▼
 Metadata & Knowledge
        │
        ▼
 Analysis & Enrichment
        │
        ▼
 Export Layer
        │
        ▼
 Client Applications
```

Each layer has a distinct responsibility and may evolve independently.

---

# Long-Term Goals

Develop an extensible stewardship environment capable of supporting:

- Individual collections
- Public archives
- Performance libraries
- Music educators
- Researchers
- DJs
- Future software platforms
- Musical communities not yet considered

The architecture should remain stable while implementation technology
continues to evolve.

---

# Non-Goals

Music Stewardship is **not**:

- a replacement for playback software
- a media player
- a DJ application
- a metadata service
- an attempt to standardize artistic decisions

Instead, it provides the canonical foundation upon which such
applications may build.

---

# Relationship to Client Applications

Music Stewardship owns canonical information.

Client applications own presentation, workflow, and user interaction.

Applications receive representations appropriate to their own
capabilities while the canonical repository remains unchanged.

Current reference implementations include:

- TangoDJ
- MediaMonkey
- foobar2000
- MusicBee
- Mixxx

Additional applications may be supported through translators and export
modules without modifying the underlying stewardship model.

---

# Closing Statement

Music Stewardship is founded on the belief that preserving music means
preserving more than recordings.

By preserving knowledge, context, provenance, editorial judgment,
relationships, and accumulated experience alongside the recordings
themselves, future generations inherit not merely collections of files,
but collections of understanding.