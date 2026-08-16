# Performance Object Generator

## Purpose

The Performance Object Generator transforms canonical Performance Object
definitions maintained by the Music Stewardship repository into
application-specific artifacts suitable for playback, cataloging, and
distribution.

The generator provides the implementation bridge between the canonical
Music Stewardship model and individual client applications while
preserving the semantic meaning of each Performance Object.

Rather than manually creating individual audio files, the generator
produces them automatically from structured canonical data. This
approach ensures consistency, repeatability, and synchronization betweenv
the canonical repository and all generated artifacts.

---

## Scope

This specification defines:

- generator inputs
- generator outputs
- processing workflow
- metadata mapping
- audio generation
- artifact naming
- validation requirements
- extensibility requirements

This document does not define the canonical Performance Object model.
That model is specified in **PerformanceObjects.md**.

---

## Design Objectives

The generator shall:

- generate artifacts entirely from canonical data
- require no manual editing of generated files
- preserve canonical identifiers
- preserve semantic meaning across exports
- support multiple export targets
- produce repeatable results
- remain independent of any individual playback application

---

## Architectural Context

Within the Music Stewardship architecture, the Performance Object
Generator occupies the implementation layer.

```
Canonical Repository
        │
        ▼
Performance Objects
        │
        ▼
Canonical Vocabulary
        │
        ▼
Performance Object Generator
        │
        ├── FLAC
        ├── MP3
        ├── JSON
        ├── XML
        ├── Playlists
        └── Future Formats
```

The generator is responsible for translation of canonical definitions
into implementation-specific artifacts. It does not alter or extend the
canonical information.

---

## Inputs

The generator consumes structured canonical data.

Typical inputs include:

- PerformanceObjects.csv
- Vocabulary definitions
- metadata templates
- audio templates
- export configuration
- application profiles

Future implementations may replace CSV with JSON, XML, SQLite, or other
canonical storage formats without changing the generator architecture.

---

## Processing Pipeline

The generator performs the following logical operations:

1. Load canonical vocabulary.
2. Validate canonical data.
3. Resolve metadata templates.
4. Generate application metadata.
5. Generate audio artifacts.
6. Embed metadata.
7. Generate manifests.
8. Validate generated artifacts.
9. Export output packages.

Each stage shall be independently testable.

---

## Outputs

The initial implementation shall generate:

- FLAC files
- MP3 files (optional)
- metadata manifests
- generation reports
- validation reports

Future outputs may include:

- TangoDJ libraries
- MediaMonkey libraries
- MusicBee libraries
- foobar2000 libraries
- playlist templates
- application configuration files

---

## Metadata Generation

Metadata shall be derived exclusively from canonical Performance Object
definitions.

Generated metadata may include:

- Title
- Artist
- Album
- Genre
- Comment
- UUID
- Classification
- Export Version
- Generator Version

Application-specific metadata shall not modify canonical meaning.

---

## Audio Generation

Performance Objects require playable audio in order to participate in
continuous playlist execution.

The initial implementation generates near-silent audio of minimal
duration.

Future implementations may generate:

- spoken announcements
- synthesized speech
- musical cues
- tones
- sound effects
- application-defined audio

Audio generation remains independent of canonical semantics.

---

## Artifact Naming

Generated filenames should follow deterministic naming rules.

Canonical identifiers remain stable.

Display names may vary according to export target.

Filename conventions should support:

- readability
- sorting
- portability
- operating-system compatibility

---

## Validation

The generator shall validate:

- required metadata
- identifier uniqueness
- vocabulary integrity
- export mappings
- generated audio
- embedded metadata
- output completeness

Generation shall fail if canonical integrity cannot be maintained.

---

## Extensibility

The generator is designed to support future export targets without
changing the canonical repository.

New export formats should be implemented through export adapters rather
than modifications to the canonical data model.

---

## Future Enhancements

Future versions may support:

- graphical separators
- generated artwork
- multilingual metadata
- synthesized announcements
- native TangoDJ extensions
- application-specific visual objects
- additional playback environments

---

## Relationship to Other Specifications

This document defines the implementation of Performance Object
generation.

Related specifications include:

- PerformanceObjects.md
- ExportModel.md
- CanonicalMetadata.md
- Appendix A – Initial Vocabulary

Together these specifications separate canonical knowledge from
implementation while ensuring consistent generation of application-
specific artifacts.