# IMPL-EM-001 — Entity Management Gateway Implementation

**Status:** Implementation baseline  
**Implements:** SPEC-EM-001  
**Design:** DES-EM-001  
**Requirement:** REQ-EM-001

## Implementation choice

The first implementation uses a small SQLite-backed gateway rather than
introducing the full canonical catalog database.

This keeps the implementation boundary visible and testable while leaving the
eventual catalog persistence architecture open.

## Implemented behavior

`EntityGateway` provides the common boundary for:

- accepting and preserving observations;
- creating provisional entities;
- associating observations with existing entities;
- marking observations unresolved;
- marking observations for review;
- revising associations;
- retrieving current entity state;
- retrieving preserved source observations.

### Identity

Entity identifiers are generated with UUIDs. They are not derived from
current text, names, dates, or source identifiers.

### Evidence

Source observation, context, evidence, and interpreted values are stored
separately in the observation record.

### Evolution

Associations are separate records. Revising an association does not delete the
source observation.

### Entity types

The gateway has no entity-specific manager. `entity_type` is data supplied to
the common gateway.

## Deliberately not implemented yet

This baseline does not attempt to solve:

- automatic matching;
- authority-provider integration;
- merge/split policy;
- numeric confidence scoring;
- canonical catalog export;
- user interface;
- complete production transaction/recovery policy.

Those are next-level work and should be added only when supported by the
specification and tests.

## Traceability

`REQ-EM-001 → DES-EM-001 → SPEC-EM-001 → IMPL-EM-001`

`TEST-EM-001` remains the next formal verification work product.
