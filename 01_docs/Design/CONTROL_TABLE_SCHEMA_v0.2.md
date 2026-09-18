# MusicStewardship Source Control Table Schema v0.2

The control table now explicitly separates three things:

```text
source_name
    ↓
source_field
    ↓
semantic_term
    ↓
operation / decoder
```

- `source_name` — the name used by the source or source grammar.
- `source_field` — the actual column supplied to the rule engine/input record.
- `semantic_term` — the controlled MusicStewardship semantic name.
- `operation` — fixed engine verb.
- `decoder` — reusable mechanism used by the verb.
- target and evidence columns specify the resulting observation.

This prevents the semantic term from being confused with the physical input
column name.

The intended processing flow is:

```text
source material
    ↓
source extraction
    ↓
source_field
    ↓
source control mapping
    ├── source_name
    ├── source_field
    └── semantic_term
    ↓
translation rule
    ├── operation
    └── decoder
    ↓
fixed-verb engine
```

The v0.2 files are a transition/control artifact. Some CT-specific fields
(`metadata_ct_catalog_id`, `source_side`, etc.) are not yet emitted by the
current generic source-ingest output; those fields remain identified so the
source-specific preparation layer can expose them explicitly later.

No source-specific knowledge belongs in the engine.
