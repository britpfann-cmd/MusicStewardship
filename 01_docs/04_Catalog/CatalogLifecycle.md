# Catalog Lifecycle

**Status:** Current architectural baseline  
**Version:** V1 — evolving

## Purpose

Defines the incremental lifecycle by which observations become catalog entities and instances, and how assignments may be corrected as the catalog grows.

## Basic lifecycle

    source observation
           |
           v
    preserve source evidence
           |
           v
    identify candidate entity
           |
           +---- existing entity supported ----> associate observation
           |
           +---- no suitable entity -----------> create entity
                                                   |
                                                   v
                                            stable internal ID
                                                   |
                                                   v
                                            cataloged instance

The initial association remains subject to later review.

## Vetted foundation

The catalog will normally begin with information believed to be relatively well vetted. Established information becomes useful evidence and context when processing later incremental sources.

Most later observations may belong to previously established entities, but some will not.

## Convenient initial construction

The common case should be easy:

> add this observation as another instance of an already identified entity.

This avoids unnecessary duplicates while allowing catalog construction to proceed efficiently. The assignment is not irreversible.

## Later correction

New evidence may require confirming an association, refining an attribute, changing a provisional interpretation, reassigning an observation, creating a previously unrecognized entity, splitting an incorrectly merged entity, or merging entities later established to be identical.

Corrections must preserve observations and provenance explaining the earlier state.

## Self-correcting model

The catalog intentionally tolerates noise. Convenience favors a useful initial assignment when evidence is sufficient for a reasonable working conclusion. Accuracy improves as additional sources and evidence accumulate.

The system therefore separates observation, evidence, current interpretation, and stable identity.

## Source convergence

Each source may have different cataloging practices. Source-specific ingestion translates observations into the common catalog while retaining source-specific evidence.

## Entity relationships

The lifecycle applies to Songs, People, Groups, Events, Performances, and other canonical entities.

It must accommodate both:

    different names -> same entity

and:

    same name -> different entities

## Outputs

Views consume the common catalog. Purpose-specific information belongs in views rather than core identity. The DJ-organized directory tree is an output of the DJ view.

## Future identification

Acoustic profiles and other derived evidence may assist in recognizing additional instances of previously identified Performances. Such evidence becomes part of the evidence base rather than silently changing the underlying source observation.


---

## V2 Design Principle — Evolutionary Knowledge Lifecycle

The catalog is an evolving body of knowledge rather than a collection of
one-time identity decisions.

The lifecycle begins with an observation, not with certainty:

```text
source observation
       |
       v
preserve source evidence
       |
       v
evaluate available evidence
       |
       +---- established entity supported ----> associate
       |
       +---- no established entity ------------> create provisional entity
                                                    |
                                                    v
                                             stable identity
                                                    |
                                                    v
                                             more instances
                                                    +
                                                 evidence
                                                    |
                                                    v
                                           revise understanding
```

The first provisional entity provides a useful home for what is known at that
moment. Subsequent instances and evidence progressively develop the catalog.

An association may therefore evolve through states such as:

- initial provisional association;
- additional supporting instances;
- confirmation;
- refinement;
- reassignment;
- split;
- merge;
- retirement.

These are changes in the catalog's knowledge, not necessarily changes in the
underlying historical objects.

### Current state and history

The ordinary catalog answers:

> What do we currently believe?

The current CSV snapshot records that present state.

Historical association changes are retained separately so that a researcher
can ask:

> How did we get here, and why?

History should be readily accessible without making routine catalog use
temporal or cumbersome.

### Design philosophy

> **MusicStewardship does not require complete knowledge before cataloging
> can begin. It creates useful provisional knowledge and allows that
> knowledge to become more accurate as evidence accumulates.**

This principle is fundamental to the project's archaeological approach.


---

## V3 Addendum — 2026-10-02 Population-Driven Knowledge Growth

The base catalog is populated before complete identity resolution. Each ingested submission creates or contributes to a persistent CatalogedInstance whose current state may contain provisional upward associations toward Recording, Performance, Work, Release, Person, Ensemble, and other entities.

As entries accumulate, provisional structures may coalesce. Coalescence can occur independently at different entity levels and remains reversible when later evidence requires a split or reassignment.

The preferred development lifecycle is now:

```text
preserve complete source population
        -> create CatalogedInstances/provisionals
        -> scan population for exact/similar candidates
        -> report candidate counts/clusters
        -> harvest economical external seed evidence
        -> reconcile/coalesce where justified
        -> investigate the smaller difficult residual population
```

Externally sourced seeds and entities first inferred from owned material participate in the same catalog. Seed origin is provenance, not authority.

Whole-population ingestion also validates the E-R model itself. Recurring residuals, forced mappings, and failures are evidence for model/grammar/decoder remediation rather than reasons to discard source material.
