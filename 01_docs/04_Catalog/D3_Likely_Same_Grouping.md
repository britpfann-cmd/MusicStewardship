# MusicStewardship D3 — Likely-Same Representation Grouping

**Status:** Architecture baseline / implementation contract  
**Date:** 2026-10-06

## 1. Purpose

D3 assesses candidate representations sufficiently to construct **useful, reversible likely-same groups**. D3 does not require or imply historical entity identity.

> **A working title does not have to be a Work, and a likely-same person-name group does not have to be a proven Person.**

This distinction permits immediate catalog and DJ usefulness while preserving a pathway to later research and reconciliation.

## 2. Processing position

```text
C semantic observations
        ↓
D2 candidate representations / discovery evidence
        ↓
D3 representation classification and compatibility assessment
        ↓
LIKELY-SAME GROUP
        ↓
operational catalog / search / DJ use
        │
        └── optional later reconciliation
                    ↓
             historical entity
```

D2 remains permissive discovery. D3 examines candidate membership in the context of all relevant observations belonging to participating CatalogedInstances. Candidate-set membership alone is not sufficient evidence assessment.

## 3. Representation domains, not premature entities

Prototype D2 currently uses `entity_type="Work"` and `entity_type="Person"`. At the grouping stage these labels are semantically stronger than warranted.

Production D should distinguish representation domains such as:

- **TITLE** — title-like representations that may later contribute evidence about a Work.
- **CONTRIBUTOR_NAME** — name-like contributor representations that may later contribute evidence about a Person.

Historical Work/Person identity is a later, optional conclusion.

## 4. Title grouping

D3 may group compatible title representations without forcing them into one canonical source string and without asserting a Work identity.

A participating CatalogedInstance may contain:

- a representation that is a direct candidate-set member;
- another representation that is mechanically compatible but outside the exact D2 membership set;
- a source-specific annotated title plus a compatible filename-derived title;
- multiple legitimate title forms that should all remain preserved.

D3 therefore distinguishes at least:

- **supporting member** — representation directly participating in the candidate set;
- **supporting related representation** — additional relevant observation compatible with the group;
- **potentially conflicting representation** — relevant observation that supplies substantive counter-evidence rather than merely differing text;
- **missing relevant representation** — expected evidence origin absent where that distinction is meaningful.

Absence from a D2 candidate set is not equivalent to absence of information or to counter-evidence.

### TangoTunes title evidence

Population analysis examined 612 cross-CatalogedInstance title candidate sets.

Initial contextual comparison found:

- 363 sets with no title evidence outside the exact candidate membership;
- 211 sets with outside evidence mechanically compatible with the candidate members;
- 38 sets initially requiring review.

Inspection of the 38 review sets found no demonstrated substantive title contradiction in this exercise. The outside observations were accounted for by source/title representation effects including:

- 37 observations carrying `-v` / `-v2` source-title annotations while the same CatalogedInstance also supplied a compatible filename-derived title;
- 4 separator-variation observations involving slash/underscore forms;
- 3 underscore/parenthetical secondary-title formatting differences.

Examples include:

- `Bar exposición -v2` alongside filename-derived `Bar exposicion`;
- `El once / A divertirse` and `El once_A divertirse`;
- `Tu boca mintió (no me mires)` and `Tu boca mintio_No me mires`.

These findings justify operational likely-same grouping but do **not** establish 612 Works.

D3 must preserve informative distinctions such as `Bar exposición -v2`; it should not destructively normalize them merely to make grouping easier.

## 5. Contributor-name grouping

The contributor path is:

```text
contributor expression
        ↓ classification
name-like representation
        ↓ compatibility
likely-same person-name group
        ↓ optional later reconciliation
Person entity
```

A valid contributor expression is not automatically a person name. Source evidence remains preserved even when D declines to create a name-like representation.

### Roles

A person may appear in many different roles. Role is therefore **not part of Person identity and must not partition a person-name group**.

Roles belong to evidence and/or relationships. Examples may include author, composer, singer, conductor, arranger, performer, orchestra leader, producer, DJ, and future roles not yet represented in TangoTunes.

A likely-same name group may accumulate occurrences in multiple roles without claiming historical identity.

### TangoTunes contributor-name evidence

D2 discovered 420 cross-CatalogedInstance contributor-name candidate sets:

- 412 used exactly the same observed name representation;
- 8 contained only inexpensive mechanical representation variants.

Observed variant classes included:

- apostrophe glyphs: `Juan D'Arienzo`, `Juan D‘Arienzo`, `Juan D’Arienzo`;
- capitalization of particles: `Oscar De La Fuente` / `Oscar de la Fuente`, `Juan De Dios Filiberto` / `Juan de Dios Filiberto`;
- diacritics: `Julio A. Buron` / `Julio A. Burón`, `José Garcia` / `José García`;
- Unicode composition differences producing visually equivalent forms.

Role recurrence included author-only, composer-only, and author-plus-composer groups. This supports treating role as relationship/evidence rather than grouping identity.

One accepted expression, `VARIOUS`, occurred four times and demonstrates the need for a lightweight **name-like / non-name-like** classification before person-name grouping. `VARIOUS` remains valid source evidence but should not become a person-name representation. Current evidence does not justify building a broad name-recognition subsystem merely for this isolated controlled token.

These findings support likely-same person-name grouping but do **not** establish 419 or 420 historical Persons. Exact same-name recurrence can still collide across distinct people and remains evidence rather than proof.

## 6. Evidence dimensions

D3 should report facts separately from policy. Useful evidence dimensions include:

- representation domain;
- candidate/discovery set identifier;
- representation count;
- participating CatalogedInstance count;
- distinct source-record count;
- distinct source-population count when available;
- representation origins;
- roles observed;
- comparison/discovery methods;
- exact versus normalization-assisted agreement;
- within-CI corroboration;
- recurrence across source records;
- recurrence across independent source populations;
- supporting candidate members;
- supporting related observations outside exact membership;
- potentially conflicting relevant observations.

Multiple normalization algorithms agreeing on the same representations are **algorithmic corroboration**, not independent source evidence.

Multiple records from one source population are not multiple independent sources.

## 7. D3 output semantics

D3 output is reportable/reversible grouping evidence. It should not silently:

- create Work or Person entities;
- coalesce CatalogedInstances;
- discard source representations;
- convert recurrence counts into identity proof;
- assign invented probabilistic confidence;
- treat a role as part of person identity;
- treat every nonmatching representation as conflict.

No named confidence-grade vocabulary is established by this specification. If confidence/promotion policy is added later, it must remain distinct from the factual evidence assessment.

## 8. Relationship to promotion and reconciliation

Likely-same grouping and entity promotion are separate operations.

Discovery proposes representations. D3 assesses compatibility and constructs useful groups. A later promotion/reconciliation process may use D3 evidence plus external corroboration, source independence, historical research, identifiers, dates, ensembles, roles, and other evidence to establish provisional or stronger entity associations.

The promotion floor governs catalog-changing action, not discovery or preservation.

## 9. Production success criterion

D3 is successful when it can provide useful, transparent, reversible grouping for catalog/search/DJ operations without requiring premature historical identity decisions, while retaining enough provenance and evidence for later research, correction, merge, split, or reconciliation.

For the present baseline, TangoTunes demonstrates that inexpensive representation compatibility captures nearly all observed title and contributor-name variation needed for operational grouping. Tango Time Travel remains the practical benchmark for overall descriptive/cataloging usefulness.
