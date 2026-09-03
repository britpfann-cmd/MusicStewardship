# Repository Naming Conventions

## Purpose

This document establishes naming conventions used throughout Music
Stewardship. Consistent naming improves readability, discoverability,
automation, and long-term maintainability while reducing ambiguity across
documentation, data, source code, and generated artifacts.

These conventions are intended to be sufficiently general for adoption
by other stewardship repositories and future projects.

---

# Top-Level Repository Structure

Top-level directories represent the major architectural layers of the
repository.

When the order of those layers conveys workflow or architectural
relationships, directories should be prefixed with two-digit numeric
identifiers.

Example:

```text
01_docs/
02_data/
03_assets/
04_src/
05_generated/
06_examples/
07_tests/
08_tools/
```

The numbering reflects the logical progression of the repository rather
than execution order.

```
Documentation
        ↓
Canonical Data
        ↓
Assets
        ↓
Implementation
        ↓
Generated Artifacts
        ↓
Examples
        ↓
Validation
        ↓
Developer Tools
```

Numeric prefixes should remain stable once established.

---

# Subdirectories

Subdirectories generally should **not** be numbered.

Subdirectories represent peer concepts rather than sequential workflow.

Example:

```text
docs/

    Architecture/
    Decisions/
    Implementation/
    Notes/
    Reference/
    Research/
    Specifications/
```

Numbering should only be introduced when a directory explicitly
represents an ordered sequence of processing stages or instructional
steps.

---

# Documents

Specifications are named for the conceptual domain they define rather
than for an individual object.

Examples:

```
PerformanceObjects.md
CanonicalMetadata.md
ExportModel.md
KnowledgeModel.md
PerformanceModel.md
```

Architecture documents describe systems rather than implementations.

Decision records use the ADR convention.

```
ADR-0001-ProjectScope.md
ADR-0002-CanonicalMetadata.md
ADR-0003-PerformanceObjects.md
```

---

# Data Files

Canonical data files use plural nouns representing collections of
objects.

Examples:

```
PerformanceObjects.csv
ExportProfiles.csv
Genres.csv
Applications.csv
```

These files constitute the authoritative canonical datasets consumed by
implementation software.

---

# Source Code

Source files follow the conventions of the implementation language while
maintaining terminology defined by the Music Stewardship architecture.

---

# Generated Artifacts

Generated files should follow deterministic naming rules derived from
canonical identifiers.

Generated filenames may vary by export target while preserving stable
canonical identity.

---

# Future Extensions

Additional naming conventions may be defined as new architectural
domains are introduced.