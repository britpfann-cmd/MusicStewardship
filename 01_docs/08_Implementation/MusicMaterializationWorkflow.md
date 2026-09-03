# Music Materialization Workflow

**Status:** Baseline implementation workflow  
**Baseline date:** 2026-08-29

## Purpose

Create managed and destination-specific digital assets from resolved source assets without altering the source.

## Pipeline

```text
source AudioAsset
      ↓
identity-resolved Recording
      ↓
materialization policy/profile
      ↓
manifest
      ↓
copy and/or convert
      ↓
technical + metadata validation
      ↓
managed/destination AudioAsset
```

## Source immutability

Materialization is never an in-place source rewrite.

The source asset remains unchanged.

## Manifest-driven operation

Every materialization operation shall be represented by a manifest containing at least:

```text
source_asset_id
source_path
recording_id
destination_profile
destination_path
format
metadata_policy
filename_policy
overwrite_policy
```

The manifest is the auditable instruction set.

## Format policy

### Managed/master

```text
lossless source → FLAC preferred
lossy source    → retain source quality
```

A lossy file must not be up-converted simply to produce a FLAC container.

### Destination

Destination formats are profile-specific.

Possible profiles:

```text
MASTER_LOSSLESS
DJ_WINDOWS
DJ_MAC
PHONE
BACKUP
```

A phone profile may choose MP3 for storage efficiency.

A DJ profile may select an appropriate format and metadata policy for the target DJ software and host environment.

## Filename policy

Generate managed filenames from canonical values, not from source filenames.

Do not use filename as identity.

Identity is provided by MusicStewardship identifiers.

## Metadata policy

Write only fields selected by the destination profile.

The profile may control:

- title;
- artist;
- album artist;
- date;
- genre;
- composer;
- comment;
- source/reference identifiers;
- DJ-oriented fields.

## Multiple copies / preferred assets

A materialization creates another AudioAsset belonging to the same Recording.

The system shall support identifying:

```text
BEST
PREFERRED
CONTEXT_PREFERRED
```

without deleting alternative assets.

## Validation

For each materialized asset:

1. destination exists;
2. destination audio opens;
3. expected format is present;
4. metadata matches manifest;
5. checksum/fingerprint is recorded;
6. source remains unchanged;
7. new asset is linked to its source/Recording relationship.

## Processing ledger

Materialization operations shall write processing events to the resumable ingest/materialization ledger.

A failed materialization must be retryable without losing the prior attempt.

## Catalog timing

Permanent catalog record creation and materialization are separable.

A recording may be cataloged before materialization.

An AudioAsset may exist before a destination copy is created.
