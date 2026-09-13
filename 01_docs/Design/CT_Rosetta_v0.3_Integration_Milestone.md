# MusicStewardship — Crackling Tunes Rosetta Integration Milestone

**Date:** 2026-09-13  
**Status:** Milestone checkpoint  
**Working area:** `99_sandbox/CT_Rosetta_Test_20260913`

## Purpose

Record the first successful integration of the previously developed Crackling Tunes source-transition representation with the generic MusicStewardship Rosetta execution engine.

This checkpoint records demonstrated behavior. It does not promote the sandbox test artifacts into production.

## Test Fixture

The historical Crackling Tunes transition fixture was recovered from the parent of commit `1b0fa419f4707689ae7d8371250255bd8f64e2dd`:

- `crackling_21.08_text_v2.csv` — field-level source transition
- `crackling_source_tracks.csv` — previously derived, one-row-per-source-audio-file transition

The recovered source-track transition contains:

- 558 source-file rows
- 54 monthly-release identifiers
- 556 rows with CT catalog identifiers
- 556 rows with source track numbers
- 558 rows with source dates
- 522 rows with ensemble candidates
- 280 rows with singer candidates
- 227 rows marked instrumental

All 556 populated CT identifiers in this fixture conform to the expected `CT...-[AB][take]` pattern.

## Integration Approach

The historical Crackling Tunes semantic transition was adapted into the current Rosetta engine input representation without changing the generic engine.

The test deliberately treated previously derived CT fields as source-specific interpretation already established upstream. The generic engine then handled source observation processing, rule execution, source-value preservation, rule provenance, information-classification, durable processing state, and repeat-run idempotence.

The test did not attempt to reimplement CT parsing inside the generic engine.

## Engine and Mapping

Generic engine:

`08_tools/ingestion/rosetta_engine.py`

CT test mapping:

`99_sandbox/CT_Rosetta_Test_20260913/input/CT_to_MusicStewardship_Rosetta_v0.3_test.csv`

CT test bindings:

`99_sandbox/CT_Rosetta_Test_20260913/input/ct_engine_bindings_v0.3.csv`

The mapping was adjusted during integration to respect the demonstrated engine contract:

- unsupported arithmetic derivation was removed from the integration test
- source-derived release-track position was consumed as an already-established transition value
- CT catalog/side/take components were consumed as source-derived values
- filename CT identifier fallback was excluded from this integration run so primary transition data was not confused with fallback extraction
- source-element names were aligned exactly with the binding table

## First Run Result

Run ID:

`CT-V03-INTEGRATION`

| Measure | Result |
|---|---:|
| Source rows | 558 |
| Work items processed | 8,725 |
| Failed work items | 0 |
| New observations | 8,203 |
| CORE observations | 2,786 |
| ASSOCIATED observations | 4,422 |
| RESIDUAL observations | 0 |

The 8,725 work items are source/rule processing units. The 8,203 observations are emitted observations. The difference is expected because a rule can be processed without emitting an observation for every source/rule combination.

## Repeat-Run Result

Run ID:

`CT-V03-REPEAT`

The same source, rules, bindings, and state directory were processed again.

| Measure | Result |
|---|---:|
| Source rows | 558 |
| Work items processed | 0 |
| Work items skipped | 8,725 |
| Failed work items | 0 |
| New observations | 0 |
| Existing observation rows | 8,203 |
| Unique source/rule/value combinations | 8,203 |

The repeat run demonstrated idempotent processing with no duplicate observations added.

## What This Milestone Demonstrates

### 1. The generic Rosetta engine can process a second materially different source

The same execution engine used for TTT successfully consumed a Crackling Tunes-specific rule and binding profile.

### 2. The earlier Crackling Tunes CSV transition approach remains useful

The historical CT transition can serve as a source-specific interpretation layer feeding the generic observation engine.

### 3. Source-specific grammar belongs outside the generic engine

CT parsing knowledge remains in CT-specific transition/profile artifacts. The engine remains responsible for generic execution, durable evidence, and restartability.

### 4. Provenance survives the transition

The engine output records source value, rule identifier, information class, operation, target, and evidence basis for each observation.

### 5. Work-item processing and emitted observation counts are distinct concepts

A processed source/rule work item need not emit an observation. That distinction should remain explicit in future reporting.

## Not Yet Demonstrated

This milestone does **not** establish success for:

- raw Crackling Tunes field-level transition processing directly through the generic engine
- CT filename catalog-identifier fallback when embedded catalog data is absent
- full CTMM + track reconciliation against TANGO-DJ
- external reference metadata ingestion
- conflict and residual-source assertions
- promotion of CT source representations into canonical MusicStewardship entities
- production graduation of the CT mapping or sandbox artifacts

These should remain separate follow-on tests.

## Architectural Significance

The experiment supports the working pattern:

```text
Source-specific source material
        ↓
Source-specific transition / interpretation
        ↓
Generic Rosetta engine
        ↓
Durable observations + provenance + processing state
        ↓
Later reconciliation / promotion
        ↓
Canonical catalog
```

This is consistent with the current MusicStewardship design principle:

> Preserve source representations at their native precision; promote them into canonical catalog structure when the evidence supports it.

## Sandbox / Graduation Status

The test artifacts remain in `99_sandbox` and are not yet production artifacts.

The next work should be deliberate:

1. document the successful integration;
2. extract reusable engine/profile improvements from the experiment;
3. add focused regression tests for CT fallback and reconciliation behavior;
4. only then graduate proven artifacts into the appropriate production directories.

## Milestone Conclusion

**Crackling Tunes has passed the first generic Rosetta-engine integration test using the recovered 558-row historical transition fixture.**

The engine completed all 8,725 work items with zero failures, emitted 8,203 provenance-bearing observations, and demonstrated a clean idempotent repeat run with zero additional observations.

This establishes a baseline integration milestone, but not production readiness for the full Crackling Tunes ingestion pipeline.
