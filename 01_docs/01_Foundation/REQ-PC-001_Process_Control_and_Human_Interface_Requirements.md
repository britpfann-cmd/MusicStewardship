# Process Control and Human Interface Requirements

**Document ID:** REQ-PC-001
**Status:** Draft
**Revision:** A
**Date:** 2026-09-09

## 1. Purpose

The MusicStewardship ingestion and catalog-construction system shall maintain persistent process-control information describing the work performed by the system.

Process control is not merely an internal progress log. It shall provide the operational state from which the human interface can present, inspect, review, resume, and manage stewardship work.

## 2. Architectural Position

Process control is a cross-cutting subsystem serving all major processing stages:

1. source acquisition and staging;
2. source-specific interpretation through a Rosetta Stone rule set;
3. generic transformation;
4. catalog interchange production;
5. reference-library import and entity management;
6. subsequent reprocessing when source information or rules change.

The process-control record shall remain distinct from the catalog data itself. It records how work was performed, what state that work is in, and what dependencies or exceptions affect it.

## 3. Requirements

### REQ-PC-001 — Persistent Operational State

The system shall persist the state of processing sufficiently to determine what work has been completed, what remains, and what requires attention.

### REQ-PC-002 — Work Item Traceability

Each significant processing operation shall be attributable to its input, processing stage, rule or rule-set version, result, and relevant provenance.

### REQ-PC-003 — Progress

The system shall record processing progress at a granularity sufficient to report completed, pending, failed, skipped, and exception work.

### REQ-PC-004 — Resumption

The system shall permit processing to resume from a previously recorded stopping point without unnecessarily repeating successfully completed work.

### REQ-PC-005 — Exceptions

The system shall record exceptions and unresolved conditions in a form that permits later human inspection and subsequent processing.

### REQ-PC-006 — Change Detection and Recursive Processing

When source information, interpretation rules, or other inputs change, the system shall be able to identify affected derived work and recursively reprocess affected descendants while leaving unaffected work available for reuse.

### REQ-PC-007 — Provenance and Reproducibility

Process-control records shall retain sufficient information to establish how a derived result was produced and to support reproduction or investigation of that result.

### REQ-PC-008 — Human Interface Foundation

The process-control state shall be usable as the foundation for a human operational interface. The interface shall be able to expose, at minimum:

- current processing state;
- progress;
- pending work;
- exceptions;
- items requiring review;
- changes requiring reprocessing;
- available resume points;
- relevant provenance and processing history.

### REQ-PC-009 — Machine/Human Common State

The human interface shall present the underlying process-control state rather than maintain an independent, conflicting representation of processing status.

### REQ-PC-010 — Initial Interchange Representation

Where practical during development, process-control information shall be representable in human-readable, machine-readable interchange files such as CSV. A later database implementation may provide richer querying and reporting without changing the underlying architectural meaning of the process-control information.

### REQ-PC-011 — Auditability

The system shall preserve sufficient historical process information to determine what operation occurred, when it occurred, against which inputs, and under which applicable rule or implementation version.

### REQ-PC-012 — Non-Destructive Operation

Process control shall not require destruction of source evidence or previously produced representations. New processing shall create or supersede derived results according to recorded dependencies and provenance.

## 4. Conceptual Process-Control Record

A process-control implementation should be capable of representing concepts equivalent to:

- work item;
- process run;
- operation;
- input;
- output;
- state;
- result;
- exception;
- dependency;
- rule/rule-set version;
- provenance;
- checkpoint;
- change/reprocessing trigger.

These are implementation concepts, not a final database schema.

## 5. Relationship to the Ingestion Architecture

The ingestion architecture separates source-specific rules from common processing machinery. Process control shall preserve that distinction by recording which source rule set and version governed a transformation while allowing the processing engine itself to remain common.

The process-control layer therefore provides the operational bridge between:

**source evidence → interpretation → transformation → catalog interchange → reference-library management**

without becoming itself a source-specific rule system.

## 6. Design Principle

> **Process control is the operational state of MusicStewardship. Its machine-readable record is simultaneously the foundation for the human operational interface.**

This requirement document establishes the need and architectural boundary. Detailed schemas, user-interface designs, workflow state machines, and implementation mechanisms belong in subsequent design and implementation documents.
