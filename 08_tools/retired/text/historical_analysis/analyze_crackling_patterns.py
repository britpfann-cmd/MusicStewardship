#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Crackling Tunes Structural Pattern Analysis

Stage 1 pattern-discovery analysis for the Crackling Tunes catalog.

This report identifies recurring structural patterns in the curated
Crackling Tunes metadata. It does not establish transformation rules.

The purpose is to discover candidate source conventions that may later
inform ingest mapping and transposition rules.

Input:
    08_tools/text/tests/crackling_catalog_text.csv

Output:
    08_tools/text/tests/crackling_pattern_analysis.md
"""

from pathlib import Path
import csv
from collections import Counter, defaultdict


INPUT = Path("08_tools/text/tests/crackling_catalog_text.csv")
OUTPUT = Path("08_tools/text/tests/crackling_pattern_analysis.md")


def load_records():
    """Load extracted metadata records from CSV."""
    with INPUT.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def normalize(value):
    """Conservative whitespace normalization for analysis."""
    return " ".join(value.split()).strip()


def split_artist(value):
    """
    Split the ARTIST value using the observed '/' separator.

    This is an analytical hypothesis, not yet an established
    transformation rule.
    """
    value = normalize(value)

    if not value:
        return []

    return [part.strip() for part in value.split("/")]


def classify_vocal_component(value):
    """
    Classify a post-ensemble ARTIST component.

    Instrumental terminology is treated as a structural indicator,
    not as a singer name.
    """
    value = normalize(value).casefold()

    if value in {"instrumental", "instr.", "instr"}:
        return "INSTRUMENTAL"

    return "PERSON_OR_OTHER"


def main():
    records = load_records()

    # Reconstruct one record per catalog/file combination.
    by_source_file = defaultdict(dict)

    for record in records:
        source_file = record["source_file"]

        by_source_file[source_file][record["field_name"]] = (
            record["original_text"]
        )

    artist_values = Counter()
    component_counts = Counter()
    vocal_patterns = Counter()
    ensemble_artist = Counter()
    albumartist_values = Counter()
    ensemble_pairs = Counter()
    singer_values = Counter()

    for source_file, fields in by_source_file.items():
        artist = fields.get("ARTIST", "")
        albumartist = fields.get("ALBUMARTIST", "")

        if artist:
            artist_values[artist] += 1

            components = split_artist(artist)

            component_counts[len(components)] += 1

            if components:
                ensemble = components[0]

                ensemble_artist[ensemble] += 1

                classifications = tuple(
                    classify_vocal_component(component)
                    for component in components[1:]
                )

                vocal_patterns[classifications] += 1

                for singer in components[1:]:
                    if (
                        classify_vocal_component(singer)
                        == "PERSON_OR_OTHER"
                    ):
                        singer_values[singer] += 1

        if albumartist:
            albumartist_values[albumartist] += 1

        if artist and albumartist:
            components = split_artist(artist)

            if components:
                ensemble = components[0]

                ensemble_pairs[(ensemble, albumartist)] += 1

    lines = []

    lines.append("# Crackling Tunes Structural Pattern Analysis")
    lines.append("")

    lines.append(
        "This report identifies recurring structural patterns in the "
        "curated Crackling Tunes metadata. It does not establish "
        "transformation rules."
    )

    lines.append("")

    lines.append(
        "The purpose is to discover recurring source conventions that "
        "may later inform ingest mapping and transposition rules."
    )

    lines.append("")

    # ------------------------------------------------------------------
    # Dataset
    # ------------------------------------------------------------------

    lines.append("## Dataset")
    lines.append("")

    lines.append(
        f"- Source/file records: **{len(by_source_file)}**"
    )

    lines.append("")

    # ------------------------------------------------------------------
    # ARTIST component counts
    # ------------------------------------------------------------------

    lines.append("## ARTIST Component Counts")
    lines.append("")

    lines.append("| Components | Recordings |")
    lines.append("|---:|---:|")

    for number, count in sorted(component_counts.items()):
        lines.append(f"| {number} | {count} |")

    lines.append("")

    # ------------------------------------------------------------------
    # Vocal component patterns
    # ------------------------------------------------------------------

    lines.append("## Vocal-Component Patterns")
    lines.append("")

    lines.append(
        "The first ARTIST component is provisionally treated as the "
        "ensemble portion. Components following it are classified "
        "for analytical purposes only."
    )

    lines.append("")

    lines.append("| Pattern after ensemble | Recordings |")
    lines.append("|---|---:|")

    for pattern, count in vocal_patterns.most_common():
        if pattern:
            label = " / ".join(pattern)
        else:
            label = "(none)"

        lines.append(f"| `{label}` | {count} |")

    lines.append("")

    # ------------------------------------------------------------------
    # Ensemble portions
    # ------------------------------------------------------------------

    lines.append(
        "## Most Common Ensemble Portions of ARTIST"
    )

    lines.append("")

    lines.append("| Frequency | Ensemble portion |")
    lines.append("|---:|---|")

    for value, count in ensemble_artist.most_common(40):
        lines.append(f"| {count} | `{value}` |")

    lines.append("")

    # ------------------------------------------------------------------
    # Singer/non-ensemble components
    # ------------------------------------------------------------------

    lines.append(
        "## Most Common Singer / Non-Ensemble Components"
    )

    lines.append("")

    lines.append("| Frequency | Component |")
    lines.append("|---:|---|")

    for value, count in singer_values.most_common(40):
        lines.append(f"| {count} | `{value}` |")

    lines.append("")

    # ------------------------------------------------------------------
    # ARTIST versus ALBUMARTIST
    # ------------------------------------------------------------------

    lines.append(
        "## ARTIST Ensemble vs ALBUMARTIST"
    )

    lines.append("")

    lines.append(
        "These are the most frequent pairings between the provisional "
        "ensemble portion of ARTIST and the stored ALBUMARTIST value."
    )

    lines.append("")

    lines.append(
        "| Frequency | ARTIST ensemble portion | ALBUMARTIST |"
    )

    lines.append(
        "|---:|---|---|"
    )

    for (
        artist_ensemble,
        albumartist,
    ), count in ensemble_pairs.most_common(60):

        lines.append(
            f"| {count} | `{artist_ensemble}` | `{albumartist}` |"
        )

    lines.append("")

    # ------------------------------------------------------------------
    # Observations
    # ------------------------------------------------------------------

    lines.append(
        "## Observations Requiring Further Investigation"
    )

    lines.append("")

    lines.append(
        "- Determine whether `/` consistently separates ensemble "
        "from vocal participant(s)."
    )

    lines.append(
        "- Determine whether `Instrumental` and `Instr.` are "
        "equivalent source conventions."
    )

    lines.append(
        "- Determine whether multiple post-ensemble components "
        "represent multiple singers or other roles."
    )

    lines.append(
        "- Determine how reliably the first ARTIST component "
        "corresponds to the ensemble represented by ALBUMARTIST."
    )

    lines.append(
        "- Compare ARTIST structure with filename structure as "
        "an independent source of evidence."
    )

    lines.append(
        "- Preserve exceptions rather than forcing them into a "
        "dominant pattern."
    )

    lines.append("")

    lines.append(
        "## Interpretation Principle"
    )

    lines.append("")

    lines.append(
        "A recurring source pattern should be treated as a candidate "
        "interpretation until it has been evaluated across multiple "
        "releases and known exceptions."
    )

    lines.append("")

    lines.append(
        "Pattern discovery precedes transformation-rule definition."
    )

    lines.append("")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(f"Wrote: {OUTPUT}")


if __name__ == "__main__":
    main()