# Foundation — From Collection to Exhibition

**Status:** Foundational project principle  
**Established:** 2026-09-01  
**Scope:** Entire MusicStewardship project

## 1. The Fundamental Insight

MusicStewardship is not simply a project to build a database of tango recordings.

It is an archaeological knowledge project.

We begin with a collection of individual surviving objects and observations:
recordings, files, source records, names, dates, attributions, external
databases, and other fragments of evidence.

Individually, these objects are artifacts. Their greater value emerges when
their relationships, context, provenance, and uncertainty are reconstructed.

The purpose of MusicStewardship is analogous to taking a collection of
artifacts out of a museum basement and turning them into an exhibition:

> **not merely displaying the objects, but reconstructing enough of their
> relationships and context to make the civilization they represent
> intelligible.**

The "exhibition" is the current, usable representation of our understanding
of the tango music world. The underlying research record remains the archive
from which that understanding was constructed.

## 2. The Fundamental Obligation

The process of interpretation must never destroy, lose, conceal, or silently
alter evidence from which the interpretation was derived.

The project must preserve the distinction between:

- what was observed;
- what a source reported;
- what evidence supports an interpretation;
- what we currently believe;
- how that belief has evolved.

A current catalog entry may therefore change without rewriting the historical
record of the evidence and interpretation that preceded it.

## 3. Evolutionary Knowledge

MusicStewardship does not require complete or certain knowledge before it can
catalog an observation.

When an observation cannot yet be associated with an established entity, the
system may create a provisional entity.

Additional observations and evidence can then be accumulated.

Associations and interpretations may subsequently be:

- strengthened;
- confirmed;
- refined;
- reassigned;
- split;
- merged;
- retired.

A provisional conclusion is useful knowledge, not an error.

> **An uncertain catalog that can learn is preferable to a system that refuses
> to catalog until certainty is achieved.**

## 4. Current Understanding and Historical Record

The current catalog represents our best understanding at the present moment.

CSV datasets are current snapshots of that understanding. They are not
history logs and should remain simple and usable.

Historical evolution and provenance are retained separately and should be
readily accessible when needed.

This permits the ordinary user to ask:

> What do we currently believe?

without requiring examination of how we arrived there.

The curious researcher can then ask:

> Why do we believe that?

and have access to the supporting evidence and history.

## 5. Archaeological Design Review

The archaeological perspective is not merely documentation. It is an
ongoing design constraint.

As MusicStewardship develops, each significant component and design decision
should be back-checked against this foundation.

At minimum, ask:

1. **What was actually observed?**
2. **What did the source actually say?**
3. **What are we currently interpreting it to mean?**
4. **What evidence supports that interpretation?**
5. **Can a future researcher recover the relevant evidence and context?**
6. **Could this design lose, ignore, obscure, or silently alter information
   that may later prove significant?**

If the answer to the final question is yes, the design requires reconsideration.

## 6. Context Matters

An artifact without context may have much less evidentiary value than the
same artifact with its relationships and circumstances preserved.

For MusicStewardship, source context may include:

- the source itself;
- source location;
- source record or page;
- source terminology;
- neighboring records;
- reported dates;
- orchestra/group;
- singer/person information;
- matrix, take, or record identifiers;
- release information;
- provenance;
- other evidence associated with the observation.

Context should not be discarded merely because it is not needed for the
current catalog view.

## 7. Absence Is Not Negative Evidence

The absence of information in a source must not silently become a statement
that the underlying fact did not exist.

For example:

> A source that does not provide a singer does not establish that the
> performance had no singer.

Likewise, an absent recording date means that the source did not establish
the date; it does not establish that no recording date existed.

The catalog should distinguish missing observation from negative assertion.

## 8. Source Record and Canonical Interpretation

Source-derived information and canonical interpretation have different roles.

A source record should preserve what was decoded or observed.

The canonical catalog expresses our current interpretation of the accumulated
evidence.

Source-derived CSV datasets may therefore remain stable even when the
canonical interpretation changes.

The canonical representation can evolve without rewriting the source record.

## 9. The Exhibition and the Archive

MusicStewardship has two complementary aspects:

### The Exhibition

The current catalog provides:

- current knowledge;
- understandable organization;
- usable CSV datasets;
- relationships among entities;
- the best current representation of the tango music world.

### The Archive

The research record preserves:

- source observations;
- source context;
- provenance;
- evidence;
- historical interpretations;
- significant investigative artifacts;
- useful intermediate or discarded approaches where their preservation has
  evidentiary or reproducibility value.

The exhibition should be easy to use.

The archive should remain available for investigation.

Neither should be confused with the other.

## 10. Stewardship Principle

The goal is not to claim that the reconstruction is permanently correct.

The goal is to create a representation that can become **more correct as
knowledge accumulates without losing the evidence that made correction
possible**.

That is the central stewardship responsibility of MusicStewardship.

## 11. Design Test

Every future architectural or implementation proposal should be capable of
answering:

> **Does this help us turn a collection of surviving artifacts into a more
> intelligible representation of the tango music civilization while
> preserving the evidence, context, uncertainty, and ability to revise our
> understanding?**

If it does, it is consistent with the foundation.

If it makes the present representation easier at the cost of losing or
obscuring potentially meaningful evidence, it conflicts with the foundation
and should be reconsidered.
