import importlib.util
import json
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

MODULE_PATH = (
    ROOT
    / "08_tools"
    / "catalog"
    / "catalog_commonality_analysis.py"
)

spec = importlib.util.spec_from_file_location(
    "catalog_commonality_analysis",
    MODULE_PATH,
)
analysis = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(analysis)


def add_observation(
    conn,
    observation_id,
    card_id,
    ci_id,
    field,
    value,
):
    conn.execute(
        """
        INSERT INTO catalog_observations (
            observation_id,
            library_card_id,
            subject_type,
            subject_id,
            observed_field,
            observed_value_json,
            observed_at
        )
        VALUES (?, ?, 'CATALOGED_INSTANCE', ?, ?, ?, ?)
        """,
        (
            observation_id,
            card_id,
            ci_id,
            field,
            json.dumps(value, ensure_ascii=False),
            "2026-10-03T00:00:00Z",
        ),
    )


def test_commonality_consolidates_candidate_paths(tmp_path):
    db = tmp_path / "catalog.db"

    schema = (
        ROOT
        / "04_src"
        / "catalog"
        / "schema_v0_1.sql"
    ).read_text(encoding="utf-8")

    conn = sqlite3.connect(db)
    conn.executescript(schema)

    for n in (1, 2):
        card_id = f"CARD-{n}"
        ci_id = f"CI-{n}"

        conn.execute(
            """
            INSERT INTO library_cards (
                library_card_id,
                source_object_id,
                source_object_key,
                source_record_revision,
                received_at,
                card_json
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                card_id,
                f"SOURCE-{n}",
                f"TEST:SOURCE-{n}",
                "test",
                "2026-10-03T00:00:00Z",
                "{}",
            ),
        )

        conn.execute(
            """
            INSERT INTO cataloged_instances (
                cataloged_instance_id,
                status,
                created_at,
                updated_at
            )
            VALUES (?, 'PROVISIONAL', ?, ?)
            """,
            (
                ci_id,
                "2026-10-03T00:00:00Z",
                "2026-10-03T00:00:00Z",
            ),
        )

        conn.execute(
            """
            INSERT INTO cataloged_instance_evidence (
                cataloged_instance_evidence_id,
                cataloged_instance_id,
                library_card_id,
                relationship_status,
                reason,
                created_at
            )
            VALUES (?, ?, ?, 'ACTIVE', ?, ?)
            """,
            (
                f"CIE-{n}",
                ci_id,
                card_id,
                "test provenance",
                "2026-10-03T00:00:00Z",
            ),
        )

        values = {
            "title": ["Chiqué", "Chique"],
            "orchestra_or_album_artist": ["Osvaldo Pugliese"],
            "recording_date": ["1953-05-28"],
            "recording_identifier": ["Matrix L.D. 35119"],
            "composer": ["Ricardo Luis Brignolo"],
            "conductor": ["Osvaldo Pugliese"],
        }

        obs_n = 0

        for field, field_values in values.items():
            for value in field_values:
                obs_n += 1
                add_observation(
                    conn,
                    f"OBS-{n}-{obs_n}",
                    card_id,
                    ci_id,
                    field,
                    value,
                )

    conn.commit()

    tables = (
        "recordings",
        "performances",
        "works",
        "catalog_associations",
    )

    before = {
        table: conn.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]
        for table in tables
    }

    report = analysis.analyze_database(conn)

    after = {
        table: conn.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]
        for table in tables
    }

    assert report["analysis_revision"] == (
        "catalog_commonality_analysis.v0.3"
    )
    assert report["identity_effect"] == "NONE"

    candidate = report["candidate_sets"]

    assert candidate["repeated_comparison_group_count"] == 2
    assert candidate["distinct_candidate_set_count"] == 1

    candidate_set = candidate["candidate_sets"][0]

    assert candidate_set["candidate_entity_type"] == "RECORDING"
    assert candidate_set["resolution_status"] == "UNRESOLVED"
    assert candidate_set["identity_effect"] == "NONE"
    assert candidate_set["member_ci_ids"] == ["CI-1", "CI-2"]
    assert candidate_set["comparison_path_count"] == 2

    assert candidate_set["members"] == [
        {
            "cataloged_instance_id": "CI-1",
            "active_library_card_evidence": [
                {
                    "library_card_id": "CARD-1",
                    "source_object_id": "SOURCE-1",
                    "source_object_key": "TEST:SOURCE-1",
                    "source_record_revision": "test",
                }
            ],
        },
        {
            "cataloged_instance_id": "CI-2",
            "active_library_card_evidence": [
                {
                    "library_card_id": "CARD-2",
                    "source_object_id": "SOURCE-2",
                    "source_object_key": "TEST:SOURCE-2",
                    "source_record_revision": "test",
                }
            ],
        },
    ]

    corroboration = candidate_set["corroboration"]

    for field in (
        "recording_identifier",
        "composer",
        "conductor",
    ):
        assert corroboration[field][
            "exact_comparison_agreement"
        ]

    assert before == after == {
        "recordings": 0,
        "performances": 0,
        "works": 0,
        "catalog_associations": 0,
    }

    conn.close()



