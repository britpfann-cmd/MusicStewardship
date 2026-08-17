# Demonstration Object Specification

## Purpose

A Demonstration Object represents an interlude whose primary purpose is to present, illustrate, teach, exhibit, or showcase material to participants within a performance structure.

## Relationship to Performance Object

Demonstration Object is a specialization of Interlude Object and therefore inherits all Interlude Object and Performance Object requirements and canonical metadata.

## Rationale

Demonstrations are commonly incorporated into events to provide instruction, entertainment, recognition, or cultural context. Modeling demonstrations explicitly preserves their purpose and enables implementations to distinguish them from other interlude types.

## Types

Examples include:

- Dance demonstration
- Instructional demonstration
- Guest presentation
- Exhibition performance
- Competition showcase
- Application-defined demonstration types

## Requirements

A Demonstration Object shall:

- satisfy all Interlude Object requirements.
- represent an activity intended to demonstrate, teach, present, or exhibit.
- support participation by one or more presenters.
- preserve its intended purpose independent of playback application.
- support live, recorded, or application-defined forms of presentation.

## Representation

A Demonstration Object is represented as a specialized Interlude Object. Implementations may realize demonstrations using live performance, recorded media, instructional content, exhibition performances, or application-specific mechanisms while preserving the same performance semantics.

## Terminology

### Demonstration

An interlude whose primary purpose is to present, illustrate, teach, or exhibit material to participants. For example, in tango social dancing, a demonstration may consist of an exhibition dance, instructional presentation, guest performance, or competition showcase.