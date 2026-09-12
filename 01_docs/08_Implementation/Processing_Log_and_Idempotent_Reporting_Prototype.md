# Processing Log and Idempotent Reporting Prototype

## Design intent

The Rosetta engine is responsible for producing processing-state data while it runs. Human reports are summaries/views of that data. The workbook is therefore a prototype presentation layer, not the authoritative processing store.

The prototype deliberately keeps source-specific TTT grammar in CSV control files. The engine supplies generic operations, deterministic work-item identity, input fingerprinting, status/checkpoint data, durable observations, and report generation.

## Work item and restart behavior

A work item is one source record processed by one Rosetta rule. Its identity is derived from source identity, source record/path, and rule ID. The input value is fingerprinted.

On a repeat run, a work item is skipped when the same work-item ID is already `COMPLETE` and its input fingerprint has not changed. Thus a repeat run processes only incomplete or changed work items. `--force` explicitly requests reprocessing.

This is the prototype's idempotent/restartable behavior. It is not yet full dependency-aware invalidation: later work will need to mark dependent items stale when source data, rules, or upstream results change.

## Processing data

`processing_log.csv` contains one state record for each attempted work item, including run ID, deterministic work-item ID, source/rule identity, input fingerprint, status, attempt, timestamps, observation count, exception, and engine/Rosetta versions.

`observations.csv` contains the source observations produced by successful processing. Source values and rule provenance remain attached.

The CSV representation is intentionally simple and inspectable. The eventual production implementation can place these conceptual records in a database without changing the processing model.

## Human workbook

`report_ttt_run.py` summarizes the processing data into an Excel workbook with pages:

- **Run Summary** — high-level operational status.
- **Processing Status** — current state of work items.
- **Rule Statistics** — rule-level activity and observation counts.
- **Information Classes** — CORE / ASSOCIATED / RESIDUAL distribution.
- **Review Queue** — non-complete work items.
- **Observations** — detailed emitted observations.
- **Residual** — residual items available for further analysis.

Additional report types can later be added as views over the same processing data.

## Proof-of-concept acceptance

For the 12-record TTT regression sample, the first run processed 313 work items and emitted 349 observations. A second identical run processed 0 work items and skipped all 313 completed work items. This demonstrates restart/idempotence and report generation without requiring a database yet.
