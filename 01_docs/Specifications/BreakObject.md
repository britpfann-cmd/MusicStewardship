# Break Object Specification

## Purpose

A Break Object represents an interlude that temporarily suspends the normal flow of a performance structure. During a break, alternative activities may occur before the normal flow resumes.

## Relationship to Performance Object

Break Object is a specialization of Interlude Object and therefore inherits all Interlude Object and Performance Object requirements and canonical metadata.

## Rationale

Breaks are common elements of many performance structures and events. Modeling breaks explicitly preserves their operational and social purpose and enables implementations to distinguish them from other interlude types.

## Types

Examples include:

- Refreshment break
- Social break
- Scheduled intermission
- Venue transition
- Live music interlude
- Demonstration interlude
- Exhibition or performance break
- Application-defined break types

## Requirements

A Break Object shall:

- satisfy all Interlude Object requirements.
- represent a temporary suspension of the normal performance flow.
- support use between performance elements.
- preserve its intended purpose independent of playback application.
- support alternative activities during the break period.
- support optional audio, spoken content, silence, live performance, or application-defined behavior.

## Representation

A Break Object is represented as a specialized Interlude Object. Implementations may realize breaks using silence, recorded audio, live music, announcements, demonstrations, timers, visual indicators, or application-specific mechanisms while preserving the same performance semantics.

## Terminology

### Break

An interlude whose primary purpose is to temporarily suspend the normal flow of a performance structure. A break may include silence, recorded music, live music, demonstrations, announcements, social activities, refreshments, or other event activities before the normal flow resumes.