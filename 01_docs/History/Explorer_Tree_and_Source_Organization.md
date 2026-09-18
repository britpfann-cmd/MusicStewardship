# Explorer Tree and Source Organization

## Purpose

The Explorer Tree represents the organization of a music collection as it was received or encountered. It is a source-observation layer, not the canonical organization of the MusicStewardship library.

Directory and file names are often the first and highest-level source of information available during ingestion. Collections assembled by restorers, archivists, DJs, vendors, or individual collectors commonly contain meaningful hierarchical organization even when the meaning is not explicitly documented.

The Explorer Tree therefore must be preserved before interpretation or normalization.

## Source Organization Is Evidence

The following source characteristics are preserved as observed:

- directory hierarchy
- directory names
- file names
- file extensions
- relative paths
- collection and subcollection boundaries
- other filesystem-level relationships that may carry meaning

This information may subsequently be used as **classification evidence**.

For example, a directory hierarchy may provide evidence about:

- genre
- orchestra
- period
- release or collection
- source grouping
- DJ organization
- restoration project
- album or recording set

The presence of such information does not, by itself, establish its canonical meaning. Directory and filename information is evidence to be evaluated together with other available evidence such as embedded metadata, source documentation, filename grammar, external references, and the audio asset itself.

## Preserve → Normalize → Interpret

The Explorer Tree participates in a strict processing sequence:

**Preserve → Normalize → Interpret**

1. **Preserve**  
   Record the source path and filename as observed.

2. **Normalize**  
   When required for reliable parsing, comparison, or matching, create a derived normalized representation of the source text.

3. **Interpret**  
   Apply source-specific grammar and decoding rules to the preserved/normalized representation.

Normalization is a processing operation. It must never replace the preserved source value.

This distinction is particularly important for filenames because collections may contain inconsistent Unicode representations, punctuation, spacing, dash characters, accents, or other textual variations.

## Original and Derived Values

Where normalization or interpretation occurs, the system should retain both:

- the original source value
- the derived value used for processing

For example:

```text
original_filename
normalized_filename
decoded_orchestra
decoded_singer
decoded_year
```

The normalized filename is not a replacement for `original_filename`. It exists only to support deterministic processing.

Likewise, a decoded value is an interpretation of source evidence and does not erase the evidence from which it was derived.

## Explorer Tree Is Not the Canonical Library Tree

The Explorer Tree should not be confused with the eventual organization of the MusicStewardship collection.

A source may arrive organized as:

```text
Collection/
    Tango/
        Gardel/
        Di Sarli/
    Milonga/
        Canaro/
```

while the resulting stewardship or DJ-oriented views may organize the same material differently.

MusicStewardship must preserve the original organization while allowing multiple downstream views to be constructed.

This supports the principle:

> **Preserve how the collection came to us; allow output organization to vary.**

The source organization is therefore provenance and evidence, rather than a permanent constraint on the canonical library structure.

## Reconstitution

The preserved Explorer Tree should contain sufficient information to support reconstruction of the source organization when requested.

Exact byte-for-byte restoration is not necessarily guaranteed because filesystem metadata, unavailable files, external references, or information outside the scanned scope may not be recoverable.

The normal objective is therefore **source reconstitution**, not necessarily forensic filesystem restoration.

Reconstitution is an available stewardship capability but is not normally required for day-to-day operation.

## Scanner Responsibility

The Explorer Tree is created by a source scanner whose responsibility is observation, not interpretation.

The scanner should:

- traverse the supplied source root
- record every encountered filesystem entry within scope
- preserve relative paths and names as observed
- identify files versus directories
- retain relevant filesystem metadata
- optionally calculate content hashes
- record errors rather than silently dropping inaccessible entries
- produce deterministic inventory output for subsequent processing

The scanner should **not**:

- rename files
- move files
- modify metadata
- normalize filenames in place
- infer genre, orchestra, singer, period, or other musical meaning
- discard apparently unimportant directories or files
- impose the eventual MusicStewardship library organization

Interpretation belongs to the ingestion layer.

## General Applicability

The Explorer Tree is intentionally source-agnostic.

The same mechanism should work for:

- restorer collections
- DJ collections
- commercial releases
- archival collections
- personal collections
- downloaded source collections
- collections assembled from multiple historical sources

Source-specific grammars determine how information contained in the tree is interpreted. The Explorer Tree itself remains a common stewardship mechanism.

## Architectural Rule

> **Source organization is preserved as provenance and may be used as classification evidence. Canonical classification must not require destructive normalization of that organization. The system shall retain sufficient provenance to permit reconstruction of the source collection when requested.**

A related rule applies to text processing:

> **Text normalization is a processing operation, not source preservation. Source text, including filenames and path components, shall be preserved as observed. When normalization is required for reliable parsing or comparison, the normalized text is a derived processing value.**
