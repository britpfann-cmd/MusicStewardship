# SPEC-NORM-001 — Cross-Source Normalization Specification

**Status:** Specification baseline  
**Design:** DES-NORM-001  
**Requirement:** REQ-NORM-001

## Specification

A source adapter SHALL emit a common observation structure containing at minimum:

- entity type;
- source identifier;
- original observed values;
- normalized values;
- source context;
- evidence/provenance.

Normalized values SHALL be deterministic for a given source observation and normalization configuration.

The identity layer SHALL produce one of:

- association to an existing entity;
- creation of a provisional entity;
- unresolved;
- review required.

No source adapter may assign or manufacture a canonical Entity ID independently.

## Acceptance criteria

### Convergence
Equivalent observations established by the controlled corpus to describe the same entity SHALL be capable of resolving to the same Entity ID.

### Separation
Normalization SHALL NOT cause distinct entities to resolve to the same Entity ID merely because normalized strings are similar.

### Provenance
Every contributing observation remains retrievable with its original source and observed values.

### Reference provenance
Reference-source observations remain distinguishable from possessed-music observations.

### Evolution
A possessed-music observation introduced after a reference-derived entity SHALL be evaluated against the existing normalized identity space before a new provisional entity is created. The reverse order is also supported.

## Out of scope

Automatic resolution of genuinely ambiguous cases is not required.
