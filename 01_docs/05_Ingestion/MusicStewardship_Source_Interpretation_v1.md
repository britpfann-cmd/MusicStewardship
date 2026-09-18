# MusicStewardship — Source Interpretation v1

## 1. Purpose

Source Interpretation converts preserved source-organization and filename evidence into explicit interpretation propositions while retaining the observations from which those propositions were derived.

It answers:

> What does the source appear to be saying?

It does not perform canonical entity resolution.

## 2. Pipeline Position

Explorer Tree
→ Semantic Map
→ Candidate Extraction
→ Candidate Record
→ Source Interpretation
→ Resolution

Candidate Record is the evidence boundary.

Source Interpretation is the source-semantic interpretation boundary.

Resolution is the semantic/canonical resolution boundary.

## 3. Core Principle

Extract facts; preserve evidence.

Interpretation shall never consume, replace, or discard the observations from which an interpretation was derived.

Every interpretation proposition shall retain lineage to its supporting evidence.

## 4. Rules

1. Never consume evidence.
2. Never manufacture absent information.
3. Do not assign canonical entity identity.
4. Do not rank evidence sources by authority.
5. Preserve the original source wording.
6. Distinguish source-context propositions from semantic attributes.
7. Numeric filename components remain uninterpreted unless a source-specific rule establishes their meaning.
8. Directory names may provide interpretation evidence, but directory position alone does not establish canonical semantic meaning.
9. Filename grammar may provide interpretation evidence, but token position alone does not establish canonical semantic meaning.
10. Competing interpretations remain explicit; they are not silently resolved.
11. Source-specific interpretation rules may be more specific than generic rules, but must preserve the underlying generic observation.
12. Interpretation status does not imply canonical identity.

## 5. Interpretation Proposition

Each proposition shall contain:

- interpretation_id
- source_object_id
- attribute
- value
- value_type
- status
- supported_by[]
- context_used[]
- derivation
- notes

### Status

- resolved
- ambiguous
- unresolved

`resolved` means that the source evidence supports the stated interpretation. It does not mean that a canonical entity or external authority has been resolved.

## 6. v1 Interpretation Operations

### preserve_directory_label

Preserve an observed directory name as a source label.

Example:

    TANDA CALO BERON

Result:

    source_grouping_label = "TANDA CALO BERON"

This does not establish that the label is a canonical Tanda.

### preserve_directory_context

Preserve a directory name as source organizational context.

Example:

    CALO MIGUEL

The value is retained as source context. No person, orchestra, singer, composer, or other canonical role is assigned.

### classify_explicit_directory_marker

Recognize an explicitly named source structural marker when a source-specific rule establishes that marker.

Example:

    TANDA CALO BERON

The interpreter may identify this as a source grouping marker.

The original directory name remains preserved.

### preserve_filename_component

Preserve a filename component extracted by an established filename grammar.

Example:

    Track02.mp3

Result:

    filename_numeric_component = "02"

The interpreter shall not call this `track_number`, `recording_id`, `catalog_number`, or another canonical identifier unless a source-specific rule establishes that meaning.

### preserve_filename_leading_text

Preserve leading filename text extracted by an established filename grammar.

Example:

    Track02.mp3

Result:

    filename_leading_text = "Track"

The value remains source evidence.

### pass_through_metadata

Direct embedded metadata propositions already established by Candidate Record evidence may pass through interpretation without alteration.

## 7. CALO BERON Expected Interpretation

For:

    MUSICA CIUDADANA/
    1 - TANGOS/
    CALO MIGUEL/
    TANDA CALO BERON/
    Track02.mp3

the interpreter may produce:

    source_grouping_label = "TANDA CALO BERON"
    source_context = "CALO MIGUEL"
    filename_numeric_component = "02"
    filename_leading_text = "Track"

The numeric value remains uninterpreted.

The interpreter shall not produce, solely from this evidence:

    track_number = 2
    recording_id = 2
    catalog_number = 2
    singer = BERON
    orchestra = CALO
    canonical_tanda = TANDA CALO BERON

## 8. Negative-Control Requirement

The interpreter shall not assign canonical meanings merely because directory names or filename components look suggestive.

For example:

    PARA COMPARAR INSTRUM 140
    SEXTETO 1929
    INSTRUMENTAL (1951-1958)

shall remain source evidence unless an applicable source-specific rule establishes their semantic interpretation.

## 9. Evidence Lineage

Each interpretation proposition shall identify the Candidate Record observation or observations that support it.

The Candidate Record remains unchanged.

Interpretation adds derived propositions; it does not rewrite the evidence.

## 10. Scope of v1

Included:

- source grouping labels
- source organizational context
- explicitly recognized source markers
- established filename components
- uninterpreted filename values
- direct metadata pass-through
- evidence lineage
- explicit interpretation status

Excluded:

- fuzzy matching
- external authority lookup
- canonical entity matching
- person identification
- orchestra identification
- singer identification
- composer identification
- automatic track-number assignment
- automatic catalog-number assignment
- semantic inference from numeric values alone
- authority ranking

## 11. Test Strategy

### Test 1 — CALO BERON

Input:

    FromJae_Tanda_Calo_Beron_candidate_records_v1.json

Expected:

- 4 interpretation records
- source grouping/context retained
- filename numeric components retained
- filename leading text retained
- no canonical track-number interpretation
- no person/orchestra/singer assignment from directory names alone
- every derived proposition has evidence lineage

### Test 2 — Negative Control

Use the heterogeneous DI SARLI source organization.

Expected:

- suggestive directory names remain preserved evidence
- numbers such as 140 and 1929 are not automatically assigned semantic meaning
- no canonical person, ensemble, period, or instrumentation assignment is made without an applicable rule

## 12. Relationship to Resolution

Source Interpretation and Resolution shall remain separate.

Source Interpretation determines what the source evidence appears to express.

Resolution determines which semantic or canonical value/entity that interpreted evidence refers to.

The existing Resolution v1 TangoTunes baseline remains unchanged while Source Interpretation v1 is developed and tested.
