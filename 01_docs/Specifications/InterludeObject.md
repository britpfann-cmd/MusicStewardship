# Interlude Object Specification

## Purpose

An Interlude Object represents a non-dance segment within a performance structure. Interludes provide separation, transition, communication, or other contextual functions between musical performance elements.

## Relationship to Performance Object

Interlude Object is a specialization of Performance Object and inherits all Performance Object requirements and canonical metadata.

## Rationale

Interludes are distinct from musical recordings and dance units. Modeling them explicitly allows performance structures to represent the complete event experience rather than only the musical content.

## Interlude Types

Examples include:

- Cortina
- Announcement
- Break
- Demonstration
- Introduction
- Future application-defined types

## Requirements

An Interlude Object shall:

• represent a non-musical performance element.
• support use between musical performance elements.
• preserve its intended performance function independent of playback application.
• support specialization into more specific interlude types.

## Representation

Implementations may represent interludes using playable audio, silence, spoken content, or application-specific mechanisms while preserving the same performance semantics.

## Terminology

### Interlude

A non-musical performance element used to separate, transition, or augment musical portions of a performance.