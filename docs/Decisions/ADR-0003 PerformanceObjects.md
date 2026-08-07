# ADR-0003

## Status

Accepted

## Context

Playback applications need organizational objects that are not musical recordings.

## Decision

Performance Objects are first-class canonical entities.

## Consequences

Applications may implement them differently.

Canonical stewardship remains unchanged.

# Performance Objects Specification

## Purpose

Performance Objects are canonical, playable artifacts that represent
structural, informational, or operational elements of a musical
performance rather than musical recordings.

They allow playback applications such as TangoDJ to present visual
boundaries, announcements, performance markers, transitions, and other
organizational elements while maintaining uninterrupted playlist
execution.

Performance Objects are first-class entities within Music Stewardship
and are exported to client applications as ordinary playable tracks
appropriate to the capabilities of each application.