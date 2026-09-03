# Appendix A – Initial Vocabulary

## Purpose

This appendix establishes the initial canonical vocabulary of
Performance Objects recognized by the Music Stewardship architecture.

The vocabulary represents the concepts that a performer, DJ, archivist,
or playback application may need to communicate during the presentation
of a musical performance. These concepts are independent of any
particular software implementation or media format.

The purpose of this appendix is not to define how a Performance Object
is represented, but rather to define **what** it represents.

Each vocabulary entry identifies a canonical concept that may be
exported into one or more application-specific artifacts, including
playable tracks, visual markers, announcements, automation events, or
future native object types.

This appendix defines the canonical language used by Music Stewardship.
It complements, but does not replace, the architectural and technical
specifications that govern Performance Objects and their implementation.

The separation of responsibilities is intentional:

- **Appendix A – Initial Vocabulary** defines the canonical language.
- **PerformanceObjects.md** defines the canonical object model.
- **ExportModel.md** defines the translation of canonical objects into
  application-specific artifacts.
- **Client applications** (such as TangoDJ) define one particular
  implementation of those exported artifacts.

Maintaining these distinct responsibilities preserves a stable canonical
representation while allowing playback applications to evolve
independently. New applications, export formats, and presentation
techniques can be supported without altering the underlying stewardship
model.

This vocabulary is expected to evolve as additional performance
practices, musical traditions, and playback environments are studied.

---

## Relationship to Canonical Data

Although this appendix is presented as human-readable documentation, the
canonical vocabulary it defines is intended to be represented as
structured data.

Each vocabulary entry corresponds to a canonical Performance Object that
may be stored in tabular, JSON, XML, database, or other machine-readable
forms. These structured representations provide the authoritative source
used to generate application-specific artifacts.

The human-readable appendix and the structured vocabulary describe the
same canonical information and should remain synchronized.

---

## Canonical Authority

This appendix constitutes the normative definition of the initial
Performance Object vocabulary.

All generated artifacts, application exports, metadata mappings, and
future implementations shall derive their semantic meaning from the
canonical vocabulary defined herein. Where implementation-specific
representations differ, this appendix remains the authoritative reference
for the intended meaning of each Performance Object.

---

## Stewardship Philosophy

Music Stewardship preserves meaning rather than implementation.

A Performance Object is not defined by its audio content, filename,
metadata, visual appearance, or playback behavior. Those are
implementation details that may vary among client applications.

Instead, each Performance Object represents a stable canonical concept
whose meaning remains constant while its representation may evolve over
time. This separation enables new playback environments, export formats,
and presentation techniques to be adopted without altering the canonical
knowledge preserved by the stewardship repository.

---

## Organization

This vocabulary is organized according to the canonical purpose of each
Performance Object rather than its implementation within any particular
playback application.

Performance Objects are grouped into functional classifications that
describe their role during a musical performance. These classifications
provide a stable organizational framework for stewardship, export,
searching, and future extension.

The classifications defined in this appendix are intended to answer the
question, "Why does this Performance Object exist?" rather than "How is
it represented?"

Each canonical Performance Object belongs to one primary classification,
although individual client applications may represent that object in
different ways.

The initial vocabulary is organized into the following classifications:

- Punctuation Objects
- Announcement Objects
- Structural Objects
- Performance Objects
- Operational Objects

These classifications are expected to evolve as additional performance
practices, musical traditions, and playback environments are studied.
Whenever practical, new concepts should extend the existing
classification system rather than replace it, preserving compatibility
with earlier versions of the canonical repository.

---

## Naming Conventions

This section establishes naming conventions for canonical Performance
Object vocabulary entries.

The objective is to create names that are stable, descriptive, human
readable, and suitable for automated processing. Canonical names should
remain independent of any particular playback application, metadata
standard, filename convention, or user interface.

Each vocabulary entry may possess several distinct names, each serving a
different purpose while referring to the same canonical concept.

Typical representations include:

- Canonical Identifier
- Canonical Name
- Display Title
- Suggested Filename
- Export Name(s)
- Application-specific Representation(s)

The canonical identifier remains stable throughout the lifecycle of the
Performance Object and should not change as applications, metadata
standards, or presentation techniques evolve.

Display titles are intended for human readers and may incorporate visual
formatting appropriate to the destination application.

Suggested filenames provide a recommended storage convention while
remaining independent of any application's internal representation.

Export names are generated as required for individual client
applications and may differ from the canonical name when necessary to
conform to application-specific capabilities or limitations.

These naming conventions preserve a stable canonical vocabulary while
allowing flexible representations across multiple playback
environments.

---

## Punctuation Objects

Punctuation Objects provide visual and semantic structure within a
playlist or performance without altering the musical content.

They function in a manner analogous to punctuation in written language,
helping performers, DJs, and audiences recognize boundaries,
transitions, classifications, and organizational structure.

Punctuation Objects are intended to improve readability, navigation, and
performance workflow while remaining compatible with conventional
playback applications.

The initial vocabulary includes objects identifying dance forms,
structural boundaries, stylistic groupings, and other organizational
markers.

---

