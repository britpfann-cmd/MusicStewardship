# Crackling Tunes Source Additions v0.1

**Builds upon:** `COMMON_SOURCE_BASELINE_v0.1`

## Source identity

```text
source = CracklingTunes
```

## Release representation

Crackling Tunes uses monthly release directories such as:

```text
21.08 Releases
21.09 Releases
...
25.12 Releases
```

A release directory name is source context; it is not by itself a canonical release identity.

## Filename grammar

Known CT filename forms include:

```text
... DD_MM_YYYY [CT...]
... YYYY [CT...]
```

The CT identifier is represented in the terminal bracketed value:

```text
[CT1898-B1]
```

## Identifier evidence

A tested 21.08 release demonstrated exact agreement between:

```text
filename CT identifier
embedded CATALOG # tag
```

for all ten audio files.

Preserve both representations.

## CT-specific embedded tag

The embedded tag:

```text
CATALOG #
```

is a source-specific CT identifier representation.

It should not be collapsed with:

```text
CATALOGNUMBER
```

which in tested material represented historical label/matrix information such as:

```text
Label 1A-0752-B, matrix S-004844
```

## Date representations

CT filenames may supply:

```text
DD_MM_YYYY
```

or only:

```text
YYYY
```

Embedded `DATE` may also have reduced precision.

Retain each representation and its precision.

## Artist representation

CT examples include:

```text
Orchestra / singer
Orchestra / Instr.
```

The interpretation of these strings into ensemble, person, singer/performer, and instrumental evidence is CT grammar, not common audio reading.

## Release track

Embedded:

```text
TRACK
```

is a candidate source release-track position.

Do not substitute historical `source_track_number` for release-track position.

## Source track provenance

Historical staging contains:

```text
source_track_number
```

under source provenance.

Its exact CT semantics remain uncommitted pending stronger historical evidence.

## CT fallback rule

When embedded `CATALOG #` is absent but the filename contains a CT identifier:

```text
filename CT identifier
    → fallback source identifier evidence
```

When both exist:

```text
agreement
    → corroborating evidence

disagreement
    → preserve both + create resolution/conflict evidence
```

## Non-audio source assets

CT releases may also contain:

```text
release notes
graphics
other collateral
```

These remain source assets even when the audio translator does not interpret them.
