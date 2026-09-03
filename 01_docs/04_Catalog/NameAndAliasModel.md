# Name and Alias Model

**Status:** Current architectural baseline  
**Version:** V1 — evolving

## Purpose

Defines handling of names, spelling variants, alternate titles, aliases, attribution differences, and ambiguous name reuse.

## Name is not identity

A name is an observed value associated with an entity. It is not itself the entity.

The catalog therefore requires a name register or index that can locate candidate entities without assuming textual equality establishes identity.

## First occurrence

A previously unseen name value should be entered into the name register. The best-supported current entity association may be established at that time.

## Later occurrences

Later sources may provide different spelling, accents, transliterations, alternate titles, abbreviations, historical names, different attribution, or conflicting attribution. The observed source value should be preserved.

## Same name, different entities

The name index must permit one name value to refer to more than one entity.

    "Sue"
       |
       +---- Person A
       |
       +---- Person B

## Different names, same entity

An entity may have several observed names.

    Song A
       |
       +---- "Olvido"
       |
       +---- "El Olvido"

The relationship may eventually be classified as an alias, alternate title, spelling variant, or another appropriate relationship.

## Unresolved relationships

Possible states include spelling variant, alternate title, alias, historical name, transliteration, abbreviation, attribution variant, and unresolved.

The catalog should permit later refinement.

## Attribution

Differences in attribution are observations requiring evaluation. A source assertion should not be silently rewritten merely because another source gives a different attribution.

## Self-correcting behavior

The name system must support later evidence establishing that two names refer to one entity, one name refers to multiple entities, or an earlier association was incorrect.
