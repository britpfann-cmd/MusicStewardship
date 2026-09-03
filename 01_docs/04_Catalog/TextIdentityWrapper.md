# MusicStewardship Text Identity Wrapper Specification

## 1. Purpose

The Text Identity Wrapper is a reusable intake-stage utility for processing textual identity fields such as person, orchestra, composer, singer, publisher, and related names.

It separates three distinct things:

1. **Original text** — exactly what the source supplied.
2. **Corrected text** — deterministic mechanical correction of the supplied text.
3. **Canonical identity** — the current best-known identity established through the Names/authority system.

The wrapper prepares these values for the ingestion process. It does not write to the database and does not replace the source evidence.

---

## 2. Role in the Ingestion Architecture

The wrapper operates between source-specific transformation and authoritative storage.

```text
source data
    |
    v
source-specific transformation
    |
    v
Text Identity Wrapper
    |
    +--> original_text
    |
    +--> corrected_text
    |
    +--> canonical identity
    |
    v
ingest record
    |
    v
authority / Names system

The wrapper is therefore a preparation and interpretation component, not a database component.

Source-specific responsibilities such as extracting fields from filenames, paths, CSV columns, or source-specific metadata remain outside the wrapper.

## 3. Processing Pipeline

For each input value, processing follows this sequence:

```text
original source value
        |
        v
preserve original
        |
        v
mechanical text correction
        |
        v
corrected text
        |
        v
Names / authority lookup
        |
        +--> established identity
        |
        +--> provisional identity
        |
        +--> unresolved

```

The processing pipeline must be deterministic for the same input and authority state.

## 4. Text Evidence Model

The wrapper maintains the distinction between evidence and interpretation.

### Original text

The original value is immutable source evidence.

It must not be silently changed, normalized, or discarded.

### Corrected text

Corrected text represents deterministic treatment of the original value.

Examples include:

Unicode normalization;
repair of recognizable mojibake;
normalization of inappropriate Unicode punctuation;
normalization of repeated or surrounding whitespace.

Mechanical correction does not by itself establish identity.

### Canonical identity

Canonical identity represents the current interpretation supplied by the authority system.

Canonical identity may change as the authority system develops without changing the original source evidence.

For ordinary data manipulation:

canonical -> corrected -> original

For provenance and audit:

original -> corrected -> canonical
## 5. Deterministic Text Correction

Mechanical correction should use established Unicode and text-processing libraries rather than implementing Unicode rules from scratch.

The wrapper may perform deterministic corrections such as:

Unicode normalization;
recognizable mojibake repair;
punctuation normalization where explicitly defined;
leading/trailing whitespace removal;
replacement of repeated spaces or tabs with a single space.

For example:

"  Carlos   Di  Sarli  "
        |
        v
"Carlos Di Sarli"

A correction must be recorded when it changes the supplied value.

The original value remains unchanged.

Text correction must not attempt to infer historical identity or resolve ambiguous names through heuristics alone.

## 6. Identity and Authority Resolution

After deterministic correction, the corrected value is presented to the Names/authority layer.

Three outcomes are supported.

### Authorized identity

An established authority record exists.

canonical_ref    = existing authority reference
canonical_name   = current canonical name
canonical_status = AUTHORIZED
### Provisional identity

No established authority exists, but the evidence is sufficient to create or reuse a provisional identity.

canonical_ref    = provisional reference
canonical_name   = corrected text
canonical_status = PROVISIONAL
### Unresolved identity

The evidence is insufficient to establish an identity.

canonical_ref    = null
canonical_name   = null
canonical_status = UNRESOLVED

The intake result retains the original and corrected values regardless of the authority result.

## 7. Names Adapter Boundary

The wrapper should interact with the Names system through a defined adapter interface.

The adapter is responsible for:

looking up an existing name;
returning its authority status;
returning its canonical name and reference;
creating or reusing a provisional identity when appropriate;
preserving the identity reference when a provisional identity later becomes authorized.

The wrapper should not implement the Names database schema.

The current test adapter is a mock implementation used to verify this interface. It is not the production authority database.

A provisional identity must retain its reference when its authority status changes.

Example:

```text
PROV-0004
    |
    +--> PROVISIONAL
    |
    +--> AUTHORIZED

```

The identity reference remains PROV-0004.

## 8. Processing Output Contract

The default processing interface is line-oriented UTF-8 input from standard input.

The machine-readable output is JSON Lines (JSONL), with one result object per input record.

Each result contains, at minimum:

record
original_text
corrected_text
correction_applied
corrections
canonical_ref
canonical_name
canonical_status
authority_source

The exact intake storage format is a separate concern and will be defined by the intake contract.

The wrapper writes no database records.

UTF-8 output must be explicit so that non-ASCII names are preserved correctly when the output is redirected to a file or passed to another program.

## 9. Diagnostics

Diagnostics must never corrupt the machine-readable output stream.

Machine-readable results go to standard output.

Human-readable diagnostics go to standard error or a separate diagnostic stream.

Diagnostics may report:

record number;
original value;
corrected value;
whether correction occurred;
corrections applied;
authority lookup result;
canonical reference;
canonical status;
authority source;
warnings or ambiguity.

Example:

```text
record=7
original='Miguel CalÃ³'
corrected='Miguel Caló'
changed=yes
status=AUTHORIZED
corrections=ftfy Unicode/mojibake repair
```

## 10. Human Review Model

The purpose of processing at scale is not to require human inspection of every record.

Routine records should pass through automatically when deterministic correction and authority resolution provide sufficient confidence.

Human attention should increasingly be concentrated on exceptions.

Typical review candidates include:

unresolved identities;
provisional identities awaiting authority;
ambiguous results;
explicitly flagged corrections;
other conditions designated by the processing rules.

The processing results remain the source for all report views. Human review does not create a separate source of truth.

## 11. Report Views

The reporting layer provides progressively different levels of information for human use.

### Summary

The Summary view answers:

How did the processing run?

It provides aggregate information such as:

total records;
authorized records;
provisional records;
unresolved records;
records whose text changed;
correction statistics;
records requiring review.
### Concise

The Concise view answers:

What happened to the records?

It provides a compact record-level representation suitable for large result sets without exposing every processing detail.

### Full

The Full view answers:

What exactly happened to this record?

It contains the complete processing and provenance information needed to understand the result, including original text, corrected text, corrections, canonical identity, authority information, and review information.

### Problems

The Problems view answers:

What requires human attention?

It contains only records requiring review.

The Problems view is intended to become the primary human-review workspace as processing scales.

The four views are presentations of the same processing results. They are not separate datasets.

### Summary
   |
   v
### Concise
   |
   v
### Full
   |
   v
### Problems

The Full view must preserve sufficient information to explain how a Problems record was produced and to support subsequent human review.

## 12. Scope and Non-Goals

The wrapper does not:

write to the database;
rewrite source files;
silently replace original values;
determine historical identity solely from text heuristics;
perform source-specific field extraction;
determine source-specific mappings;
define the Names database schema;
replace the authority system.

Source-specific transformation belongs in the ingest transformation layer.

Authority decisions belong in the Names/authority system.

The wrapper prepares evidence and current interpretation between those layers.

## 13. Design Principles
### Preserve evidence

Original source text is never discarded or silently replaced.

### Separate correction from identity

Mechanical text correction and identity determination are different operations.

### Prefer authority over heuristics

Canonical identity comes from the authority system rather than from increasingly elaborate text-matching rules in the wrapper.

### Make processing inspectable

Every transformation that changes text should be identifiable in the processing result.

### Keep machine output clean

Machine-readable output and human diagnostics must remain separate.

### Scale human attention

The objective of the pipeline is to automate routine cases and concentrate human effort on Problems.

### Keep components replaceable

The wrapper, ingest engine, Names authority system, and reporting layer have distinct responsibilities and should remain independently replaceable.

The wrapper prepares evidence and current interpretation; the ingest engine stores it; the authority system determines current meaning; the reporting layer directs human attention to what needs review.
