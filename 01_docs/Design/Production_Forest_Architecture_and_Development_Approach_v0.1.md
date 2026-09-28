# MusicStewardship — Production Forest Architecture and Development Approach

**Status:** Working architecture direction  
**Revision:** 0.1  
**Date:** 2026-09-27

## 1. Purpose

This document records the change in development posture adopted on 2026-09-27.

The project has accumulated a number of useful source-specific, processing, validation, and diagnostic components. These components have been valuable for discovering requirements and proving individual capabilities. They are not, however, presumed to constitute the final production architecture.

The project will now be managed as a **forest rather than as a collection of individually cultivated trees**.

> **Validation work discovers and demonstrates the requirements of the production system. It is not presumed to be the production system.**

## 2. Immediate Objective

Finish validation of the C/source-processing layer with the minimum additional disturbance necessary.

During validation:

- preserve successful demonstrations;
- record errors and omissions;
- record interface problems;
- record architectural observations;
- avoid polishing exploratory components merely because they exist;
- avoid converting every validation artifact into a production dependency.

## 3. Production Model

The eventual production architecture is expected to provide a coherent system around these major concerns:

```text
SOURCE STATE
     │
     ├── source identity
     ├── complete source hierarchy
     ├── source objects
     ├── native metadata/evidence
     └── change state
            │
            ▼
PROCESS CONTROL
     │
     ├── scope
     ├── rules/control
     ├── work items
     ├── dependencies
     ├── checkpoints
     ├── exceptions
     └── reprocessing triggers
            │
            ▼
GENERIC PROCESSING
     │
     ├── source-specific knowledge
     ├── reusable transformations
     ├── evidence preservation
     └── processing outcomes
            │
       ┌────┴────┐
       ▼         ▼
   LIBRARY     CATALOG/
   ENTRIES     HISTORY
       │
       ▼
   DJ LIBRARY
       │
       ▼
   DJ OUTPUTS
       │
       ▼
   PROVENANCE
```

The exact production component boundaries will be designed after the validation evidence has been collected.

## 4. Library Boundary

C must produce a complete and self-sufficient representation of the original source materials sufficient for later catalog construction.

At minimum, the resulting representation must permit:

- complete source-item coverage;
- identification of each represented item;
- preservation of source identity and location;
- preservation of source-native evidence;
- preservation of residual information;
- reconstruction of how source-derived information was obtained.

The Library Card remains the formal C→D interchange boundary unless later architecture work establishes a better explicit public contract.

## 5. Source Environment Is Evidence

Directory hierarchy is part of source evidence. It is not embedded audio metadata and must not be treated as if it were.

The C chain therefore has to demonstrate:

```text
source filesystem
    ↓
source inventory
    ↓
directory context
    ↓
source-specific interpretation
    ↓
record-level result
    ↓
Library representation
```

Different source families may assign different meanings to directory levels. Those meanings belong in source-specific controls/rules; the capability to preserve and carry directory evidence belongs in the generic processing architecture.

## 6. Production-vs-Validation Rule

For every component encountered during validation, ask:

> **Will the future production processing system need this capability, this data, or this contract?**

If yes, capture the requirement and consider the component for later promotion.

If no, retain it as validation evidence or allow it to remain disposable.

Do not allow exploratory implementation history to dictate production architecture.

## 7. Development Sequence

### Phase A — Finish C validation

Validate:

1. source inventory/state capture;
2. source-tree hierarchy preservation;
3. source-specific interpretation;
4. generic transformation execution;
5. processing outcomes;
6. Library Card production;
7. complete source coverage;
8. residual/evidence preservation;
9. repeatability/idempotence;
10. change/reprocessing behavior to the extent already supported.

### Phase B — Design the production C system

Use the validation notebook and issues/omissions record as design input.

Design the production system from requirements and contracts rather than by accumulating more local fixes.

### Phase C — Build the initial Library

Run the production C system against the selected source collections and produce the initial Library representation.

### Phase D — Build DJ outputs

Derive DJ-oriented representations from the Library rather than making DJ output the source of truth.

### Phase E — Expand provenance processing

Apply the provenance architecture after the Library and C/D boundaries are stable enough to support it.

## 8. Relationship to Existing Architecture Documents

This is an architectural direction amendment. It does not invalidate the established requirements for:

- process control;
- source-first preservation;
- reusable transformation functions;
- declarative source knowledge;
- completeness testing;
- non-destructive processing;
- machine/human common state;
- Library Card interchange.

Those existing documents remain useful foundations. This document changes the development posture: exploratory validation artifacts are evidence for the production design, not automatic production components.

## 9. Working Principle

> **Manage the forest. Cultivate individual trees only when doing so advances the forest.**

