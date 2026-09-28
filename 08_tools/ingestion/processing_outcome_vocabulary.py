"""Generic processing-outcome vocabulary.

The vocabulary is deliberately separate from information_class.
Information class answers "what role does this information have?"
Processing outcome answers "what happened to it?"
Outcome reason explains notable/unresolved outcomes.

This module is intentionally dependency-free so the engine and reporting code can
share the same controlled vocabulary.
"""

INFORMATION_CLASSES = frozenset({
    "CORE",
    "ASSOCIATED",
    "RESIDUAL",
})

PROCESSING_OUTCOMES = frozenset({
    "DECODED",
    "DERIVED",
    "PRESERVED",
    "NOT_ATTEMPTED",
    "PARTIAL",
    "UNDECODABLE",
    "CONFLICT",
    "REVIEW",
})

OUTCOME_REASONS = frozenset({
    "OUT_OF_SCOPE",
    "NO_CAPABILITY",
    "DECODER_FAILURE",
    "AMBIGUOUS",
    "CONFLICTING_EVIDENCE",
    "HUMAN_REQUIRED",
    "PRESERVATION",
    "OTHER",
})

# Outcomes that normally require operational attention.
ATTENTION_OUTCOMES = frozenset({
    "PARTIAL",
    "UNDECODABLE",
    "CONFLICT",
    "REVIEW",
})

# Preservation is expected non-destructive behavior, not an exception.
NON_EXCEPTION_OUTCOMES = frozenset({
    "DECODED",
    "DERIVED",
    "PRESERVED",
    "NOT_ATTEMPTED",
})


def validate_information_class(value):
    if value not in INFORMATION_CLASSES:
        raise ValueError(f"Unknown information class: {value!r}")
    return value


def validate_processing_outcome(value):
    if value not in PROCESSING_OUTCOMES:
        raise ValueError(f"Unknown processing outcome: {value!r}")
    return value


def validate_outcome_reason(value):
    if value and value not in OUTCOME_REASONS:
        raise ValueError(f"Unknown outcome reason: {value!r}")
    return value
