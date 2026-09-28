# CT Provisional Transformation Vocabulary v0.1

**Status: PROVISIONAL — CT-derived starting point**

This paired specification abstracts transformation capabilities from the existing CracklingTunes control, field-map, binding, and Rosetta artifacts. It is not yet the final common vocabulary.

## Purpose

The vocabulary describes **processing transformations**, not a master list of source fields. Source-specific profiles state which transformations apply and how the source supplies the required evidence. The downstream processing engine remains source-independent.

## Machine-readable companion

`CT_Provisional_Transformation_Vocabulary_v0.1.csv`

The CSV and this document are one paired controlled artifact.

## Provisional transformations

| ID | Transformation | Applicability |
|---|---|---|
| CT-ST-001 | Establish source identity | REQUIRED |
| CT-ST-002 | Preserve source-relative location | REQUIRED |
| CT-ST-003 | Preserve directory hierarchy as context | REQUIRED |
| CT-ST-004 | Preserve original filename | REQUIRED |
| CT-ST-005 | Extract filename evidence | REQUIRED |
| CT-ST-006 | Copy source title | REQUIRED |
| CT-ST-007 | Decompose compound artist value | REQUIRED |
| CT-ST-008 | Derive an attribute | REQUIRED |
| CT-ST-009 | Represent release relationship | REQUIRED |
| CT-ST-010 | Standardize a source value | REQUIRED |
| CT-ST-011 | Assert source identifier | REQUIRED |
| CT-ST-012 | Corroborate independent evidence | PLANNED |
| CT-ST-013 | Reference external authority | OPTIONAL |
| CT-ST-014 | Preserve residual information | REQUIRED |
| CT-ST-015 | Classify information | REQUIRED |
| CT-ST-016 | Preserve transformation provenance | REQUIRED |

## Findings from the CT evidence

1. CT transformation needs extend beyond field copying.
2. CT controls demonstrate `DECOMPOSE`, `DERIVE`, `REFERENCE`, `STANDARDIZE`, `EXTRACT`, and `ASSERT`.
3. CT Rosetta v0.3 exercises only `COPY`, `EXTRACT`, and `SOURCE_CONTEXT`; therefore the Rosetta file alone is not a complete inventory of CT transformation needs.
4. Directory hierarchy is processing context as well as preserved source evidence.
5. Source-native values remain distinguishable from transformed and derived values.
6. Corroboration is included as **PLANNED**, because the CT field map/control material identifies it as planned rather than completed.
7. This is a provisional processing vocabulary, not a CT domain schema.

## Next application

Apply this checklist to TTT, FromJae, and other source classes. For each transformation classify it as:

- REQUIRED
- OPTIONAL
- NOT APPLICABLE
- MISSING / CAPABILITY GAP
- NOT YET DETERMINED

Additions to the common vocabulary should occur when another source demonstrates a transformation capability not adequately represented here.

## Completion principle

A source-processing scope is complete only when all applicable transformations have been satisfied, required evidence and residual information have been preserved, and the resulting generic representation is valid for downstream processing.
