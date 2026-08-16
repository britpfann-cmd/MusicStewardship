# Future Performance Model Topics

## Purpose

This note captures concepts that emerged during development of the Performance Model but are not yet sufficiently understood or mature to warrant formal modeling. These topics should be revisited as practical experience accumulates.

## Performance Structure vs. Performance Instance

The current model focuses on reusable performance structures. Future work should examine the distinction between:

* Performance Structure — a reusable design or plan.
* Performance Instance — a specific realization of that structure during an actual event.

Questions:

* What information belongs only to a specific performance instance?
* How are deviations from the planned structure represented?
* How are observations linked back to the originating structure?

## Experience vs. Knowledge

The project increasingly distinguishes between experience and knowledge.

Working hypothesis:

* Experience represents what occurred.
* Knowledge represents what has been learned from experience.

Questions:

* How should experience be captured?
* How does experience become knowledge?
* How are competing interpretations represented?

## Reuse at Multiple Levels

The model currently assumes that performance components can be reused.

Potential reusable elements include:

* Track
* Tanda
* Interlude
* Performance Segment
* Performance Structure

Questions:

* What information should remain attached to reusable components?
* How are modifications and variations tracked?
* When does adaptation create a new component?

## Stewardship Cycle

An emerging pattern appears repeatedly throughout the project:

Collection
→ Performance Structure
→ Performance
→ Observation
→ Knowledge
→ Refinement
→ Improved Performance Structure

This cycle may eventually become a foundational concept within MusicStewardship.

Questions:

* Is the cycle universal across all stewardship activities?
* What artifacts are produced at each stage?
* How should the cycle be represented within the model?

## Intent and Rationale

Performance structures capture more than sequence.

Future work should examine how to preserve:

* Intent
* Context
* Design rationale
* Expected outcomes
* Lessons learned

Questions:

* How much rationale should be captured?
* What is the relationship between rationale and observation?
* How can rationale remain useful without becoming burdensome to record?

## Status

These topics are exploratory and do not represent approved architectural decisions. They are retained to guide future investigation and to preserve insights that emerged during Performance Model development.
