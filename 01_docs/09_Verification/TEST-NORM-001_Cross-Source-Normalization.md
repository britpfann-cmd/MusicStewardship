# TEST-NORM-001 — Cross-Source Normalization Verification

**Status:** Test specification  
**Verifies:** IMPL-NORM-001  
**Specification:** SPEC-NORM-001  
**Design:** DES-NORM-001  
**Requirement:** REQ-NORM-001

## Verification cases

**T1 — Equivalent person representations converge**  
Use equivalent representations such as `Anibal Troilo`, `Aníbal Troilo`, and `Troilo, Aníbal`.

**T2 — Equivalent group representations converge**  
Use multiple representations of one orchestra/group.

**T3 — Equivalent song representations converge**  
Use harmless source-specific title formatting differences.

**T4 — Possessed music joins a reference-derived entity**  
Create a reference-derived provisional entity, then process an equivalent possessed-track observation and verify that it can resolve to the existing entity without creating a duplicate.

**T5 — Reference evidence joins a music-derived entity**  
Repeat T4 in reverse order.

**T6 — Reference-only entity remains distinguishable**  
Verify reference-only provenance when no possessed-music observation exists.

**T7 — Original observations survive convergence**  
Verify original source values remain intact.

**T8 — Similar text does not force identity**  
Use intentionally distinct entities whose normalized forms are similar.

**T9 — Ambiguity remains reviewable**  
Verify genuinely unresolved observations can remain `REVIEW_REQUIRED` or `UNRESOLVED`.

**T10 — Stable canonical identity**  
Adding another equivalent observation does not manufacture a second canonical entity.

## Pass condition

All ten cases pass without deleting or overwriting source observations.

## Traceability

`PRN-002 → REQ-NORM-001 → DES-NORM-001 → SPEC-NORM-001 → IMPL-NORM-001 → TEST-NORM-001`
