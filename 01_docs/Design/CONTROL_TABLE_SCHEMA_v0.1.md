# MusicStewardship Source Control Table Schema v0.1

A source control table maps a source/provider representation into a
MusicStewardship semantic term and specifies the engine-verb application.

## Columns

- `control_id` — stable control-table identifier.
- `source` — source/provider.
- `source_name` — source-side field or representation.
- `semantic_term` — controlled MusicStewardship semantic name.
- `representation_level` — source, source→semantic, decomposed, derived, supplemental, or external.
- `operation` — fixed engine verb.
- `decoder` — reusable mechanism/decoder used by the verb.
- `target_entity` — downstream object receiving the observation.
- `target_property` — downstream property.
- `target_relationship` — optional relationship.
- `preserve_source_value` — whether the original representation remains available.
- `confidence` — evidence confidence.
- `status` — established, optional, proposed, etc.
- `notes` — scope or unresolved semantic detail.

The architectural flow is:

```text
source representation
        ↓
source control mapping
        ↓
MusicStewardship semantic term
        ↓
operation + decoder + parameters
        ↓
same rule-driven engine
```

These tables separate source vocabulary from MusicStewardship vocabulary. Future
collections should receive additional source control tables rather than engine
changes merely because source field names differ.
