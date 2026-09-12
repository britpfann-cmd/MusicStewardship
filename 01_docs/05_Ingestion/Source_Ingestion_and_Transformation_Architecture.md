# Source Ingestion and Transformation Architecture

**Status:** Draft / TTT-informed, intentionally extensible
**Version:** 0.1
**Date:** 2026-09-04

---

## 1. Purpose

MusicStewardship must ingest catalog information from multiple sources whose formats, field structures, terminology, and information density differ.

The ingestion architecture therefore separates:

1. the **common ingestion engine**;
2. **source-specific knowledge** describing the information structure and semantics of each source;
3. reusable **decoding and transformation functions**;
4. the **Common Model** into which information is mapped;
5. a **Supplemental / Extra Overlay** for useful information that does not belong in the Common Model; and
6. **completeness tests** that determine whether all useful source information has been accounted for.

Tango Time Travel (TTT) is the first source being used to develop and test this architecture.

TTT-specific knowledge should therefore inform the architecture without becoming an accidental constraint on later sources.

---

## 2. Design Principles

### 2.1 One ingestion engine

There should be one general ingestion engine rather than a separate importer for each source.

The engine provides common processing capabilities while source profiles provide knowledge about how a particular source expresses information.

Conceptually:

    Source input
        ↓
    Source adapter
        ↓
    Source-specific interpretation rules
        ↓
    Generic transformation / decoding functions
        ↓
    Common Model
        +
    Supplemental / Extra Overlay
        ↓
    Completeness and validation

---

### 2.2 Source knowledge is declarative where practical

Source-specific information should be represented as rules, mappings, profiles, and grammar rather than embedded unnecessarily in Python code.

A source profile may describe:

- input format;
- source fields;
- source terminology;
- field semantics;
- compound-field structures;
- filename conventions;
- directory conventions;
- source-specific vocabularies;
- extraction rules;
- decomposition rules;
- evidence requirements;
- mappings to Common Model concepts;
- supplemental information.

The engine supplies the mechanisms; the source profile supplies the knowledge.

---

### 2.3 Decoding techniques should be reusable

A transformation discovered while analyzing one source may also apply to other sources.

Examples include:

- direct copy;
- rename;
- normalization;
- separator-based decomposition;
- labeled-field extraction;
- regular-expression extraction;
- clause extraction;
- date interpretation;
- vocabulary mapping;
- lookup;
- derivation;
- path extraction.

A new source should normally add **rules using existing decoding techniques**, rather than require a new implementation of the same technique.

When a genuinely new transformation technique is discovered, it should be added to the generic decoder framework and then become available to all source profiles.

---

### 2.4 Preserve source evidence

Transformation should not destroy the source representation.

Where information is transformed, the system should retain sufficient evidence to establish:

- the original source value;
- the transformation applied;
- the resulting components;
- the source rule that caused the transformation;
- the provenance of the resulting value.

Derived information should therefore remain explainable.

---

## 3. Source Adapters

Different sources may arrive as:

- CSV;
- HTML;
- database exports;
- JSON/XML;
- audio-file metadata;
- directory/file structures;
- other structured or semi-structured formats.

The source adapter converts the physical input into a form that the generic ingestion machinery can analyze.

The completeness framework should not depend on the physical source format.

Thus:

    CSV ─┐
    HTML ├──→ normalized source evidence ─→ common processing
    JSON ┤
    tags ┤
    files ┘

The adapter solves the format problem.

The source profile solves the semantic problem.

The decoder solves the transformation problem.

---

## 4. Transformation / Decoder Framework

Transformations should be represented as generic operations with source-specific arguments.

A conceptual transformation has the form:

    decoder(type, input, arguments)

For example:

    separator(
        value,
        separator=" / ",
        components=["ensemble", "performer"]
    )

or:

    labeled_fields(
        value,
        labels=["Record", "Matrix", "Take"],
        components=["record", "matrix", "take"]
    )

The same decoder can therefore be used by multiple sources.

### 4.1 Standard transformation classes

The initial transformation vocabulary includes:

- `COPY`
- `RENAME`
- `STANDARDIZE`
- `DECOMPOSE`
- `COMBINE`
- `LOOKUP`
- `EXTRACT`
- `PATH_EXTRACT`
- `DERIVE`
- `REFERENCE`
- `IGNORE`
- `SOURCE_CONTEXT`

This vocabulary may evolve as additional sources are analyzed.

---

## 5. Compound-Field Decoding

Compound fields require particular attention because a single source field may contain several distinct pieces of information.

Examples encountered in TTT include:

- artist/ensemble/performer information;
- composer and lyric/credit information;
- record/matrix/take information;
- structured clauses embedded in comments.

Rather than creating a separate Python function for every compound field, the system should use a generic decoding mechanism whose arguments specify:

- what is being split;
- how it is recognized;
- what the resulting components are called;
- how unmatched material is treated.

For example:

    input field
        ↓
    generic decoder
        ↓
    named components
        +
    residual source value

This reduces testing requirements and makes future rule additions primarily a matter of adding data/configuration rather than adding code.

---

## 6. Common Model Mapping

The purpose of decoding is not merely to reproduce the source schema.

The objective is to recover information represented by the source and map it into the MusicStewardship Common Model.

A source field may therefore:

- map directly to one Common Model field;
- decompose into several Common Model fields;
- combine with another source value;
- provide evidence for an existing identity;
- provide information used to derive another value.

The transformation should preserve the distinction between:

**source representation**

and

**Common Model representation**.

A richer source vocabulary is not necessarily a problem.

For example, TTT contains a richer genre vocabulary than TangoDJ. The Common Model should retain distinctions that have meaningful stewardship or catalog value rather than prematurely forcing the information into the narrower vocabulary of a downstream DJ application.

Conversion to TangoDJ's vocabulary belongs to a later output/transformation stage.

---

## 7. Supplemental / Extra Overlay

Not every useful source datum will necessarily have a corresponding Common Model field.

Such information should not simply be discarded.

The system should retain useful source-specific information in a Supplemental / Extra Overlay.

The intended decision path is:

    Source information
          │
          ├── maps directly → Common Model
          │
          ├── safely decomposes → Common Model
          │
          ├── useful but not Common Model → Extra Overlay
          │
          └── deliberately valueless → Explicitly Ignored

The distinction between "not in the Common Model" and "not useful" is important.

The Extra Overlay provides a controlled place for source-specific information without contaminating the Common Model with every source's unique vocabulary and conventions.

---

## 8. Completeness Testing

Completeness must become a repeatable automated test.

The fundamental requirement is:

> Every information-bearing source value must be accounted for.

For each source field/value, the system should be able to determine that the information has reached one of the following destinations:

1. **Common Model**
2. **Supplemental / Extra Overlay**
3. **Explicitly Ignored**

Anything else is:

    UNACCOUNTED

and constitutes a completeness failure.

### 8.1 Structural completeness

Structural completeness asks:

> Have we accounted for the information-bearing source fields and values?

### 8.2 Transformation completeness

Transformation completeness asks:

> Have we recognized every syntactic pattern required to decode those values?

These are related but distinct tests.

A source may have a known field whose values contain an unrecognized compound syntax. The field itself is known, but the transformation grammar is incomplete.

---

## 9. Pattern Coverage

Compound and structured fields should be analyzed against actual source data.

For each observed pattern, the analysis should identify:

- source field;
- observed syntax;
- number of occurrences;
- decoder technique;
- rule identifier;
- resulting components;
- Common Model destination;
- Supplemental destination, if applicable;
- residual information;
- unresolved status, if any.

The objective is to replace subjective confidence such as:

> "We think we covered the patterns."

with a testable assertion:

> "Every observed information-bearing pattern is classified and handled."

---

## 10. Completeness Test Result

A generic completeness test should ultimately produce a machine-readable result.

A successful source analysis might report:

    PASS

    Source fields accounted for:       100%
    Observed transformation patterns:  100%
    Unaccounted information:           0
    Unrecognized patterns:             0

A failure might report:

    FAIL

    Unaccounted values:                17
    Unrecognized patterns:              3
    Common Model gaps:                  0
    Supplemental candidates:            4

The exact reporting format may evolve.

The important requirement is that completeness be objectively testable and repeatable.

---

## 11. Cohort and Individual-Record Testing

Component tests should be performed before applying the complete transformation system to individual records.

The intended sequence is:

    Generic decoder tests
        ↓
    Source rule tests
        ↓
    Source completeness test
        ↓
    Representative record cohorts
        ↓
    Individual record inspection
        ↓
    Full-source processing

The purpose of cohort testing is to expose interaction between independently valid transformations.

A transformation may work correctly in isolation while interacting incorrectly with another transformation when applied to a complete source record.

---

## 12. TTT as Initial Implementation

Tango Time Travel provides the first substantial test case for the architecture.

The TTT analysis has already established useful examples involving:

- direct field mappings;
- richer genre vocabulary;
- artist/ensemble/performer decomposition;
- composer/credit decomposition;
- catalog-number decomposition;
- comment classification;
- date abstraction;
- source-specific clauses;
- residual information requiring supplemental treatment.

TTT therefore provides the initial source grammar and the first substantial test population.

The TTT grammar is not intended to define the entire ingestion architecture.

It is the first implementation against which the architecture is tested.

---

## 13. Date Abstraction

Dates require an abstraction capable of representing both:

- **points** in time; and
- **periods/ranges**.

Source representations may contain complete dates, partial dates, ranges, or ambiguous dates.

The Common Model should represent the temporal meaning rather than merely reproduce a particular source's textual date format.

Where conflicting dates suggest a possible representation error, the system should preserve the source evidence and produce a review flag rather than silently rewriting the source value.

---

## 14. Generalization to Other Sources

After TTT has been implemented and tested, the same ingestion engine and generic decoder framework should be applied to additional sources.

The process should be:

    Analyze new source
        ↓
    Identify source semantics
        ↓
    Identify transformation patterns
        ↓
    Reuse existing decoders where possible
        ↓
    Add new generic decoder only when necessary
        ↓
    Add source-specific rules
        ↓
    Run completeness test
        ↓
    Test representative cohorts
        ↓
    Re-run existing source tests

A new source should therefore be an opportunity to improve the general system rather than produce another isolated importer.

---

## 15. Learning and Evolution

The architecture is intentionally evolutionary.

Knowledge gained from later sources may require changes to:

- the transformation vocabulary;
- decoder capabilities;
- completeness categories;
- Common Model boundaries;
- Supplemental Overlay structure;
- source-profile conventions.

When a later source reveals a generally useful transformation, that capability should be generalized where practical and then tested against previously implemented sources.

This provides a regression mechanism for the ingestion architecture.

The objective is not to freeze the design after TTT.

The objective is to make each new source improve the general ingestion capability.

---

## 16. Current Architectural Boundary

At this stage the following principles are considered established:

- one common ingestion engine;
- source-specific semantic knowledge;
- reusable transformation/decoder functions;
- preservation of source evidence;
- Common Model as the convergence point;
- Supplemental / Extra Overlay for useful source-specific information;
- automated completeness testing;
- cohort testing before broad processing;
- later downstream transformation for application-specific output formats.

The exact implementation of these principles remains subject to refinement as additional sources are analyzed.

---

## 17. Open Questions

The following should remain explicitly open until additional source experience provides evidence:

- whether the initial transformation vocabulary is sufficient;
- whether additional completeness categories are required;
- the final representation of the Supplemental / Extra Overlay;
- the final declarative grammar format;
- the degree to which source adapters should normalize input;
- how much source-specific vocabulary belongs in the Common Model;
- which transformations should be purely declarative and which require code;
- how provenance and transformation evidence should be represented in the final data model.

These questions should be resolved from evidence rather than prematurely fixed by the TTT implementation.

---

## 18. Design Goal

The ultimate goal is:

> **One ingestion system capable of learning the information structure of diverse sources, decoding that information through reusable transformation techniques, mapping it into a stable Common Model, preserving useful source-specific information in a Supplemental Overlay, and demonstrating through automated completeness tests that no information has been silently lost.**

TTT is the first proving ground for this approach, not its final definition.