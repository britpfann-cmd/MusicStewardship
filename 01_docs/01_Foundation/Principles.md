# Music Stewardship Design Principles

## P1. Canonical Truth

Each musical work has one canonical representation within the stewardship system.

Applications receive translated representations appropriate to their capabilities.

---

## P2. Separation of Knowledge

Audio, metadata, observations, knowledge, and experience are distinct but related.

They should never be conflated.

---

## P3. Stewardship Before Convenience

Short-term convenience must not compromise long-term preservation.

---

## P4. Reproducibility

Generated artifacts should be reproducible from canonical sources.

---

## P5. Application Independence

No application owns canonical information.

Applications consume exported views.

---

## P6. Progressive Enrichment

Knowledge accumulates over time.

The system should support continual refinement without requiring redesign.

---

## P7. Extensibility

New metadata, object types, analyses, and applications should be accommodated without disrupting existing content.
---

## P8. Sandbox and Graduation

Exploratory development should take place in a structured sandbox rather than prematurely altering production artifacts.

Sandbox work is provisional. Experiments, discovery analyses, prototypes, and intermediate results may be discarded, superseded, or reorganized.

When an experiment demonstrates durable value, its useful artifacts should be deliberately graduated into the appropriate production area:

- implementation → `08_tools`
- verification → `07_tests`
- architectural or domain knowledge → `01_docs`
- operational results → `06_runtime`

Important discoveries should be preserved as knowledge even when the experimental implementation is discarded.

The development lifecycle is:

**Play → Discover → Test → Graduate → Operate**

The sandbox is a workshop, not a second production tree.
