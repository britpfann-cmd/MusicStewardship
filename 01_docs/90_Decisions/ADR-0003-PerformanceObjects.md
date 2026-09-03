# Performance Object Specification

## Purpose

Performance Objects are canonical entities that represent structural,
informational, or operational elements of a musical performance rather
than musical recordings.

Unlike musical recordings, Performance Objects exist to organize,
annotate, guide, or enhance the presentation and execution of a
performance. Examples include punctuation markers, announcements,
performance cues, transitions, and other non-musical elements that
contribute to the listener's or performer's experience.

Within the Music Stewardship architecture, Performance Objects are
first-class canonical entities possessing their own identity, metadata,
classification, and lifecycle. They are independent of any specific
playback application or implementation.

During export, a Performance Object may generate one or more
application-specific artifacts appropriate to the capabilities of the
destination software. For example, a TangoDJ export may produce a silent
playable track with descriptive metadata, while another application may
represent the same canonical object as a visual marker, cue point, or
automation event.

This separation between canonical representation and application-specific
implementation allows Music Stewardship to preserve meaning while
supporting diverse playback environments without altering the underlying
stewardship model.

---

## Scope

This specification defines the canonical representation, behavior,
metadata, lifecycle, and export requirements for Performance Objects.
It does not prescribe the implementation details of any individual
playback application.

---

## Rationale

This section explains the architectural motivations behind Performance
Objects and the design decisions that distinguish them from musical
recordings.

---

## Requirements

This section defines the functional and non-functional requirements that
all Performance Objects shall satisfy.

---

## Terminology

Definitions of terms used throughout this specification.

---

## Canonical Representation

Defines the canonical data model used to represent Performance Objects
within Music Stewardship.

---

## Classification

Defines the categories of Performance Objects and their intended use.

### Punctuation Objects

Structural markers that improve the readability and organization of
playlists and performances.

### Announcement Objects

Objects intended to communicate information to performers or audiences.

### Performance Objects

Objects representing scheduled performances, demonstrations, or other
planned presentation events.

### Operational Objects

Objects supporting technical or operational aspects of a performance,
including testing, setup, synchronization, and automation.

### Future Categories

Reserved for future expansion without requiring structural changes to
the canonical model.

---

## Metadata Model

Defines the canonical metadata associated with every Performance Object.

---

## Audio Representation

Defines the audio characteristics used when generating playable
representations of Performance Objects.

---

## Visual Representation

Defines the conventions used to present Performance Objects within user
interfaces and exported applications.

---

## Generated Artifacts

Defines the files and other artifacts generated from the canonical
representation.

---

## Export Mapping

Defines how canonical Performance Objects are translated into
application-specific representations.

---

## TangoDJ Implementation

Describes the current reference implementation using TangoDJ.

---

## Validation

Defines the criteria used to verify that a Performance Object conforms
to this specification.

---

## Examples

Illustrates representative Performance Objects and their application.

---

## Future Extensions

Documents anticipated enhancements while preserving compatibility with
the canonical model.

---

## Appendix A – Initial Vocabulary

Reference vocabulary for the initial library of Performance Objects.

---

## Appendix B – Metadata Mapping

Cross-reference between canonical metadata and application-specific
metadata representations.

---

## Appendix C – Naming Conventions

Defines naming standards for canonical objects, generated artifacts, and
exported representations.