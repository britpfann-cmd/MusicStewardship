# Historical Ingestion Tools

These tools are retired historical implementations from the development
of MusicStewardship's grammar-driven ingestion architecture.

They are retained as regression references and historical evidence.

They are NOT part of the current production ingestion path.

## Retirement principle

A historical implementation is retired only after its relevant behavior
has been baselined or superseded by the generalized architecture.

Files may be restored through Git if historical comparison is required.

## Current successor

The intended production direction is:

    source tree
        ↓
    source grammar
        ↓
    generic ingestion engine
        ↓
    evidence
        ↓
    asset records
        ↓
    optional reconciliation

## Retired files

See RETIREMENT_MANIFEST.csv.
