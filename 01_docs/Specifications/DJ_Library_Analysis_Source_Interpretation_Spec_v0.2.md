# DJ Library Analysis & Source Interpretation Specification

**Project:** MusicStewardship  
**Document:** DJ Library Analysis & Source Interpretation Specification  
**Version:** 0.2 — Agreed Clarifications  
**Status:** Agreed Draft / Explorer Import  
**Date:** 2026-09-03

---

## 1. Purpose

MusicStewardship shall analyze existing DJ music libraries as **knowledge-bearing source systems**.

The objective is not simply to extract audio metadata. A DJ's organization of music—especially file-system hierarchy, filenames, playlists, classifications, and other artifacts—may encode knowledge about repertoire, musical identity, event use, and performance practice.

The analysis process shall:

1. Preserve original source evidence.
2. Interpret that evidence using source-specific rules.
3. Produce a common structure of source assertions.
4. Feed those assertions into MusicStewardship identity resolution.
5. Preserve the distinction between what a source says and what MusicStewardship concludes.

Initial source systems:

- ToTango
- FromJae
- FromDaniel

These are three **parallel source systems** using a common conceptual framework with source-specific interpretation rules.

---

## 2. Core Principles

> **Common model, source-specific interpretation.**

The system shall provide a common structure for representing information extracted from DJ libraries while allowing each source profile to interpret its own organizational conventions.

The goal is to preserve the DJ's "language" while translating it into a common structure.

The system shall not force all DJ libraries into one assumed organizational scheme.

### Source personality

Each source profile shall capture the characteristic ways in which its creator organized and expressed musical knowledge.

Source-specific rules are intended to preserve these differences, not merely to accommodate technical variations in file layout.

> **Common model, different personalities.**

---

## 3. DJ Libraries as Evidence-Bearing Knowledge Systems

A DJ library shall be treated as more than a collection of audio files.

Potential evidence includes:

- File-system hierarchy
- Directory names and relationships
- Filenames
- Embedded audio metadata
- Playlists
- DJ-software databases
- Cue information
- Ratings
- Comments
- Collections
- Special-purpose folders
- Other surviving library artifacts

The analysis shall preserve evidence before interpretation.

### Observation versus interpretation

The system shall distinguish:

**Observed fact**

> The file occurs under `Cortinas/FULLSONGS/Jazz/Django`.

from:

**Source interpretation**

> The DJ classified this recording as a Cortina, under FULLSONGS, Jazz, Django.

from:

**Canonical conclusion**

> MusicStewardship identifies the recording as entity X.

These are different assertions and shall not be collapsed into one value.

---

## 4. Preserve Original Source Evidence

For each imported file, preserve, as available:

- Source identity
- Original full path
- Original directory hierarchy
- Original filename
- Embedded metadata
- Playlist membership
- Other relevant source artifacts
- Source-specific interpretations derived from them

Original source descriptions shall not be silently overwritten or "corrected."

If a source says one thing and external evidence later indicates another, both shall remain available.

Example:

    ToTango source assertion:
        year = 1943

    MusicStewardship current conclusion:
        recording year = 1941

The 1943 assertion remains part of source provenance.

---

## 5. File-System Hierarchy as Evidence

Every DJ-library importer shall evaluate the original file-system hierarchy as a potential source of knowledge.

The importer shall not assume that a directory is merely a storage convenience.

Hierarchy is evidence; it is not automatically given precedence over other evidence such as metadata.

Hierarchy may encode:

- Genre
- Dance type
- Orchestra
- Singer
- Period
- Cortina role
- Musical character
- Collection
- Intended use
- DJ-specific classification
- Other source-specific concepts

The meaning of a directory component shall come from the source-specific interpreter.

### Preserve both raw and interpreted hierarchy

Retain:

    Original path
        +
    Path components
        +
    Source interpretation of components

Interpretation remains attributable to the source.

---

## 6. Metadata as Supplementary Evidence

Embedded metadata is an additional evidence layer.

The system shall **not** assume that metadata supersedes file-system hierarchy.

Likewise, hierarchy-derived information shall not automatically supersede metadata.

Instead:

    Hierarchy
    Filename
    Metadata
    Playlists / artifacts
            ↓
    Source assertions
            ↓
    Identity resolution

Metadata may corroborate, supplement, contradict, or add information absent from the hierarchy.

Missing metadata shall not be interpreted as missing DJ knowledge.

---

## 7. Source-Specific Interpreters

Each source shall have a source profile defining how its evidence is interpreted.

Conceptually:

    Source files
        ↓
    Source-specific interpreter
        ↓
    Common source assertions
        ↓
    Identity resolution

The source interpreter shall:

- Recognize source conventions.
- Interpret hierarchy.
- Interpret filename conventions.
- Recognize source-specific abbreviations.
- Distinguish contextual assertions from precise assertions.
- Identify DJ-specific classifications.
- Preserve provenance.

The source interpreter shall **not** establish canonical entity identity by itself.

---

## 8. Common Source Assertion

A source assertion is the common unit of interpreted source knowledge passed from a source interpreter toward identity resolution or other downstream processing.

At minimum, a source assertion conceptually contains:

```text
subject
property / relationship
value
source
evidence location
interpretation rule
assertion context/type
uncertainty, where applicable
```

For example:

```text
subject = source file
property = singer
value = Roberto Rufino

source = ToTango
evidence = filename
interpretation rule = ToTango filename grammar
```

A source assertion is an interpretation of source evidence. It is not itself a canonical fact.

---

## 9. Period and Date

Tango music commonly carries meaningful temporal information at more than one level.

**Date** refers to a specific calendar date or date precision supported by the evidence.

**Period** is a separate concept. A period may be:

- a date range, such as `1939–1942`;
- a named historical or musical period, such as `Guardia Viejo`;
- another source-defined temporal expression.

Both date and period have semantic value and shall be preserved as distinct assertions.

A period shall not automatically be converted into an exact date or year.

A date shall not automatically be reduced to a period label.

A source may provide both.

---

# 10. ToTango Source Profile

## 10.1 General organization

ToTango uses relatively shallow directory organization.

Observed broad categories include:

    ToTANGO 5 Wav/
        TANGO
        VALS
        MILONGA

    ToTANGO 5 MP3/
        TANGO MP3
        VALS MP3
        MILONGA MP3

The directory level shall therefore be interpreted primarily as broad musical/dance context.

## 10.2 Filename grammar

ToTango uses an intentionally structured filename convention approximately:

    ORCHESTRA + YEAR + SINGER _ TITLE

Example:

    Di Sarli43Rufino_Cortando Camino

This shall be interpreted as source assertions approximately:

    orchestra = Di Sarli
    year = 43
    singer = Rufino
    title = Cortando Camino

Exact parsing rules shall be developed empirically from the library.

## 10.3 Year assertions

The year encoded in a ToTango filename shall be preserved as a **source assertion**.

It shall not be silently replaced by a later canonical recording year.

Example:

    ToTango assertion:
        43

    External/canonical evidence:
        1941

Both remain available with their respective provenance.

## 10.4 WAV and MP3 copies

WAV and MP3 files shall initially be treated as distinct source files.

Identity resolution may subsequently determine that they represent the same recording/performance.

File identity and recording identity remain distinct.

## 10.5 ToTango interpretation priority

Initial priorities:

- Filename structure: high importance
- Broad directory structure: important contextual evidence
- Embedded metadata: supplementary evidence
- Audio similarity: evidence for recording identity, not source semantics

---

# 11. FromJae Source Profile

## 11.1 General organization

FromJae uses deeper directory hierarchy, and the hierarchy carries substantial semantic information.

Example:

    MUSICA CIUDADANA/
        1 - TANGOS/
            QUINTETO PIRINCHO 1937 1941/
                19 - EL CIRUJA.mp3

This may provide source assertions such as:

    genre/context = Tango
    orchestra/context = Quinteto Pirincho
    period context = 1937–1941
    track number = 19
    title = El Ciruja

## 11.2 Period versus exact year

A directory expressing a range such as:

    1937 1941

shall be interpreted as a **period/context assertion**, not automatically as an exact recording year.

The importer shall not manufacture a specific recording year from such a range.

## 11.3 Singer hierarchy

Jae has added singer information as a directory level in parts of the collection.

Where such a level occurs, it shall be treated as an explicit source assertion about singer/context.

## 11.4 Filename

Jae filenames are often relatively simple and may contain:

- Track number
- Title
- Other local notation

Filename information shall be retained and interpreted in conjunction with hierarchy.

## 11.5 Metadata

Embedded metadata shall be used as supplementary evidence.

It may corroborate or add to hierarchy-derived assertions.

## 11.6 FromJae interpretation priority

Initial priorities:

- Directory hierarchy: very high importance
- Filename: useful supporting information
- Embedded metadata: supplementary
- Period directories: meaningful temporal/contextual evidence; not exact recording dates unless independently supported

---

# 12. FromDaniel Source Profile

## 12.1 Source identity

FromDaniel shall be treated as **Daniel's tango DJ collection**.

It is not merely an arbitrary subset of a general music library.

The larger DanielsLaptop acquisition is a related source artifact/superset and may contain additional DJ information such as playlists or DJ-software artifacts.

The system shall not infer that such artifacts did not exist merely because they are absent from the currently identified FromDaniel subset.

## 12.2 Heterogeneous organization

FromDaniel contains multiple organizational regimes, including:

- Main tango repertoire
- Orchestra-oriented structures
- Special collections
- Musical-style groupings
- Cortina collections
- Album/library-like structures

The importer shall therefore not assume one universal meaning for every directory branch.

Source interpretation may depend on the branch and its surrounding hierarchy.

---

# 13. Daniel's Cortina Knowledge

Cortina shall be treated as a significant first-class source concept.

Daniel's organization includes structures such as:

    Canaro y o tipica/
        Cortinas/
            FULLSONGS/
                Afro/
                Blues/
                Jazz/
                    Django/
                ...

The hierarchy shall be preserved and interpreted as Daniel's DJ organization.

Possible assertions include:

    DJ = Daniel
    role = Cortina
    collection = FULLSONGS
    musical classification = Jazz
    subclassification = Django

These are **DJ-specific classifications**, not automatically canonical MusicStewardship classifications.

`FULLSONGS` is retained as an observed hierarchy element unless analysis establishes its precise semantics; it shall not be prematurely assigned a canonical category.

## 13.1 Cortina is more than punctuation

The analysis shall allow Cortinas to represent intentionally selected musical components contributing to:

- Event character
- Pacing
- Energy
- Transition
- Audience experience
- Musical contrast
- Other DJ intentions

The specification shall not assume that a Cortina is merely a separator between tandas.

## 13.2 Prepared playback constraints

A DJ may prepare a Cortina for use by specifying how much of a recording to play.

The source model shall therefore be capable of preserving DJ-specific playback constraints such as:

    start position
    end position
    maximum duration

These constraints belong to the **DJ's use of the recording as a Cortina**, not to the recording itself.

Example:

    Recording
        ↓
    Daniel's DJ Use
        role = Cortina
        classification = Jazz / Django
        playback constraint = 0:00–0:35

The exact representation of timing constraints shall be determined during implementation.

## 13.3 Prepared choices

Some DJs configure Cortina choices before an event.

Therefore DJ-use information shall not be assumed to originate only from observed playback.

Prepared DJ knowledge and actual performance history are distinct evidence types.

---

# 14. DJ Provenance

DJ provenance shall be a first-class concept.

Preserve, where available:

- Which DJ/collector supplied the information
- Which source collection it came from
- Original hierarchy
- DJ classification
- DJ's intended/use-oriented role where inferable
- Prepared playback information
- Other DJ-specific knowledge

Distinguish:

    "This recording is a Cortina."

from:

    "Daniel uses/classifies this recording as a Cortina."

The latter is DJ provenance and may remain valuable even if MusicStewardship later reaches a different canonical classification.

---

# 15. DJ Use versus Recording Identity

A recording and a DJ's use of that recording shall be separate conceptual objects.

At minimum:

    Recording
        ↓
    DJ Use
        ├── DJ
        ├── role
        ├── source classification
        ├── source hierarchy
        └── playback preparation

This permits different DJs to use the same recording differently and the same DJ to use the same recording in multiple contexts.

Detailed temporal/version history of DJ choices is **not required for v1**, although the model should not prevent it later.

---

# 16. Identity Resolution Boundary

The source analysis system produces evidence.

The identity-resolution system determines what that evidence refers to.

The source interpreter shall not silently:

- Rename recordings
- Correct source metadata
- Replace source years
- Merge files
- Declare canonical identities without appropriate evidence

Identity resolution may use:

- Source assertions
- Known synonyms/equivalences
- Other relationships
- Audio evidence
- Trusted catalogs
- External research
- Human review

Canonical values are current best-supported conclusions and retain provenance.

---

# 17. Uncertainty and Contradiction

The system shall preserve uncertainty.

Examples:

- A DJ's period folder may establish a time context but not an exact year.
- A release year in metadata may not be a recording year.
- Two sources may provide conflicting dates.
- A filename may contain an abbreviation whose meaning is uncertain.

The system shall preserve the original assertion while separately recording the current interpretation.

No source assertion shall be discarded merely because it is currently believed to be incorrect.

---

# 18. Acquisition versus Stewardship Scope

The existence of a file in an acquired library does not necessarily mean that it belongs in the MusicStewardship catalog.

Distinguish:

    Source inventory
        ↓
    Candidate material
        ↓
    Stewardship selection

Material may be:

- Selected
- Candidate
- Deferred
- Excluded

These are stewardship decisions, not alterations to the source inventory.

Exclusion from the stewardship catalog shall not imply deletion of source evidence.

This is particularly relevant to larger acquisitions such as DanielsLaptop.

---

# 19. Search for Surviving Library Artifacts

Analysis of a source shall look beyond the obvious audio tree.

Where available, search for:

- Playlist files
- DJ-software databases
- Library databases
- Cue information
- Ratings
- Comments
- Exported playlists
- Alternate directory trees
- Hidden or parallel collection structures

For DanielsLaptop in particular, search the acquisition for artifacts that may preserve Daniel's working playlists or DJ organization outside FromDaniel.

---

# 20. Common Output Structure

All three source interpreters should produce a common conceptual output containing, as applicable:

    Source
    Source Person / DJ
    Source Collection
    Source Artifact
    Original Path
    Original Path Ordering / Sequence, where meaningful
    Original Filename
    Observed Hierarchy
    Interpreted Hierarchy
    Embedded Metadata
    Source Assertions
    DJ Classifications
    DJ Use
    Playback Constraints
    Provenance
    Uncertainty / Conflicts

Not every source will populate every field.

The common structure exists to make outputs interoperable, not to force every source to contain the same information.

Source, DJ/person, collection, and source artifact shall remain distinct concepts. A source artifact may contain or represent another collection or source.

---

# 21. Analysis Workflow

Initial workflow:

    1. Inventory source
            ↓
    2. Preserve original structure
            ↓
    3. Analyze hierarchy
            ↓
    4. Analyze filename conventions
            ↓
    5. Analyze embedded metadata
            ↓
    6. Search for playlists/library artifacts
            ↓
    7. Apply source-specific interpretation rules
            ↓
    8. Produce source assertions + provenance
            ↓
    9. Resolve identities
            ↓
    10. Preserve unresolved/contradictory evidence

Analysis should proceed from least interpretive observations toward increasingly interpretive conclusions.

---

# 22. Empirical Refinement

The source profiles in this specification are **initial rules/hypotheses**, not immutable truths.

Analysis of the actual libraries shall discover:

- Exceptions
- Additional conventions
- Ambiguous structures
- Additional semantic levels
- Source-specific abbreviations
- Previously unknown DJ practices

Repeated conventions may be added to the relevant source profile.

Source-specific rules shall evolve independently without changing the common conceptual model unless a genuine common pattern is discovered.

---

# 23. Explicit Non-Goals for v1

This specification does not yet define:

- Final database tables/classes
- Numeric confidence thresholds
- Complete tango ontology
- Exhaustive musical classification
- Detailed temporal versioning of DJ choices
- Automatic retagging or renaming of files
- Automatic construction of tandas
- Final TangoDJ export format
- Complete event grammar

Those concerns may consume the outputs of this analysis system but should not distort the initial source-analysis problem.

---

# 24. Acceptance Criteria for the Three Initial Sources

## ToTango

- Structured filenames can be parsed into source assertions.
- Filename year assertions are preserved independently of canonical dates.
- Directory context is preserved.
- WAV/MP3 copies remain separate files while permitting recording-level reconciliation.

## FromJae

- Deep hierarchy can be preserved and interpreted.
- Orchestra/singer/period context can be represented.
- Period ranges are not mistaken for exact recording years.
- Filename and metadata can supplement hierarchy.

## FromDaniel

- Daniel's tango DJ collection is recognized as a DJ knowledge source.
- Heterogeneous organizational branches can be represented.
- Cortina hierarchy is preserved.
- DJ classifications remain attributable to Daniel.
- Prepared Cortina playback constraints can be represented when discovered.
- DanielsLaptop can be treated as a related acquisition/source artifact from which additional library evidence may be recovered.

## All three

- The same common conceptual output structure is used.
- Source-specific interpretation rules remain separate.
- Original evidence is never silently overwritten.
- Metadata supplements rather than replaces hierarchy-derived evidence.
- Resulting assertions can be passed to the common identity-resolution engine.

---

# 25. Guiding Principle

> **Preserve the DJ's language; translate it into a common structure; don't erase the accent.**

The purpose of source analysis is not to make three different DJ libraries look the same.

It is to make their knowledge **interoperable while preserving the differences that make that knowledge valuable**.
