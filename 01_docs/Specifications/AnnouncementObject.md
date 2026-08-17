# Announcement Object Specification

## Purpose

An Announcement Object represents an interlude whose primary purpose is to communicate information to participants within a performance structure.

## Relationship to Performance Object

Announcement Object is a specialization of Interlude Object and therefore inherits all Interlude Object and Performance Object requirements and canonical metadata.

## Rationale

Announcements communicate information that is relevant to participants but is not itself part of the musical performance. Modeling announcements explicitly preserves their informational purpose and enables implementations to distinguish them from other interlude types.

## Types

Examples include:

- Welcome announcement
- Schedule announcement
- Safety announcement
- Closing announcement
- Application-defined announcement types

## Requirements

An Announcement Object shall:

- satisfy all Interlude Object requirements.
- communicate information to participants.
- preserve its informational purpose independent of playback application.
- support spoken, recorded, textual, or application-defined forms of presentation.
- support use before, during, or after musical performance elements.

## Representation

An Announcement Object is represented as a specialized Interlude Object. Implementations may realize announcements using recorded speech, synthesized speech, displayed text, or application-specific mechanisms while preserving the same performance semantics.

## Terminology

### Announcement

An interlude whose primary purpose is to communicate information to participants within a performance structure. For example, in tango social dancing, announcements may be used to welcome attendees, communicate schedule changes, recognize organizers, or provide event information.