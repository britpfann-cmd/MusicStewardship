# Entity Identity

**Status:** Current architectural baseline  
**Version:** V1 — evolving

## Purpose

Defines how MusicStewardship establishes, distinguishes, reuses, corrects, merges, and splits canonical entities.

## Identity versus observation

A canonical entity is distinct from any source observation, name, spelling, attribution, or catalog record.

A source provides observations about an entity. An observation may be associated with an established entity or may lead to creation of a new entity.

## Named entities

This applies to Person, Group, Song, Event, and Performance.

An entity has a stable internal identity. Names, attributes, observations, evidence, and associations may be refined as knowledge improves.

## Initial assignment

Use the best available evidence to determine whether an observation represents an existing entity or a new entity. When an established entity is a well-supported match, reuse it rather than unnecessarily creating a duplicate.

This is a working assignment and remains subject to later correction.

## Same name does not imply same entity

Two distinct entities may have the same name.

Therefore: **name equality is not entity equality.**

The catalog must allow a name value to point to multiple entities when evidence requires it.

## Different names may identify the same entity

An entity may have multiple observed names. For example, "Olvido" and "El Olvido" may eventually be established as names referring to the same Song.

The relationship must be supported by evidence rather than assumed from text similarity alone.

## Later correction

New evidence may establish that an earlier association was correct, incomplete, provisional, incorrectly assigned, a duplicate, part of an entity that must be split, or an entity that should be merged with another.

Correction must preserve the underlying observations and their provenance.

## Performance identity

Song + Group + Recording Date is a useful working key but is not assumed to be a universal definition of Performance identity. A group may record the same Song more than once, and dates may be imprecise, provisional, or conflicting.

## Design objective

Make ordinary catalog construction convenient while retaining enough evidence and provenance to permit later correction.


---

## V2 Design Principle — Evolutionary Association

Association is evolutionary rather than a one-time identity decision.

When a new observation is encountered, the system uses the best available
evidence to determine whether it can be associated with an established
entity.

If no established entity is sufficiently supported, the system creates a
**provisional entity**.

A provisional entity is valid catalog state. It is not a failure to identify
the entity.

Additional observations may subsequently be associated with the provisional
entity. As evidence accumulates, the entity and its associations may be
confirmed, refined, reassigned, split, merged, or otherwise revised.

The lifecycle is therefore:

```text
new observation
      |
      v
existing entity sufficiently supported?
      |                    |
     yes                   no
      |                    |
      v                    v
associate              create provisional
      |                    |
      +---------+----------+
                |
                v
       additional instances
                +
             evidence
                |
                v
        evolving knowledge
```

The current association represents the catalog's best understanding at the
present moment. A change in current association does not erase the original
observation or the evidence that supported an earlier interpretation.

A provisional identity should retain its stable identity reference as its
authority/status changes. Status evolution is not itself a reason to create a
new entity identity.

### Fundamental rule

> **A provisional conclusion is useful knowledge, not an error. The catalog
> should be able to learn without losing what it previously knew.**



## Addendum — 2026-09-24 Seed Vocabulary and Presentation Names

The first major Restorer collection, TTT, will seed the initial entity/name vocabulary. This is a practical bootstrapping measure, not an assertion that TTT is authoritative.

Subsequent collections contribute additional observed names. Different names are initially treated as candidate representations of an existing entity when the available evidence supports that association; the source observation is always preserved.

An external public reference such as TANGO-DJ.AT may be used as a **name/reference vocabulary source**. MusicStewardship does not copy its recording values as catalog truth merely because a name occurs there.

Internal entity identifiers are opaque stable keys. They exist for indexing and relationships and are not intended for user-facing display.

An entity may have many observed names. User-facing presentation is separate from identity:

- `preferred_name` is a presentation choice;
- `short_name` is an optional compact presentation alias, particularly useful for DJ output.

A user's presentation choices do not change the underlying entity identity or source observations.
