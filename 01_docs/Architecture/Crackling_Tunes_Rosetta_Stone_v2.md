# Crackling Tunes Rosetta Stone — v0.2

**Status:** Working source-translation specification  
**Purpose:** Apply the established Crackling Tunes source knowledge to the MusicStewardship working model after the TTT catalog-ingestion exercise.  
**Supersedes:** Research-derived Crackling Tunes Rosetta Stone (v0.1) as the active working interpretation; the earlier document remains historical evidence.

## 1. What remains true

The earlier Crackling Tunes work established a strong and reusable pattern:

```text
Crackling Tunes source snapshot
        ↓
source-specific Rosetta Stone
        ↓
generic extraction / transformation engine
        ↓
source representations preserved
        ↓
candidate catalog mappings
        ↓
external-reference mappings
        ↓
validated staging
```

The tested monthly-release structure supports the following source-specific rules:

- release names such as `21.08 Releases` derive to `CTMM2108`;
- an embedded `CATALOG #` value is preferred for the Crackling Tunes source catalog identifier;
- when absent, an unambiguous CT identifier may be extracted from the filename;
- CT identifiers such as `CT2302-A1` can be decomposed into source catalog, side, and take designation;
- for the tested monthly-release structure, the CT suffix sequence gives release-track position;
- the CTMM release plus derived track position gave deterministic correspondence to the supplied TANGO-DJ snapshot for the represented releases tested.

These remain **Crackling Tunes rules**, not universal MusicStewardship identity rules.

## 2. Changes from v0.1 arising from TTT work

### 2.1 Representation is not identity

A source value is first treated as a representation supplied by a source. It may later support an entity identity, but the representation itself is not automatically the entity.

Examples:

```text
source ARTIST string       ≠ Person or Ensemble entity
source TITLE               ≠ automatically a Work identity
source CATALOG #           ≠ automatically a Performance identity
source filename            ≠ Recording identity
```

The original source representation must remain recoverable.

### 2.2 Do not force a source representation into an existing entity level

The TTT exercise showed that one source representation can span multiple musical tracks. For example, a record/matrix representation may describe a source artifact containing several tracks. Therefore a source catalog value should not automatically become a recording key.

Similarly, source medium can vary inside what appears to be a single release. A release may therefore contain both `TT/33` and `TT/78` source representations. The source value should remain attached to the source occurrence unless evidence supports a more general entity relationship.

### 2.3 Promotion is evidence-driven

When a source supplies unusually precise historical information, retain that precision and promote it when the evidence supports doing so.

The pipeline must not reduce a precise source representation merely because another source is less precise.

```text
source representation
        ↓
retained evidence
        ↓
interpretation
        ↓
promotion when justified
```

### 2.4 Historical event vs. recording manifestation

MusicStewardship distinguishes, conceptually, between:

- a **Performance**: a singular historical event;
- a **Recording/Manifestation**: a recording representation or path by which that performance reaches us;
- a **Release**: a publication/edition issued by a publisher or label;
- a **Library Item**: an owned digital or physical artifact.

The Rosetta Stone does not assign these as final ontology categories. It supplies evidence that can participate in those distinctions.

### 2.5 External references are mappings

A TANGO-DJ, Discogs, or other external identifier is retained as an external reference. It does not replace a MusicStewardship internal identity.

## 3. Source preservation rule

Every transformation must preserve enough information to reconstruct the original Crackling Tunes representation and the source context in which it occurred.

A complete source snapshot should remain available as the historical breadcrumb trail.

The preferred pattern is:

```text
source snapshot
    + source row / source file reference
    + original value
    + transformation rule
    + derived value
```

The operational catalog may use the derived value while provenance remains available.

## 4. Release representation

### Input

Crackling Tunes monthly release names such as:

```text
21.08 Releases
22.01 Releases
25.10 Releases
```

### Rule

```text
YY.MM Releases → CTMMYYMM
```

**Operation:** DERIVE  
**Confidence:** Very high for the established Crackling Tunes collection.

The derived `CTMM` value is a source/release identifier candidate. It does not prevent a later canonical Release entity from having additional identifiers, names, editions, or external references.

## 5. Crackling Tunes source catalog representation

Prefer embedded `CATALOG #`.

If it is absent, recover an unambiguous CT identifier from the filename.

Examples:

```text
[CT2302-A1] → CT2302-A1
(CT2302-B1) → CT2302-B1
```

Preserve the complete original value. Do not compare the CT namespace directly to TANGO-DJ historical catalog numbers.

**Operations:** COPY / EXTRACT / fallback EXTRACT

## 6. CT identifier decomposition

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

For the tested monthly-release structure:

```text
-A1 → track 1
-B1 → track 2
-A2 → track 3
-B2 → track 4
...
```

**Operations:** DECOMPOSE / DERIVE  
**Confidence:** Very high for the tested release structure.

This derived track position is a property of the **source representation**, and can be promoted to Release Track when the source structure supports that interpretation.

## 7. Artist representation

Observed dominant forms include:

```text
Ensemble / Singer
Ensemble / Instrumental
Ensemble / Singer / Singer
```

The source ARTIST value is preserved unchanged.

For analysis or candidate mapping:

- first component may be treated as an **ensemble candidate**;
- `Instrumental` / `Instr.` may be interpreted as instrumental status;
- remaining named components may be treated as performer/singer candidates.

These are **candidate interpretations**, not automatic Person/Ensemble entity creation.

**Operation:** DECOMPOSE

## 8. Album artist representation

Values such as:

```text
Canaro, Francisco [Orquesta]
Firpo, Roberto [Cuarteto]
```

should remain source assertions.

The bracketed designation is useful evidence about ensemble type, but should not by itself establish leadership or canonical ensemble identity.

**Operations:** COPY / optional DECOMPOSE

## 9. Title representation

Crackling Tunes titles may include:

- accents;
- punctuation;
- alternate-title parentheses;
- transfer annotations such as `(435Hz)` or `(440Hz)`.

For comparison only:

- normalize case, accents, and punctuation;
- remove transfer-frequency annotations;
- preserve alternate-title text;
- never overwrite the source title.

The comparison form is evidence used to suggest correspondence. It is not itself a replacement for the source representation.

**Operation:** STANDARDIZE for comparison only

## 10. Date representation

A date embedded in a filename may be extracted from:

```text
DD_MM_YYYY
```

Examples:

```text
17_10_1928 → 1928-10-17
03_12_1936 → 1936-12-03
```

A year-only value remains year-only.

Date differences among sources are preserved as source assertions. No silent correction is permitted.

**Operations:** EXTRACT / STANDARDIZE

## 11. Source medium

Values such as `TT/33` and `TT/78` describe source material/representation.

They should not automatically be promoted to a singular Release property because a release can contain more than one such value.

The source-medium assertion should remain associated with the source occurrence from which it was observed until a broader source/manifestation model provides the correct relationship.

## 12. Record / matrix / take information

Crackling Tunes may supply source identifiers with structure analogous to record/side/take representations.

These should be preserved in their original source namespace and may be decomposed into structured components when the grammar is known.

They should **not** automatically become a Performance key or Release key.

The current rule is:

```text
preserve raw source representation
        ↓
optionally decompose
        ↓
use as evidence for source artifact / recording / performance mapping
```

## 13. Matching and identity evidence hierarchy

For established Crackling Tunes curated material, the working hierarchy remains:

1. CTMM release
2. Crackling CT catalog/side/take identifier
3. derived source track position
4. title
5. recording date
6. ensemble representation
7. singer representation
8. TANGO-DJ catalog/matrix information
9. future acoustic evidence, when needed

This hierarchy is evidence weighting for reconciliation, not a universal identity algorithm.

Text discrepancies should normally be treated as field-level reconciliation issues rather than immediate identity failure when the strong source structure agrees.

## 14. Conflicting assertions

Conflicting values from different sources must not be collapsed into one value simply to achieve agreement.

Instead preserve:

```text
source
source snapshot
source row
original representation
interpreted value
```

and allow later reconciliation to determine whether the assertions:

- agree;
- describe different manifestations;
- refer to different performances;
- reflect an edition/reissue difference;
- or remain unresolved.

## 15. Candidate entity promotion

Promotion from representation to entity should be explicit.

Examples:

```text
"Comme il faut"
    → candidate Work

"Canaro, Francisco [Orquesta]"
    → candidate Ensemble representation

CTMM2108
    → candidate Release

CT2302-A1
    → source catalog representation

TT result ref
    → external mapping
```

No promotion is required merely because a representation exists.

## 16. Recommended CSV transition layers

The prior Crackling Tunes transition artifacts remain useful, but their roles should now be understood as distinct layers:

```text
1. COMPLETE SOURCE SNAPSHOT
   One row per source audio representation.

2. SOURCE REPRESENTATION / TRANSFORMATION
   Preserve original values and derived/decomposed values.

3. CANDIDATE ENTITY MAPPING
   Suggest Work / Person / Ensemble / Performance / Release mappings.

4. EXTERNAL REFERENCE MAPPING
   Connect to TANGO-DJ, Discogs, or other source identifiers.

5. VALIDATED CATALOG STAGING
   Present only the promoted interpretations and their provenance.
```

The first layer is historical. The later layers are derivable and may be regenerated as interpretation changes.

## 17. Existing Crackling Tunes artifacts to retain

The following earlier artifacts remain valuable and should be reused rather than discarded:

- complete source snapshot CSVs;
- `crackling_tunes_rosetta.csv`;
- `crackling_catalog_text*.csv`;
- `crackling_source_tracks.csv`;
- `crackling_reference_records.csv`;
- Crackling Tunes ↔ TANGO-DJ comparison/reconciliation CSVs;
- `build_crackling_reference_records*.py`.

They should be treated as research and staging artifacts whose semantics are updated by this working specification rather than as final canonical database tables.

## 18. Generic-engine requirement

Crackling Tunes should be processed by the same generic ingestion engine used for other sources.

A new source-specific behavior belongs in declarative source knowledge wherever practical.

Reusable operations include:

```text
COPY
RENAME
STANDARDIZE
DECOMPOSE
COMBINE
LOOKUP
EXTRACT
PATH_EXTRACT
DERIVE
REFERENCE
SOURCE_CONTEXT
IGNORE
```

A genuinely new transformation technique should be added to the generic engine rather than duplicated as source-specific code.

## 19. Test objective for the next Crackling Tunes run

The next implementation test should demonstrate that one monthly Crackling Tunes distribution can pass through the same generic engine while producing:

- complete source preservation;
- source-specific CTMM / CT identifier derivation;
- candidate release-track structure;
- external-reference linkage where supported;
- explicit unresolved cases;
- provenance from derived output back to source representation.

The test should **not** require final canonical Work, Person, Ensemble, Performance, or Manifestation identities.

## 20. Working conclusion

The earlier Crackling Tunes work does not need to be discarded. Its strongest ideas are retained:

> **Exploit the source's own structure and identifiers first; preserve source representations; use transformation rules to expose useful structure; promote interpretations when evidence supports them; retain provenance; and keep external identities as mappings rather than replacements for MusicStewardship identities.**
