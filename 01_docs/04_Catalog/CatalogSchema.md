# Catalog Schema — V2 Clarifications

## CSV as Public Interface

CSV datasets are the public and interchange representation of the
MusicStewardship catalog.

A published CSV dataset is a **current snapshot** of catalog state at the
time it is produced.

CSV is intentionally:

- human-readable;
- machine-readable;
- portable;
- inspectable;
- archivable;
- usable without knowledge of internal implementation.

This principle grew directly from the project's successful use of flat CSV
datasets produced by decoding external sources such as tango-dj.at HTML.

Internal processing may use JSON, SQLite, in-memory structures, or other
representations when those are better suited to the task. Internal
representations are implementation choices and do not replace the CSV public
interface.

## Current Snapshot, Not History Log

CSV snapshot tables should not contain historical versions merely because
the catalog evolves.

The normal catalog question is:

> What do we currently believe?

The answer should be easy to obtain from the current snapshot.

Historical evolution is retained separately. It records how an assertion or
association changed and, where appropriate, when and why it changed.

History should be easy to access for users who need to understand or audit
the current state, but ordinary catalog use should not require navigating
history.

This is the project's **kind-to-the-curious** principle:

> History is available when wanted, but does not burden ordinary use.

## Association State

An association expresses the catalog's current best interpretation at a
particular point in time.

For example, a CatalogedInstance may currently be associated with a
particular Song or Performance.

That current association is represented in the current catalog snapshot.

If later evidence causes the association to be refined, confirmed,
reassigned, split, or otherwise changed, the current snapshot changes while
the historical evolution is retained separately.

The system therefore distinguishes:

- **current association** — what we believe now;
- **association history** — how that belief evolved;
- **evidence/provenance** — why a particular interpretation was supported.

The historical record must not require the current CSV tables to become
temporal or cumbersome.

## Identity and Names

Names are observations/representations, not permanent entity identities.

The catalog must support both:

    different names -> same entity

and:

    same name -> different entities

A convenient initial assignment may associate a new observation with an
already identified entity when evidence supports that interpretation.

That assignment must remain correctable as new evidence accumulates.

The original source observation and its provenance remain preserved when the
current association changes.

## Design Intent

The catalog is deliberately optimized for the common question:

> What do we currently believe?

while retaining enough separate history and provenance to answer:

> Why do we believe that?

when someone is curious, reviewing, or auditing the catalog.
