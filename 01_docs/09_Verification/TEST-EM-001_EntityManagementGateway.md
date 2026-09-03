# TEST-EM-001 — Entity Management Gateway Verification

**Status:** Verification baseline  
**Verifies:** IMPL-EM-001  
**Specification:** SPEC-EM-001  
**Design:** DES-EM-001  
**Requirement:** REQ-EM-001

## Purpose

Verify the reference Entity Management Gateway implementation against the
behavioral acceptance criteria established by SPEC-EM-001.

The tests deliberately exercise the architectural properties that matter most:
preservation of source observations, provisional identity, ambiguity,
evolutionary association, stable identity, separation of current state from
history, and common treatment of entity types.

## Test coverage

| Test | Verification |
|---|---|
| 01 | Source observation preserved |
| 02 | Existing entity receives additional evidence |
| 03 | Unknown observation creates provisional entity |
| 04 | Insufficient information remains unresolved |
| 05 | Same text can map to different entities |
| 06 | Different text can map to same entity |
| 07 | Reassignment preserves original evidence |
| 08 | Identity is not a text hash |
| 09 | Ambiguity remains reviewable |
| 10 | Common gateway works across entity types |
| 11 | Current state is separate from observation history |
| 12 | Invalid references are rejected |

## Expected result

All tests pass against the MS05 implementation baseline.

## Important limitation

This verification tests the gateway implementation in isolation.

It does **not yet** prove that every production source translator is technically
unable to bypass the gateway. That requires an integration test of the supported
ingestion path.

It also does not verify production database durability, automatic entity
matching, authority integration, or final CSV export.

## Traceability

```text
REQ-EM-001
    ↓
DES-EM-001
    ↓
SPEC-EM-001
    ↓
IMPL-EM-001
    ↓
TEST-EM-001
```

This closes the initial documented gateway design chain.

Further integration requirements or tests should be added only when the
supported ingestion path is implemented.
