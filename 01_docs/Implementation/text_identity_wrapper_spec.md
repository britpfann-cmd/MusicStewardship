# MusicStewardship Text Identity Wrapper — Initial Specification

## Purpose

Provide one reusable intake-stage utility for textual identity fields.

It produces three values for the MusicStewardship intake record:

1. **Original text** — exactly what the source supplied.
2. **Corrected text** — deterministic text/Unicode correction.
3. **Canonical reference/name** — the current best authority, or a provisional/unresolved result when no established authority is available.

The utility prepares these values. The ingest engine stores them. It does not perform database writes.

## Processing model

```text
source value

    |

    +------------------------------> original_text

    |

    v

text repair / Unicode normalization

    |

    +------------------------------> corrected_text

    |

    v

name / authority lookup

    |

    +------------------------------> canonical_ref / canonical_name