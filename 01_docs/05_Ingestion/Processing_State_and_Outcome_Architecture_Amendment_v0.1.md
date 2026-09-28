# Processing State and Outcome Architecture Amendment v0.1

**Status:** Proposed architecture amendment
**Date:** 2026-09-27
**Scope:** Generic ingestion / Rosetta processing / reporting

## 1. Purpose

This amendment separates three dimensions that had previously been conflated in processing observations:

1. information classification;
2. processing outcome;
3. reason for an unresolved or otherwise notable outcome.

The distinction is required so that preservation of source information is not reported as processing failure.

## 2. Orthogonal dimensions

### Information class

Describes the role or disposition of information:

- `CORE`
- `ASSOCIATED`
- `RESIDUAL`

### Processing outcome

Describes what the processor did with the information:

- `DECODED`
- `DERIVED`
- `PRESERVED`
- `NOT_ATTEMPTED`
- `PARTIAL`
- `UNDECODABLE`
- `CONFLICT`
- `REVIEW`

### Outcome reason

Provides the reason when an outcome requires explanation:

- `OUT_OF_SCOPE`
- `NO_CAPABILITY`
- `DECODER_FAILURE`
- `AMBIGUOUS`
- `CONFLICTING_EVIDENCE`
- `HUMAN_REQUIRED`
- `PRESERVATION`
- `OTHER`

The enumerations are an initial controlled vocabulary and may be extended as additional sources demonstrate a need.

## 3. Architectural rule

> **Information classification, processing outcome, and outcome reason are independent dimensions.**

In particular:

> **`RESIDUAL` does not mean processing failure.**

Residual information may result from deliberate non-processing, lack of current capability, incomplete interpretation, ambiguity, or other circumstances.

## 4. Preservation is normal

The system is non-destructive. Retention of the original source representation is expected behavior.

Preservation should therefore not itself generate an exception or review condition.

For example:

```text
source catalog value
        |
        +-- DECODED  -> record = 7160-A
        |
        +-- DECODED  -> matrix = 9326
        |
        +-- DECODED  -> take = 1
        |
        +-- PRESERVED -> complete original source value
```

The preservation observation documents provenance; it does not indicate unsuccessful decoding.

## 5. Residual reporting

Human reporting shall distinguish at least:

- successfully decoded;
- successfully derived;
- intentionally preserved / not attempted;
- partially processed;
- unable to decode;
- conflicting or ambiguous;
- requiring human review.

A report shall not classify every `information_class=RESIDUAL` observation as an exception.

## 6. Example

For:

`Record: 7160-A, Matrix: 9326,Take: 1`

the meaningful result is:

```text
Information class: ASSOCIATED
Processing outcome: DECODED
Decoded:
    record = 7160-A
    matrix = 9326
    take = 1
Original source value: retained
```

The complete original value may also have a preservation observation. That observation is informational.

## 7. Relationship to process control

This amendment does not replace process-control state such as work-item status, checkpoints, exceptions, dependencies, and reprocessing triggers.

It adds semantic detail to the result of processing.

Process control therefore remains the operational state from which the human interface derives its presentation.

## 8. Reporting principle

The report should emphasize what the processor accomplished and what requires attention.

The existence of preserved source information is normally not remarkable.

Examples:

```text
Successful decoding:
    402 catalog-number components

Source preservation:
    134 original catalog-number values retained

Unable to decode:
    0

Partial:
    0

Review:
    0
```

The exact report categories may evolve, but the distinction between successful processing and preservation must remain.
