# MusicStewardship C Development Notebook

**Started:** 2026-09-27  
**Purpose:** Running record of observations, lessons learned, errors, omissions, interface findings, and production-model requirements discovered while validating C.

This notebook is deliberately separate from the final production architecture. It records what the development work teaches us.

---

## 2026-09-27 — Change in Development Posture

### Observation

The project has been cultivating individual processing/validation components without always maintaining the production forest-level view.

### Lesson

Validation components are design instruments unless explicitly promoted to production.

### Decision

Finish validation with minimal disturbance. Record what needs to be addressed in the production model. After validation, design and build the production system deliberately.

### Production implication

Production architecture must be designed from accumulated requirements and validated contracts rather than from the accidental structure of exploratory code.

---

## 2026-09-27 — Directory Context

### Observation

Directory information is environmental source evidence, not track metadata.

Different source families use directory hierarchy differently:

- TTT: directory hierarchy identifies/characterizes release/ensemble context.
- CT: monthly distribution directories provide source context.
- DJ collections: multiple directory levels can supply genre, orchestra, singer/instrumental status, tune, etc.
- At least one FromJae case uses directory context for a tanda.

### Validation result

A fresh TTT chain demonstrated that directory information can travel from the source tree through source ingest and Rosetta processing into record-level observations.

### Production implication

The production system needs a generic directory-context capability plus source-specific interpretation controls. It must not reduce this to a single universal meaning for `directory_path`.

---

## 2026-09-27 — Source Inventory Interface

### Observation

The current source-tree implementation produces a unified inventory, while some older processing components expect separate `source_tree_directories.csv` and `source_tree_files.csv` artifacts.

### Lesson

This is an interface/architecture issue, not merely a script bug.

### Production requirement

The production C architecture needs one explicit source-inventory contract. Legacy representations must not remain hidden dependencies.

### Current validation posture

Do not undertake a broad repair merely to make every historical exploratory component compatible. Record the issue and continue using the current validated path where possible.

---

## 2026-09-27 — Validation vs Production

### Observation

Several existing components are useful for answering narrow validation questions.

### Lesson

A successful validation component does not automatically deserve production status.

### Production requirement

Every candidate production component should have an explicit role, contract, inputs, outputs, persistence model, and relationship to process control.

---

## 2026-09-27 — C Output Boundary

### Observation

The Library Card is intended to be the formal C→D interchange boundary.

### Production requirement

C must produce a complete, self-sufficient representation of the original materials. The representation cannot depend on hidden C implementation state to understand what was processed.

---

## 2026-09-27 — Source Information Preservation

### Observation

The project repeatedly encounters information that is useful but not yet fully interpretable.

### Lesson

Residual information is not failure.

### Production requirement

Source values, source context, residual evidence, and processing provenance must survive even when current interpretation is incomplete.

---

## 2026-09-27 — Human and Machine Inspection

### Observation

CSV has repeatedly been useful because it is both machine-readable and directly inspectable by a person.

### Project rule

Whenever a machine-readable processing/control artifact is created during development, provide a paired human-readable representation.

This remains a development requirement until/unless a later human interface provides an equivalent inspectable representation.

---

# Production Model — Open Issues / Omissions

| ID | Type | Finding | Production requirement | Status |
|---|---|---|---|---|
| PM-001 | Architecture | Exploratory components have accumulated without a single production forest model | Design production C separately from validation machinery | OPEN |
| PM-002 | Interface | Unified source inventory conflicts with legacy two-file inventory consumers | Establish one explicit production source-inventory contract | OPEN |
| PM-003 | Architecture | Directory hierarchy has source-specific meanings | Generic directory evidence + source-specific interpretation | OPEN |
| PM-004 | Completeness | C must represent the entire source, not merely successfully decoded values | Set-level completeness validation | OPEN |
| PM-005 | Preservation | Uninterpreted information must survive processing | CORE/ASSOCIATED/RESIDUAL plus residual evidence | OPEN |
| PM-006 | Process control | Source changes and processing-rule changes are different causes of reprocessing | Durable dependency/change model | OPEN |
| PM-007 | Human interface | Machine processing state should remain inspectable by humans | Common machine/human state representation | OPEN |
| PM-008 | Production boundary | Library Card must not depend on C implementation internals | Stable public C→D contract | OPEN |

---

# Validation Log

Use this section for each validation run:

```text
Date:
Source:
Scope:
Source state/baseline:
Rules/control version:
Processing implementation version:
Records/objects in:
Records/objects represented:
Work items:
Failures:
Exceptions:
CORE:
ASSOCIATED:
RESIDUAL:
Unaccounted:
Idempotence result:
Human inspection result:
Machine validation result:
Issues discovered:
Production implications:
```

