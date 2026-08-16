# ADR-0005: Arc as the Recursive Programmatic Unit

## Status

Accepted

## Context

Early versions of the Performance Model used **Sequence** as the principal mechanism for grouping ordered program elements. As the model developed, it became clear that simple ordering was insufficient to express an important characteristic of a musical event: the intentional progression or trajectory created by the DJ.

A Sequence answers the structural question:

> What comes next?

The Performance Model also needs to represent the conceptual question:

> What larger musical or programmatic trajectory does this progression constitute?

An event may need to be considered at multiple scales: an individual Tanda, a short progression of Tandas, a larger portion of an evening, or the complete event. The same recursive structure should support all of these scales without flattening their relationships.

## Decision

The Performance Model adopts **Arc** as the recursive conceptual unit for a meaningful musical or programmatic trajectory.

An Arc may contain:

* Tandas;
* Interludes;
* other nested Arcs; and
* ordered combinations of these elements.

**Sequence** remains a structural concept representing ordered elements. It is not synonymous with Arc.

The distinction is:

* **Sequence** expresses order.
* **Arc** expresses meaningful musical or programmatic trajectory through that order.

An Event is ultimately represented by its tree of Arcs, Tandas, Interludes, and their referenced recordings.

## Rationale

This distinction preserves both the structural and semantic dimensions of the performance model.

It allows the model to represent the recursive nature of DJ planning and performance without requiring every ordered grouping to carry the stronger semantic meaning of an Arc.

It also keeps the model independent of  playback applications, whose representations may be flatter or use different terminology.

## Consequences

The Performance Model becomes capable of representing meaningful structure at multiple scales while preserving the distinction between simple ordering and intentional trajectory.

Future implementations must preserve the distinction between Sequence and Arc rather than treating them as interchangeable terms.

Existing Sequence concepts may remain useful where only ordering is significant.

## Related Concepts

* Event
* Tanda
* Interlude
* Track Reference
* Performance Tree
