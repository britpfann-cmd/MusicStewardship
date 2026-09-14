# Tango Time Travel Source Additions v0.1

**Builds upon:** `COMMON_SOURCE_BASELINE_v0.1`

## Source identity

```text
source = TangoTimeTravel
```

## Filename grammar

Known TTT forms include:

```text
001 - Olvido
074_-_Farol
10-Tú
TanturiCampos _-_ Malvon
```

Filename interpretation is source-specific.

## Catalog compound representation

TTT may represent:

```text
catalog_number
```

as a compound Record / Matrix / Take representation.

Where the source grammar establishes labeled components:

```text
Record
Matrix
Take
```

preserve both the raw compound representation and decomposed components.

## Component fields

TTT may provide or derive:

```text
record_number
matrix_number
take_number
```

These are distinct identifiers/representations.

## Artist / performer interpretation

TTT may use embedded artist/performance text to provide evidence for:

```text
ensemble
person
singer / performer
instrumental
```

The source grammar decides the interpretation.

## Composer / author interpretation

TTT may use:

```text
composer
author
```

including compound or clause-based representations.

Lyrics clauses must not be treated as ordinary composer text without source-specific interpretation.

## Comment clauses

TTT comments may contain multiple structured assertions, including:

```text
pitch
key
score key
person
matrix error
other source notes
```

Preserve the original comment and derive structured assertions separately.

## Release structure

TTT may provide:

```text
album / release
track / release track number
```

These are source release representations.

## Reference evidence

TTT may contain:

```text
TANGO-DJ reference
reference metadata
```

These should enter the common external-reference layer rather than becoming TTT-specific canonical identity.
