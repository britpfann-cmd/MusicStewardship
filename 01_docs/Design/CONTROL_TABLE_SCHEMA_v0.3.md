# MusicStewardship Source Control Table Schema v0.3

## Purpose

The control table separates source naming, source input location, semantic
meaning, and execution intent.

```text
source_name
    ↓
source_field
    ↓
semantic_term
    ↓
input_role
    ↓
operation / decoder
    ↓
target
```

## input_role

`input_role` describes how a source field participates in producing a semantic
term:

- `SOURCE` — direct source representation preserved/mapped to the semantic term.
- `DERIVATION_INPUT` — source value used as evidence/input for a derived semantic.
- `DERIVED` — semantic value produced by interpretation/decomposition.
- `CORROBORATING` — independent source representation supporting the same semantic concept.

This distinction is important when one semantic term has multiple evidence paths.

### Example: TTT

```text
metadata_artist
    → artist_representation
    input_role = SOURCE

metadata_artist
    → instrumental
    input_role = DERIVATION_INPUT

metadata_artist
    → performer
    input_role = DERIVATION_INPUT
```

### Example: CT

```text
filename_rule_values
    → ct_source_identifier
    input_role = CORROBORATING

metadata_ct_catalog_id
    → ct_source_identifier
    input_role = CORROBORATING
```

The engine remains responsible only for fixed verbs and generic execution.
The control table and materializer determine which source evidence supplies
each semantic term.
