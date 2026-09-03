# DES-NORM-001 — Cross-Source Normalization Design

**Status:** Design baseline  
**Requirement:** REQ-NORM-001  
**Gateway:** DES-EM-001

## Design principle

Source translators may understand different source grammars, but they SHALL NOT invent independent canonical identity systems.

All source paths converge on a common normalized representation before canonical identity is established.

```text
Sources → Source Translation → Common Normalization
                                      ↓
                              Identity Candidates
                                      ↓
                            Entity Management Gateway
                                      ↓
                               Canonical Entity
```

## Three layers

### Source observation
Exactly what the source supplied, including source-specific spelling and context.

### Normalized observation
A deterministic/common representation suitable for comparison.

### Canonical identity
The Entity Manager determines whether observations refer to the same entity, different entities, or remain unresolved.

**Normalization is preparation for identity resolution, not identity resolution itself.**

## Provenance

Provenance belongs to observations/evidence rather than separate classes of canonical entities.

## Reference-first and music-first

Both orders are supported:

`Reference → provisional entity → possessed music → strengthened association`

and:

`Possessed music → provisional entity → reference evidence → strengthened association`
