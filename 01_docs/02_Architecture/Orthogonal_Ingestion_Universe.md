# Orthogonal Ingestion Universe

**Status:** Architectural Statement
**Scope:** MusicStewardship ingestion architecture
**Purpose:** Define the independent dimensions by which source information, processing, and resulting knowledge are represented.

---

## 1. Architectural Principle

The MusicStewardship ingestion universe shall be defined by **orthogonal dimensions rather than a single classification**.

Source records are observations of a musical domain that contains recurring entities, relationships, and other information. The ingestion system must therefore distinguish:

1. **what information is present and how necessary it is to ingestion;**
2. **what processing action is applied to that information;**
3. **how much assurance we currently have about the entities or assertions produced;** and
4. **where the information and resulting assertions came from.**

These dimensions are independent. No one dimension shall be used as a substitute for another.

This permits MusicStewardship to preserve information even when it cannot presently interpret it, apply different processing strategies without changing the semantic importance of the information, and improve the assurance of an entity or assertion without rewriting the original source observation.

---

## 2. Information Class

**CORE, ASSOCIATED, and RESIDUAL are mutually exclusive classifications of source information.**

They describe the role of information in the ingestion process, not the action performed on it.

### 2.1 CORE

**CORE** is the minimum information required for ingestion to occur.

Core information must be sufficiently present and interpretable for the system to create an ingestible catalog representation. If required Core information is absent or cannot be established to the required minimum, ingestion cannot proceed as a valid catalog entry.

Core therefore defines the **minimum semantic boundary for ingestion**.

### 2.2 ASSOCIATED

**ASSOCIATED** information is useful additional information that is not required for ingestion.

Associated information should be captured whenever the current processing toolset can decode, normalize, reference, or otherwise preserve it in a useful form.

The guiding principle is:

> If useful information can be obtained at reasonable cost with the tools currently available, record it rather than discard it.

Associated information may subsequently become more important as the catalog model, tools, or research needs evolve.

### 2.3 RESIDUAL

**RESIDUAL** is information that is outside the currently required or currently actionable processing scope.

This includes information that:

- cannot presently be decoded;
- is not presently of interest;
- has no presently defined transformation;
- or otherwise has no current role in the common catalog representation.

Residual does **not** mean worthless or erroneous.

**MusicStewardship shall never throw source information away.** The original source record is retained as source evidence. A residual may therefore be represented explicitly as an extracted remnant, or it may remain available in the preserved original source record when no further extraction or transformation is currently defined.

The distinction is between **not currently processing information** and **discarding information**. The former is permitted; the latter is not.

Thus, Residual provides an explicit home for **all loose ends** while the retained source record guarantees that information remains available for future processing.

---

## 3. Processing Disposition

Processing disposition is a separate and orthogonal dimension.

It describes **what the processing system does** with information.

Examples include:

- `EXTRACT`
- `DECODE`
- `NORMALIZE`
- `DECOMPOSE`
- `COMBINE`
- `DERIVE`
- `LOOKUP`
- `REFERENCE`
- `COPY`
- `IGNORE`
- `SOURCE_CONTEXT`

The existing completeness framework also provides dispositions such as:

- `COMMON_MODEL`
- `EXTRA_OVERLAY`
- `IGNORED`
- `UNACCOUNTED`

These processing dispositions must not be confused with CORE / ASSOCIATED / RESIDUAL.

For example, Associated information may be processed into the Common Model, while Residual information may be preserved as source context or deliberately ignored. The information class does not determine the processing verb.

---

## 4. Entity and Assertion Assurance

A third independent dimension describes **how confidently the system currently understands what an observation represents**.

A source observation may contribute to an entity or relationship whose assurance changes over time.

A conceptual progression is:

```text
OBSERVED
    ↓
PROVISIONAL
    ↓
RECONCILED
    ↓
CANONICAL
```

The exact assurance vocabulary and transition rules belong to the entity and identity architecture.

The important architectural rule is that **assurance is not the same thing as information class or processing disposition**.

A Core orchestra name can produce only a provisional entity today and a canonical entity later. The original source observation remains the same; the system's confidence and accumulated evidence have changed.

---

## 5. Provenance

Provenance provides the connection back to the source observation.

Every meaningful derived assertion should be traceable, as appropriate, to:

- its originating source;
- the source record or location;
- the source-specific interpretation or translation rule;
- the processing operation;
- and, where applicable, external reference evidence.

Provenance is therefore another independent dimension rather than a status attached to the information class.

The system must be able to distinguish:

```text
What the source said
        ↓
What we extracted
        ↓
What we normalized
        ↓
What we inferred or reconciled
        ↓
What entity/assertion we currently accept
```

---

## 6. Orthogonality in Practice

The dimensions may be viewed as coordinates describing an observation and its consequences:

| Dimension | Question answered | Examples |
|---|---|---|
| **Information class** | How necessary/useful is this information to ingestion? | CORE / ASSOCIATED / RESIDUAL |
| **Processing disposition** | What do we do with it? | DECODE / NORMALIZE / REFERENCE / IGNORE |
| **Assurance** | How certain are we about its interpretation or identity? | OBSERVED / PROVISIONAL / RECONCILED / CANONICAL |
| **Provenance** | Where did it come from and how was it produced? | source / record / rule / operation / evidence |

These dimensions can therefore legitimately cross one another.

For example:

| Source information | Class | Processing | Assurance |
|---|---|---|---|
| Orchestra name required by the catalog | CORE | EXTRACT → NORMALIZE → REFERENCE | PROVISIONAL |
| Singer information | ASSOCIATED | EXTRACT → REFERENCE | CANONICAL |
| An unusual source note | RESIDUAL | PRESERVE / SOURCE_CONTEXT | OBSERVED |
| External catalog identifier | ASSOCIATED | REFERENCE | CANONICAL |

The table is illustrative; the authoritative Core/Associated classification belongs to the applicable domain rules.

---

## 7. Architectural Consequence

Because these dimensions are orthogonal, the ingestion engine shall not collapse them into a single status field or mutually exclusive master state.

Instead:

```text
                     SOURCE OBSERVATION
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
       INFORMATION      PROCESSING      PROVENANCE
          CLASS          DISPOSITION
             │              │
     CORE / ASSOCIATED   verbs/actions
       / RESIDUAL             │
             │                │
             └───────┬────────┘
                     ▼
             DERIVED ASSERTION
                     │
                     ▼
                ASSURANCE
                     │
        OBSERVED → PROVISIONAL
             → RECONCILED
             → CANONICAL
```

This separation allows the same common processing machinery to operate against different source-specific rule sets while preserving the semantic distinctions required by the catalog architecture.

---

## 8. Relationship to the Rosetta Stone

The Rosetta Stone is the source-specific expression of how a particular source's representations map into this universal processing universe.

A Rosetta Stone therefore needs to be capable of specifying, for each relevant source representation:

- its information class;
- how it is decoded or otherwise processed;
- its destination semantic concept;
- any required decomposition or recombination;
- applicable references and validation;
- and its disposition when no current transformation exists.

The Rosetta Stone should make the translation **closed and auditable**:

> Every source element has a declared interpretation or an explicit residual disposition.

A residual disposition does not authorize deletion. It records that the information is not currently transformed, while the original source record remains preserved.

The common engine executes those rules. It does not need to know the peculiar grammar of TTT, Discogs, or another source.

---

## 9. Relationship to Recombination

Decoding and recombination are separate responsibilities.

The source-specific translation layer turns source representations into structured observations and assertions.

The common recombination layer then assembles those observations into the universal catalog representation, preserving recurrence, relationships, identity evidence, and provenance.

Conceptually:

```text
SOURCE REPRESENTATION
        ↓
SOURCE-SPECIFIC RULES
        ↓
COMMON DECODING / TRANSLATION ENGINE
        ↓
STRUCTURED OBSERVATIONS
        ↓
COMMON RECOMBINATION
        ↓
CATALOG INTERCHANGE REPRESENTATION
        ↓
DATABASE IMPORT
```

The database is therefore downstream of the translation and recombination architecture. Database insertion is not the mechanism by which the source is understood.

---

## 10. Architectural Summary

MusicStewardship shall treat the ingestion universe as the combination of independent dimensions:

**Information class** tells us what information matters to ingestion.

**Processing disposition** tells us what action we take.

**Assurance** tells us how confident we are about the resulting interpretation or identity.

**Provenance** tells us where the observation and resulting knowledge came from.

Together these dimensions provide a stable framework in which source-specific rules can evolve without changing the common processing machinery, incomplete interpretation can be preserved without being mistaken for failure, and entity identity can mature as evidence accumulates.

This is the foundation for a reusable ingestion architecture in which the **rules change by source, while the processing stream remains common**.
