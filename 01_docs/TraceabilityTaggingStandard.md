# Traceability Tagging Standard

**Status:** Project standard  
**Principle:** KISS — Keep It Sparse  
**Purpose:** Preserve enough explicit linkage to reconstruct the design chain later without building a traceability system now.

## 1. Purpose

MusicStewardship uses sparse catalog tags in Markdown to identify significant architectural ideas and connect them through the development chain.

The tags are deliberately simple so they can be searched by people today and harvested by software later.

The standard is **not** a traceability database.

## 2. The Development Chain

Significant ideas may be traced through:

```text
Foundation / Principle
        ↓
Requirement
        ↓
Design
        ↓
Specification
        ↓
Implementation
        ↓
Test
```

Not every idea requires every level.

Use only the levels that are meaningful.

## 3. Tag Vocabulary

| Tag | Meaning |
|---|---|
| `PRN-###` | Foundational principle |
| `REQ-###` | Requirement |
| `DES-###` | Design |
| `SPEC-###` | Specification |
| `IMPL-###` | Implementation |
| `TEST-###` | Test / verification |
| `DEC-###` | Significant decision |

These seven types are sufficient for normal project traceability.

`EVD` and `HIST` are intentionally **not** part of the basic traceability vocabulary. Evidence and history may be documented using ordinary document structure unless a future need demonstrates that dedicated identifiers are worth the added complexity.

## 4. Identifier Rules

Identifiers are:

- unique within the project;
- short;
- stable;
- never reused;
- independent of filenames and directory locations.

Use a meaningful family prefix followed by a simple number:

```text
PRN-001
REQ-EM-001
DES-EM-001
SPEC-EM-001
IMPL-EM-001
TEST-EM-001
DEC-007
```

A short subsystem qualifier is permitted where it improves readability.

Do not invent elaborate hierarchical numbering.

## 5. Where Tags Appear

For a significant item, put its identifier in the document near the item it identifies.

Preferred form:

```markdown
## Entity Management Gateway

**REQ-EM-001**

All changes to canonical entity knowledge must pass through the Entity Management Gateway.
```

For a document containing several traceable items, a compact section is appropriate:

```markdown
## Traceability

- Requirement: REQ-EM-001
- Design: DES-EM-001
- Specification: SPEC-EM-001
```

Do not add tags to ordinary explanatory prose merely for completeness.

## 6. Linking the Chain

Where useful, state the direct relationship explicitly:

```markdown
## Traceability

- **Foundation:** PRN-002
- **Requirement:** REQ-EM-001
- **Design:** DES-EM-001
- **Specification:** SPEC-EM-001
- **Implementation:** IMPL-EM-001
- **Verification:** TEST-EM-001
```

A lower-level artifact may cite the higher-level identifier it implements.

A test should identify what requirement or specification it verifies.

## 7. Sparse Means Sparse

Do **not** tag:

- every paragraph;
- every function;
- every file;
- routine implementation details;
- temporary experiments.

Tag only things whose identity or relationship will matter when reconstructing the project's reasoning.

When in doubt, **don't tag it**.

## 8. Future Traceability System

The project may eventually use software to harvest these identifiers from Markdown and other project artifacts.

Nothing in this standard requires that system to exist now.

The present objective is simply:

> **Leave enough breadcrumbs that the chain can be reconstructed later without reconstructing it from memory.**

## 9. Architectural Back-Check

For every significant architectural feature, ask:

1. What principle or requirement caused this to exist?
2. Where is its design described?
3. Where is its detailed specification?
4. Where is it implemented?
5. How is it verified?

If an answer is not applicable, that is acceptable.

If an answer should exist but cannot be found, the traceability chain has a gap that should be addressed.

## 10. KISS Rule

This standard exists to reduce complexity, not create another system.

> **Trace the important ideas. Do not trace everything.**

The value of the standard is the continuity of the reasoning chain, not the number of identifiers in the repository.
