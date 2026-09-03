# Date Model

**Status:** Current architectural baseline  
**Version:** V1 — evolving

## Purpose

Defines representation of recording dates when historical evidence has differing precision or agreement.

## Principle

The catalog must not manufacture precision that the evidence does not support.

## Date precision

At minimum:

- DAY — year, month, and day available
- MONTH — year and month available
- YEAR — year available
- UNSPECIFIED — date-like value does not fit the recognized representation
- NONE — no date available

Additional representations such as ranges or approximate dates may be introduced when required.

## Provisional dates

An imprecise date may be useful and valid as a provisional value.

For example, `1927` may be the best currently supported date even when an exact day is not known.

## Refinement

Later evidence may refine `1927` to `1927-05` or `1927-05-14`. The earlier observation remains part of the evidence history.

## Conflicting dates

Different sources may provide different dates. Retain the conflicting evidence and record the current interpretation rather than silently discarding one source's claim.

## Date and identity

Recording date may help distinguish Performances, but date precision must reflect actual evidence. An imprecise date must not be treated as exact merely because an implementation requires a key.

## Verification

The catalog should permit an assertion to remain provisional while additional research or source comparison is pending.

## Views

Different views may display dates at different levels of detail.
