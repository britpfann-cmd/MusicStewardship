# Source Collection Maintenance and Processing History

Status: Deferred architecture
Recorded: 2026-10-08

## Original objective

MusicStewardship should eventually manage a collection by accepting
a source-directory root and recursively processing its contents.

TangoDJ Smart Directory was discussed as an example of the desired
ongoing collection-maintenance capability.

## Existing foundations

- Deterministic recursive source-tree discovery.
- Preservation of files, directories, empty directories, and non-audio material.
- Explorer Tree CSV representation of observed hierarchy.
- Source-specific interpretation and provenance.
- Rosetta processing logs and unchanged-input idempotence.
- Library Cards and CatalogedInstances.
- Transactional catalog reconciliation.

## Deferred collection-maintenance capabilities

- Rescan managed source roots.
- Compare successive source inventories.
- Identify additions, removals, modifications, and possible relocations.
- Selectively process changes without duplicating existing results.
- Present changes and proposed actions for human review.
- Preserve previous observations and decisions.

These are requirements, not claims of completed implementation.

## Git-like processing history

Maintain distinct histories:

1. Source history: what was observed and when.
2. Processing history: transformations, inputs, rules, and versions.
3. Instance and catalog history: interpretations, associations, and decisions.

Preserve original evidence. Later interpretations must not overwrite it.

## Reporting and persistence

CSV and JSON were used as inspectable processing records.
Excel review workbooks were contemplated as a human interface.

Database persistence was deliberately deferred during early development.
A database should support, not replace, inspectable evidence and reports.

## Verification status

Demonstrated:
- Deterministic repeated source-tree discovery.
- Rosetta idempotence for unchanged inputs.
- Transactional provisional-recording reconciliation.

Not yet verified:
- Successive inventory comparison.
- Add/remove processing across runs.
- Relocation detection.
- Complete historical reconstruction.

## Current development decision

Do not implement a new change-tracking subsystem now.

Continue C/D development using existing source-tree and interpretation
components. Preserve source hierarchy, original observations, provenance,
transformation versions, and separate histories.

Inspect existing C interfaces before modifying hierarchy processing.

Guiding principle:
Preserve existing work, verify capabilities, and implement only genuine gaps.
