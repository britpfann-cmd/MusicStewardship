# Music Stewardship Project Charter

Music collections are more than audio files. They embody history, editorial judgment, provenance, relationships, and accumulated experience. Music Stewardship exists to preserve that knowledge independently of any particular software application so it remains understandable, reusable, and transferable across generations.

---

## Mission

Music Stewardship exists to preserve recorded music as a living body of knowledge.

The project provides a canonical framework for organizing recordings, metadata, provenance, performance assets, analytical observations, and accumulated experience independently of any individual software application.

Applications such as TangoDJ, MediaMonkey, foobar2000, MusicBee, Mixxx, or future tools consume representations of this knowledge but do not own it.

The stewardship system remains the authoritative source.

---

## Vision

Create a long-lived, extensible music stewardship environment that:

- Preserves recordings without unnecessary duplication.
- Maintains accurate, verifiable metadata.
- Documents provenance and editorial history.
- Supports performance preparation and live presentation.
- Captures observations and experience gained through use.
- Exports appropriately to multiple playback and cataloging applications.
- Remains independent of any single software platform.

The objective is not simply to organize music, but to preserve musical knowledge for future use and future generations.

---

## Scope

Music Stewardship includes:

- Canonical music repository
- Metadata management
- Ingest and validation pipeline
- Provenance tracking
- Duplicate detection
- Audio analysis
- Performance objects
- Playlist construction
- DJ knowledge
- Performance observations
- Export to external applications

---

## Guiding Principles

1. Every recording has one canonical representation.

2. Metadata belongs to the recording, not the application.

3. Knowledge is distinct from metadata.

4. Applications receive translated representations appropriate to their capabilities.

5. Performance Objects are first-class entities alongside recordings.

6. Editorial decisions are documented and reproducible.

7. The system should preserve both information and accumulated experience.

8. Every design decision should favor long-term stewardship over short-term convenience.

---

## Architecture

Music Stewardship consists of several cooperating layers:

- Canonical Repository
- Metadata Layer
- Ingest Pipeline
- Analysis Layer
- Knowledge Layer
- Performance Layer
- Export Layer

Applications interact only through the Export Layer.

---

## Long-Term Goals

Develop an extensible stewardship environment capable of supporting:

- Tango DJs
- Music collectors
- Archivists
- Researchers
- Teachers
- Performers
- Future applications not yet conceived

The architecture should remain stable while implementation technology evolves.

---

## Non-Goals

Music Stewardship is not intended to replace playback software.

It is not intended to become another music player.

It does not compete with DJ applications.

Instead, it complements existing applications by providing canonical organization, knowledge, and long-term stewardship.

---

## Relationship to Client Applications

Music Stewardship owns canonical information.

Client applications own presentation and performance.

Examples include:

- TangoDJ
- MediaMonkey
- foobar2000
- MusicBee
- Mixxx

Additional applications may be supported through translators and export modules without changing the canonical repository.