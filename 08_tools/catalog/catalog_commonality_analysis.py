#!/usr/bin/env python3
"""Analyze commonality and candidate sets in an ingested catalog population.

This is a diagnostic tool, not an identity resolver.

It reports:
- exact observed-value frequencies,
- inexpensive comparison-form frequencies,
- CI-level co-occurrence combinations,
- collision patterns,
- consolidated candidate CI sets with corroborating evidence.

It does not create, merge, or associate catalog entities.

A candidate set means only that two or more CatalogedInstances were reached
by the same comparison evidence. Candidate membership is not an identity
decision.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ANALYSIS_REVISION = "catalog_commonality_analysis.v0.2"

DEFAULT_COMBINATIONS = (
    ("title",),
    ("title", "orchestra_or_album_artist"),
    ("title", "orchestra_or_album_artist", "recording_date"),
    (
        "title",
        "orchestra_or_album_artist",
        "recording_date",
        "recording_identifier",
    ),
    ("title", "composer"),
    ("orchestra_or_album_artist", "singer"),
)

CANDIDATE_PATH_FIELDS = (
    "title",
    "orchestra_or_album_artist",
    "recording_date",
)

CORROBORATING_FIELDS = (
    "recording_identifier",
    "composer",
    "conductor",
)


def comparison_form(value: Any) -> str:
    """Return a cheap comparison form; never a canonical value."""
    if value is None:
        return ""

    text = unicodedata.normalize("NFKC", str(value))
    text = text.casefold()
    text = re.sub(r"[^\w]+", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def load_population(conn: sqlite3.Connection):
    rows = conn.execute(
        """
        SELECT
            observation_id,
            library_card_id,
            subject_id,
            observed_field,
            observed_value_json
        FROM catalog_observations
        WHERE subject_type = 'CATALOGED_INSTANCE'
        ORDER BY subject_id, observed_field, observation_id
        """
    ).fetchall()

    by_ci: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for observation_id, card_id, ci_id, field, value_json in rows:
        value = json.loads(value_json)
        by_ci[ci_id][field].append(
            {
                "observation_id": observation_id,
                "library_card_id": card_id,
                "value": value,
            }
        )

    return rows, by_ci


def fields_present(by_ci):
    return sorted(
        {
            field
            for field_map in by_ci.values()
            for field in field_map
        }
    )


def literal_analysis(by_ci):
    result = {}

    for field in fields_present(by_ci):
        occurrences = Counter()
        cis_by_value = defaultdict(set)

        for ci_id, field_map in by_ci.items():
            for obs in field_map.get(field, []):
                key = json.dumps(
                    obs["value"],
                    ensure_ascii=False,
                    sort_keys=True,
                )
                occurrences[key] += 1
                cis_by_value[key].add(ci_id)

        result[field] = [
            {
                "value": json.loads(key),
                "observation_count": count,
                "ci_count": len(cis_by_value[key]),
            }
            for key, count in occurrences.most_common()
        ]

    return result


def comparison_analysis(by_ci):
    result = {}

    for field in fields_present(by_ci):
        groups = defaultdict(
            lambda: {
                "observations": 0,
                "cis": set(),
                "literal_values": Counter(),
            }
        )

        for ci_id, field_map in by_ci.items():
            for obs in field_map.get(field, []):
                literal = str(obs["value"])
                form = comparison_form(literal)

                if not form:
                    continue

                group = groups[form]
                group["observations"] += 1
                group["cis"].add(ci_id)
                group["literal_values"][literal] += 1

        entries = []

        for form, group in groups.items():
            entries.append(
                {
                    "comparison_form": form,
                    "observation_count": group["observations"],
                    "ci_count": len(group["cis"]),
                    "literal_variant_count": len(
                        group["literal_values"]
                    ),
                    "literal_variants": [
                        {
                            "value": value,
                            "count": count,
                        }
                        for value, count
                        in group["literal_values"].most_common()
                    ],
                }
            )

        entries.sort(
            key=lambda x: (
                -x["ci_count"],
                -x["literal_variant_count"],
                x["comparison_form"],
            )
        )

        result[field] = entries

    return result


def comparison_tuples(field_map, fields):
    """Generate derived CI-level comparison tuples for requested fields."""
    value_lists = []

    for field in fields:
        values = [
            obs["value"]
            for obs in field_map.get(field, [])
        ]

        if not values:
            return []

        value_lists.append(values)

    tuples = [()]

    for values in value_lists:
        tuples = [
            prior + (value,)
            for prior in tuples
            for value in values
        ]

    return [
        tuple(comparison_form(value) for value in values_tuple)
        for values_tuple in tuples
    ]


def combination_groups(by_ci, fields):
    groups = defaultdict(set)

    for ci_id, field_map in by_ci.items():
        for comparison_tuple in comparison_tuples(
            field_map,
            fields,
        ):
            groups[comparison_tuple].add(ci_id)

    return groups


def combination_analysis(by_ci, combinations):
    result = {}

    for fields in combinations:
        key_name = " + ".join(fields)
        groups = combination_groups(by_ci, fields)

        entries = [
            {
                "comparison_values": dict(zip(fields, values)),
                "ci_count": len(ci_ids),
            }
            for values, ci_ids in groups.items()
        ]

        entries.sort(
            key=lambda x: (
                -x["ci_count"],
                json.dumps(
                    x["comparison_values"],
                    ensure_ascii=False,
                    sort_keys=True,
                ),
            )
        )

        result[key_name] = {
            "basis": "derived_ci_level_cooccurrence",
            "groups": entries,
        }

    return result


def comparison_values_for_ci(field_map, field):
    return sorted(
        {
            comparison_form(obs["value"])
            for obs in field_map.get(field, [])
            if comparison_form(obs["value"])
        }
    )


def corroboration_for_set(by_ci, ci_ids):
    result = {}

    for field in CORROBORATING_FIELDS:
        values_by_ci = {
            ci_id: comparison_values_for_ci(
                by_ci[ci_id],
                field,
            )
            for ci_id in sorted(ci_ids)
        }

        nonempty = [
            set(values)
            for values in values_by_ci.values()
            if values
        ]

        all_present = (
            len(nonempty) == len(ci_ids)
            and len(ci_ids) > 0
        )

        shared = (
            sorted(set.intersection(*nonempty))
            if all_present
            else []
        )

        result[field] = {
            "all_members_have_value": all_present,
            "shared_comparison_values": shared,
            "exact_comparison_agreement": (
                all_present
                and len(shared) > 0
                and len(
                    {
                        tuple(values)
                        for values in values_by_ci.values()
                    }
                ) == 1
            ),
            "values_by_ci": values_by_ci,
        }

    return result


def candidate_set_analysis(by_ci):
    """Consolidate repeated comparison paths by identical CI membership."""
    groups = combination_groups(
        by_ci,
        CANDIDATE_PATH_FIELDS,
    )

    repeated = {
        path: frozenset(ci_ids)
        for path, ci_ids in groups.items()
        if len(ci_ids) > 1
    }

    paths_by_ci_set = defaultdict(list)

    for path, ci_set in repeated.items():
        paths_by_ci_set[ci_set].append(path)

    entries = []

    for ci_set, paths in paths_by_ci_set.items():
        sorted_cis = sorted(ci_set)
        sorted_paths = sorted(paths)

        entries.append(
            {
                "member_ci_ids": sorted_cis,
                "member_count": len(sorted_cis),
                "comparison_path_count": len(sorted_paths),
                "comparison_paths": [
                    dict(
                        zip(
                            CANDIDATE_PATH_FIELDS,
                            path,
                        )
                    )
                    for path in sorted_paths
                ],
                "corroboration": corroboration_for_set(
                    by_ci,
                    sorted_cis,
                ),
            }
        )

    entries.sort(
        key=lambda x: (
            -x["member_count"],
            -x["comparison_path_count"],
            x["member_ci_ids"],
        )
    )

    return {
        "basis": "derived_ci_level_cooccurrence",
        "identity_effect": "NONE",
        "candidate_path_fields": list(
            CANDIDATE_PATH_FIELDS
        ),
        "repeated_comparison_group_count": len(repeated),
        "distinct_candidate_set_count": len(entries),
        "candidate_sets": entries,
    }


def collision_analysis(by_ci):
    title_to_orchestras = defaultdict(set)
    title_orchestra_to_dates = defaultdict(set)

    for field_map in by_ci.values():
        titles = comparison_values_for_ci(
            field_map,
            "title",
        )
        orchestras = comparison_values_for_ci(
            field_map,
            "orchestra_or_album_artist",
        )
        dates = comparison_values_for_ci(
            field_map,
            "recording_date",
        )

        for title in titles:
            for orchestra in orchestras:
                title_to_orchestras[title].add(orchestra)

                for date in dates:
                    title_orchestra_to_dates[
                        (title, orchestra)
                    ].add(date)

    title_collisions = [
        {
            "title_comparison_form": title,
            "distinct_orchestra_count": len(orchestras),
            "orchestra_comparison_forms": sorted(orchestras),
        }
        for title, orchestras in title_to_orchestras.items()
        if len(orchestras) > 1
    ]

    title_collisions.sort(
        key=lambda x: (
            -x["distinct_orchestra_count"],
            x["title_comparison_form"],
        )
    )

    performance_collisions = [
        {
            "title_comparison_form": title,
            "orchestra_comparison_form": orchestra,
            "distinct_date_count": len(dates),
            "date_comparison_forms": sorted(dates),
        }
        for (title, orchestra), dates
        in title_orchestra_to_dates.items()
        if len(dates) > 1
    ]

    performance_collisions.sort(
        key=lambda x: (
            -x["distinct_date_count"],
            x["title_comparison_form"],
            x["orchestra_comparison_form"],
        )
    )

    return {
        "same_title_multiple_orchestras": title_collisions,
        "same_title_orchestra_multiple_dates": performance_collisions,
    }


def population_summary(conn, rows, by_ci):
    return {
        "library_cards": conn.execute(
            "SELECT COUNT(*) FROM library_cards"
        ).fetchone()[0],
        "cataloged_instances": conn.execute(
            "SELECT COUNT(*) FROM cataloged_instances"
        ).fetchone()[0],
        "observations": len(rows),
        "observed_fields": fields_present(by_ci),
    }


def analyze_database(conn):
    rows, by_ci = load_population(conn)

    return {
        "analysis_revision": ANALYSIS_REVISION,
        "identity_effect": "NONE",
        "population": population_summary(
            conn,
            rows,
            by_ci,
        ),
        "literal_commonality": literal_analysis(by_ci),
        "comparison_commonality": comparison_analysis(by_ci),
        "combination_commonality": combination_analysis(
            by_ci,
            DEFAULT_COMBINATIONS,
        ),
        "candidate_sets": candidate_set_analysis(by_ci),
        "collisions": collision_analysis(by_ci),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Catalog population commonality analysis"
    )
    parser.add_argument("database", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    conn = sqlite3.connect(args.database)

    try:
        report = analyze_database(conn)
    finally:
        conn.close()

    args.output.parent.mkdir(parents=True, exist_ok=True)

    args.output.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    print("Catalog commonality analysis")
    print(f"Revision: {report['analysis_revision']}")
    print(f"Database: {args.database}")
    print(f"Output:   {args.output}")
    print(
        "CIs:     ",
        report["population"]["cataloged_instances"],
    )
    print(
        "Obs:     ",
        report["population"]["observations"],
    )

    for name, data in report[
        "combination_commonality"
    ].items():
        repeated = sum(
            1
            for group in data["groups"]
            if group["ci_count"] > 1
        )
        print(f"Repeated {name}: {repeated}")

    candidate = report["candidate_sets"]

    print(
        "Repeated comparison groups:",
        candidate["repeated_comparison_group_count"],
    )
    print(
        "Distinct candidate CI sets:",
        candidate["distinct_candidate_set_count"],
    )

    print(
        "Title collisions (multiple orchestras):",
        len(
            report["collisions"][
                "same_title_multiple_orchestras"
            ]
        ),
    )

    print(
        "Title+orchestra collisions (multiple dates):",
        len(
            report["collisions"][
                "same_title_orchestra_multiple_dates"
            ]
        ),
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
