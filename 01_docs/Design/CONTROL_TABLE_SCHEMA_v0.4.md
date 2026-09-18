# MusicStewardship Source Control Table Schema v0.4

## Purpose

A source control table is the declarative authority for translating one
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
- `input_semantic_term` — semantic input when a rule consumes an already-derived semantic value rather than a raw source field.

### Semantic intent
- `semantic_term` — MusicStewardship semantic vocabulary term.
- `representation_level` — source, source→semantic, decomposed, derived, supplemental, external, etc.
- `input_role` — how the input participates:
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

## Input resolution

A materialized rule should retain its own `source_field` whenever the input
comes directly from a source-ingest column. This allows multiple source fields
to provide evidence for one semantic term.

Example:

```text
filename_rule_values   → ct_source_identifier
metadata_ct_catalog_id → ct_source_identifier
```

A rule may instead declare:

```text
input_semantic_term = artist_representation
```

when a semantic result is derived from an earlier semantic representation.

This distinction prevents source-specific grammar from being hidden inside the
engine.

## Pattern rule

Patterns belong in the control table. The materializer must copy them; it
must not contain source-specific `if control_id == ...` logic.

## Fixed-verb principle

The engine's verb set remains independent of source/provider. New collections
add control rows, mappings, and vocabulary terms rather than new engine verbs.

## Current implementation note

Direct source-field rules and multi-source evidence are executable through the
current rule contract. Semantic-to-semantic derivation (`input_semantic_term`)
is part of the architecture and is the next generic engine capability to
enable; it must not be implemented as source-specific code.
