# Crackling Tunes Rosetta Stone

**Status:** Research-derived source transposition specification  
**Source:** Crackling Tunes curated releases  
**Reference crosswalk:** TANGO-DJ.AT Crackling Tunes result set  
**Purpose:** Define the source-specific extraction, decomposition, and cross-reference rules needed to convert Crackling Tunes material into MusicStewardship reference-catalog data.

## 1. Core finding

For the Crackling Tunes material examined, the combination of:

```text
CTMM release identifier + Crackling Tunes catalog/side/take identifier
```

provides a deterministic correspondence to the TANGO-DJ.AT recording row for the same release and track position.

The test comprised 558 Crackling Tunes audio files across 54 releases. The supplied TANGO-DJ snapshot contained 53 Crackling Tunes release identifiers. CTMM2106 and CTMM2512 were absent from that snapshot, accounting for 16 source files. The other 542 files matched a TANGO-DJ row by release + track position after missing Crackling catalog identifiers were recovered from filenames.

This is an **identity cross-reference rule for this curated source**, not a universal assumption about other sources.

## 2. Source preservation principle

The translator shall preserve the original Crackling Tunes values. Standardized values are derived outputs.

A complete source snapshot should be retained as the historical breadcrumb trail. The operational reference record may retain a source-snapshot identifier and source-row reference rather than duplicating every source value.

> **Extract facts; preserve evidence.**

The MusicStewardship ingestion framework treats COPY, RENAME, STANDARDIZE, DECOMPOSE, COMBINE, LOOKUP, EXTRACT, PATH_EXTRACT, DERIVE, REFERENCE, IGNORE, and SOURCE_CONTEXT as distinct transformation types.

## 3. Release identification

### Input

Crackling Tunes release names such as:

```text
21.08 Releases
22.01 Releases
25.10 Releases
```

### Rule

```text
YY.MM Releases → CTMMYYMM
```

Examples:

```text
21.08 Releases → CTMM2108
22.01 Releases → CTMM2201
25.10 Releases → CTMM2510
```

**Operation:** DERIVE

**Confidence:** Very high for this Crackling Tunes collection.

## 4. Crackling Tunes source recording identifier

Prefer the embedded `CATALOG #` value.

If it is absent, extract the CT identifier from the filename.

Examples:

```text
[CT2302-A1] → CT2302-A1
(CT2302-B1) → CT2302-B1
[CT21001-A2] → CT21001-A2
```

**Operations:** EXTRACT / fallback EXTRACT

**Priority:**

1. Embedded `CATALOG #`
2. Filename CT identifier
3. Blank if neither is available

The original filename remains source evidence.

## 5. Compound CT identifier decomposition

A common CT identifier:

```text
CTnnnn-A1
CTnnnn-B1
CTnnnn-A2
CTnnnn-B2
```

can be decomposed into:

```text
source_catalog_id
source_side
source_take_designation
```

For the monthly Crackling Tunes release structure observed in this dataset, the sequence corresponds to release track position:

```text
-A1 → track 1
-B1 → track 2
-A2 → track 3
-B2 → track 4
...
```

Formula:

```text
track = (take - 1) * 2 + side_position
```

where:

```text
A = 1
B = 2
```

**Operations:** DECOMPOSE / DERIVE

**Confidence:** Very high for the tested releases. Validate independently before applying this rule to another source.

## 6. ARTIST decomposition

Observed dominant Crackling Tunes forms:

```text
Ensemble / Singer
Ensemble / Instrumental
Ensemble / Singer / Singer
```

### Rule

Split `ARTIST` on `/`.

The first component is an **ensemble candidate**.

Remaining components are interpreted as either:

- `Instrumental` / `Instr.` → instrumental status
- one or more performer/singer candidates → vocal participant(s)

Examples:

```text
Francisco Canaro / Charlo
    → ensemble = Francisco Canaro
    → singer = Charlo

Juan D'Arienzo / Instr.
    → ensemble = Juan D'Arienzo
    → instrumental = true

Canaro / Agustin Irusta / Roberto Fugazot
    → ensemble = Canaro
    → singer candidates = Agustin Irusta; Roberto Fugazot
```

This is a **source interpretation for matching and canonicalization**. Preserve the original ARTIST string.

**Operation:** DECOMPOSE

**Confidence:** High for the dominant two-component pattern; multiple-participant cases remain source conventions until independently validated.

## 7. ALBUMARTIST interpretation

Observed values include:

```text
Canaro, Francisco [Orquesta]
Firpo, Roberto [Cuarteto]
Lauro, Francisco [Sexteto]
Pirincho [Quinteto]
```

Treat the complete value as the source's recording-artist/ensemble assertion.

The bracketed designation is useful evidence of ensemble type.

Do not automatically infer that the named person was historically the leader solely from this field.

**Operations:** COPY; optional DECOMPOSE for analytical use

**Confidence:** High as a source assertion.

## 8. Title handling

Crackling Tunes titles can contain accents, punctuation, alternate-title parentheses, and restoration/transfer annotations such as `(435Hz)` or `(440Hz)`.

For comparison:

- normalize case, accents, and punctuation;
- remove frequency annotations from the comparison form;
- preserve alternate-title text;
- never overwrite the original source title.

Examples:

```text
El trece (El 13) (435Hz)
El trece (El 13)

Así es el mundo 435Hz
Así es el mundo
```

These normally represent the same underlying recording when the independent evidence agrees.

**Operation:** STANDARDIZE for comparison only; preserve original.

## 9. Recording date

When a date is present in the filename, it can be extracted from:

```text
DD_MM_YYYY
```

Examples:

```text
17_10_1928 → 1928-10-17
03_12_1936 → 1936-12-03
```

A year-only date remains year-only.

Date differences between sources shall be retained as evidence rather than silently corrected.

**Operations:** EXTRACT / STANDARDIZE

## 10. Identifier namespaces

Crackling Tunes CT identifiers and TANGO-DJ historical catalog numbers are **different namespaces**.

Example:

```text
Crackling Tunes:
CT1874-A1

TANGO-DJ:
historical catalog number
matrix number
```

Both should be retained; they should not be scored as literal identifier disagreement.

**Operation:** REFERENCE / SOURCE_CONTEXT

## 11. TANGO-DJ cross-reference

For the tested collection:

```text
CTMM release + source track position
        ↓
TANGO-DJ record
```

This yielded 542/542 correspondence for all tracks whose releases existed in the supplied TANGO-DJ snapshot.

Retain the TANGO-DJ `ref` identifier as an external reference. Do not substitute it for the MusicStewardship internal reference identity.

**Operation:** REFERENCE

## 12. Matching evidence hierarchy

For this curated source:

1. CTMM release
2. Crackling CT catalog/side/take identifier
3. derived track position
4. title
5. recording date
6. ensemble
7. singer(s)
8. TANGO-DJ catalog/matrix information
9. future acoustic evidence, if needed

For established curated collections, automatic confidence may be very high. Text discrepancies should normally become **field-level reconciliation issues**, not identity failures.

## 13. Exceptions

### Missing TANGO-DJ release

The supplied snapshot lacked:

```text
CTMM2106
CTMM2512
```

Treat these as unresolved against that snapshot, not as source errors.

### Missing embedded Crackling catalog number

Recover from the filename whenever the CT pattern is unambiguous.

### Conflicting assertions

Do not collapse conflicting source values into one value. Preserve the source assertions and their provenance.

## 14. Recommended reference-catalog information

A Crackling-derived reference record should be able to carry:

```text
reference_record_id
source
source_snapshot
source_row

source_release
source_file
source_audio_format
source_catalog_id
source_track_number

source_artist
source_albumartist
source_title
source_date

ensemble_candidate
singer_candidates
instrumental

tango_dj_reference
tango_dj_release
tango_dj_track_number
tango_dj_title
tango_dj_artist
tango_dj_recording_date
tango_dj_catalog_number
tango_dj_matrix_number
```

The exact canonical schema remains a separate design decision. This document specifies the source translation and reconciliation behavior.

## 15. Implementation

This is a **source-specific Rosetta Stone**, not a new source-specific transformation program.

Intended flow:

```text
Crackling Tunes
      ↓
complete source snapshot CSV
      ↓
Crackling Tunes mapping / Rosetta Stone
      ↓
generic transformer
      ↓
validated reference-catalog data
      ↓
TANGO-DJ reference linkage
```

The mapping is version-controlled and inspectable so a future correction can change interpretation without losing the original source snapshot.

## 16. Research conclusion

The Crackling Tunes experiment demonstrates that an established curated collection can be imported largely by **structural correspondence rather than fuzzy identity resolution**.

The preferred pattern is:

> **Exploit the source's own structure and established identifiers first; use text interpretation to reconcile representations; reserve acoustic matching for the genuinely unresolved residue.**
