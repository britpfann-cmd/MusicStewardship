# Entity Reference and Presentation Index — Design Addendum

**Status:** Initial design decision
**Date:** 2026-09-24

## Purpose

Define the small internal indexing layer that is built after canonical CSV import.

## Principles

1. Entity identity is represented by an opaque stable internal ID.
2. Internal IDs are keys only; users see names.
3. Source names are preserved with provenance.
4. Multiple source names may associate with one entity.
5. The same name may associate with multiple entities when evidence requires it.
6. TTT supplies the initial vocabulary seed but is not an authority.
7. External references such as TANGO-DJ.AT may supply additional names and vocabulary.
8. Preferred and short names are presentation choices and may differ by user.
9. A short name is particularly useful for compact DJ output.
10. Entity association must not modify or erase the source value on a catalog record.

## Initial entity/reference fields

The initial index should remain small. The first demonstrated fields are:

- `entity_id`
- `entity_type`
- `observed_name`
- `name_source`
- `source_record_id`
- `association_status`
- `preferred_name` (presentation layer)
- `short_name` (presentation layer)

Additional entity types or relationships are added only when actual collection evidence requires them.

## Association status

Initial values may include:

- `provisional`
- `assumed`
- `confirmed`
- `disputed`
- `rejected`

A provisional entity is valid catalog state and can later be refined, merged, split, or reassigned without deleting the original observation.

## Name selection

The first accumulated corpus can nominate the most frequently observed equivalent name as the default preferred-name candidate. This is a presentation heuristic only. Users may select a different preferred or short name.

## Boundary

Entity IDs are not part of the public source-value vocabulary. They are attached to the managed internal catalog/index after canonical CSV construction.
