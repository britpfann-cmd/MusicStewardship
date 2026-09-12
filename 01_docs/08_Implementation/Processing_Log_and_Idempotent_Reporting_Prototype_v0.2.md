# Processing Log and Idempotent Reporting Prototype v0.2

## Purpose

This prototype demonstrates a version-isolated processing implementation in which the engine emits durable processing data while it runs, completed work is safely skipped on an identical repeat, and human reports are generated as summaries of that same processing data.

## Repository layout

- `08_tools/ingestion/prototype/v0.2/` — executable engine, TTT Rosetta controls, fixtures, and report builder.
- `06_runtime/processing/prototype/v0.2/runs/<run-id>/` — execution state, observations, and reports.
- `07_tests/ingestion/test_processing_idempotence_v02.py` — pytest proof of repeat-run behavior.

The runtime tree is deliberately outside `08_tools`; processing state is operational evidence, not source code.

## Idempotent work

A work item is one source record × Rosetta rule. Its deterministic identity is based on source identity, source record/path, and rule ID. The input value is fingerprinted. An identical repeat skips a completed work item; changed input or `--force` causes reprocessing.

This v0.2 prototype is not yet dependency-aware invalidation. Later versions will need stale-state propagation when source, rules, or upstream results change.

## Reporting

The engine records processing state and observations during execution. `report_ttt_run.py` summarizes those data into a workbook with operational, rule, coverage, review, observation, and residual views. The workbook is a human-facing projection, not the authoritative processing store.

## Prior POC evidence

The previous small demonstration is preserved as run `POC1` under the v0.2 runtime tree. It contains the processing log, observations, and workbook generated from the 12-record TTT regression sample.
