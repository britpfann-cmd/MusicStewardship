# MusicStewardship Source Control Table Schema v0.5

## Purpose

A source control table is the declarative authority for translating an
external source representation into MusicStewardship semantic terms.

The execution architecture is:

```text
source vocabulary
      ↓
source control table
      ↓
generic materializer
      ↓
effective engine rules
      ↓
fixed-verb Rosetta engine
```

## Control-table fields

### Identity and provenance
- `control_id` — unique control-row identifier.
- `source` — source/provider name.
- `source_name` — source-visible field or representation name.
- `source_field` — field in the source-ingest record when the input is directly available.
- `input_semantic_term` — semantic input when a rule consumes an already-derived semantic value.

### Semantic intent
- `semantic_term` — MusicStewardship semantic vocabulary term.
- `representation_level` — source, source→semantic, decomposed, derived, supplemental, external, etc.
- `input_role`:
  - `SOURCE` — direct source representation.
  - `DERIVATION_INPUT` — evidence/input used to derive another semantic.
  - `DERIVED` — output produced by interpretation/decomposition.
  - `CORROBORATING` — independent evidence supporting the same semantic concept.

### Execution
- `operation` — one of the engine's fixed verbs.
- `decoder` — generic decoder variant.
- `match_pattern` — optional condition determining whether a rule applies.
- `decoder_pattern` — optional pattern supplied to the decoder.

### Target and audit
- `target_entity`
- `target_property`
- `target_relationship`
- `preserve_source_value`
- `confidence`
- `status`
- `notes`

## Source references and research preservation

Source-reference fields should preserve the complete source-provided representation
even when MusicStewardship does not currently decompose it into constituent
identifiers.

These values may be useful later for historical research, provenance analysis,
cross-catalog reconciliation, or other investigative work. DJ-facing views may
display the reference as a simple origin citation without requiring interpretation
of its internal components.

Example:

```text
Origin: CT1898-B1
Source catalog: Label 1A-0752-B, matrix S-004844
```

The complete source values remain stored; decomposition into side, take, matrix,
label, or other components is optional and should be introduced only when a
specific use case and source evidence justify it.

## CT implementation note

For Crackling Tunes, the current ingest demonstrates two useful reference
representations:

```text
filename_rule_values
    → ct_source_identifier
    → displayable origin/reference

metadata_catalognumber
    → source_catalog_number
    → preserved source catalog reference
```

The current design intentionally does **not** decompose `CT1898-B1` into
`source_side`, `source_take`, or another inferred identifier hierarchy.

Those components remain available in the raw source evidence and may be modeled
later for a research-oriented use case.

## Fixed-verb principle

The engine's verb set remains independent of source/provider. New collections
add control rows, mappings, and vocabulary terms rather than new engine verbs.

## Input resolution

A materialized rule retains its own `source_field` whenever the input comes
directly from a source-ingest column. This permits multiple source
representations of one semantic concept.

A rule may instead declare `input_semantic_term` when it consumes an already
derived semantic representation. Semantic-to-semantic derivation remains a
generic engine capability rather than source-specific code.
