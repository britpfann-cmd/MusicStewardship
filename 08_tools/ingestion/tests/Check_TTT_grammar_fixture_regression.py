from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

FIXTURE_CSV = (
    ROOT
    / "08_tools"
    / "ingestion"
    / "tests"
    / "TTT_grammar_ingest_v2_baseline_sample.csv"
)

ADAPTER = (
    ROOT
    / "08_tools"
    / "ingestion"
    / "tests"
    / "TTT_grammar_fixture_adapter.py"
)

BUILDER = (
    ROOT
    / "08_tools"
    / "ingestion"
    / "source_tree"
    / "source_candidate_record_builder.py"
)

SANDBOX = ROOT / "99_sandbox"

EVIDENCE_JSON = SANDBOX / "TTT_grammar_fixture_regression_evidence.json"
MAP_JSON = SANDBOX / "TTT_grammar_fixture_regression_semantic_map.json"
CANDIDATES_JSON = SANDBOX / "TTT_grammar_fixture_regression_candidates.json"
RECORDS_BASE = SANDBOX / "TTT_grammar_fixture_regression_candidate_records"


EXPECTED_ROWS = 24
EXPECTED_OBSERVATIONS = 48
EXPECTED_FIELDS = {
    "release_track_number",
    "title",
}
EXPECTED_RULES = {"1"}


def run(command: list[str]) -> None:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    if result.stdout:
        print(result.stdout, end="")

    if result.returncode != 0:
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        raise AssertionError(
            f"Command failed with exit code {result.returncode}: "
            + " ".join(command)
        )


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> None:
    print("===== TTT GRAMMAR FIXTURE REGRESSION =====")

    if not FIXTURE_CSV.exists():
        fail(f"Missing frozen fixture: {FIXTURE_CSV}")

    if not ADAPTER.exists():
        fail(f"Missing fixture adapter: {ADAPTER}")

    if not BUILDER.exists():
        fail(f"Missing candidate builder: {BUILDER}")

    SANDBOX.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Rebuild structured source-specific evidence from the frozen CSV.
    # ------------------------------------------------------------------
    run(
        [
            sys.executable,
            str(ADAPTER),
            str(FIXTURE_CSV),
            "-o",
            str(EVIDENCE_JSON),
        ]
    )

    evidence = load_json(EVIDENCE_JSON)

    if evidence.get("schema") != (
        "musicstewardship.ttt_grammar_fixture_evidence.v1"
    ):
        fail("Unexpected fixture evidence schema")

    source_objects = evidence.get("source_objects", [])
    observations = evidence.get("observations", [])
    summary = evidence.get("summary", {})

    if len(source_objects) != EXPECTED_ROWS:
        fail(
            f"Expected {EXPECTED_ROWS} source objects; "
            f"got {len(source_objects)}"
        )

    if len(observations) != EXPECTED_OBSERVATIONS:
        fail(
            f"Expected {EXPECTED_OBSERVATIONS} observations; "
            f"got {len(observations)}"
        )

    decoded_fields = set(summary.get("decoded_fields", []))
    if decoded_fields != EXPECTED_FIELDS:
        fail(
            "Unexpected decoded fields: "
            f"{sorted(decoded_fields)}"
        )

    filename_rules = set(summary.get("filename_rules", []))
    if filename_rules != EXPECTED_RULES:
        fail(
            "Unexpected filename rules: "
            f"{sorted(filename_rules)}"
        )

    # Every observation must retain source-object lineage.
    source_ids = {
        item["source_object_id"]
        for item in source_objects
    }

    for observation in observations:
        if observation.get("source_object_id") not in source_ids:
            fail(
                "Observation has invalid source_object_id: "
                f"{observation.get('source_object_id')}"
            )

        if observation.get("evidence_channel") != "source_specific":
            fail("TTT grammar evidence escaped source_specific channel")

        if observation.get("evidence_type") != "filename_rule":
            fail("TTT grammar evidence has unexpected evidence_type")

        if not observation.get("rule_field"):
            fail("TTT grammar observation has no rule_field")

    # ------------------------------------------------------------------
    # 2. Build Candidate Records from the same fixture evidence.
    #
    # The semantic-map/candidate files are supplied by the existing
    # fixture pipeline. We deliberately do not recreate those structures
    # in this regression test.
    # ------------------------------------------------------------------
    existing_map = SANDBOX / "TTT_grammar_fixture_semantic_map_v1.json"
    existing_candidates = SANDBOX / "TTT_grammar_fixture_candidates_v1.json"

    if not existing_map.exists():
        fail(f"Missing fixture semantic map: {existing_map}")

    if not existing_candidates.exists():
        fail(f"Missing fixture candidates: {existing_candidates}")

    run(
        [
            sys.executable,
            str(BUILDER),
            "-map",
            str(existing_map),
            "-candidates",
            str(existing_candidates),
            "-metadata",
            str(EVIDENCE_JSON),
            "-o",
            str(RECORDS_BASE),
        ]
    )

    records_path = RECORDS_BASE.with_suffix(".json")
    records = load_json(records_path).get("records", [])

    if len(records) != EXPECTED_ROWS:
        fail(
            f"Expected {EXPECTED_ROWS} Candidate Records; "
            f"got {len(records)}"
        )

    # ------------------------------------------------------------------
    # 3. Verify Candidate Record preservation and non-promotion.
    # ------------------------------------------------------------------
    observed_fields: set[str] = set()
    canonical_promotions: list[tuple[str, str]] = []

    forbidden_attributes = {
        "track_number",
        "recording_id",
        "catalog_number",
        "singer",
        "orchestra",
        "tanda",
        "year",
        "title",
    }

    for record in records:
        for observation in record.get("observations", []):
            if observation.get("evidence_type") in {
                "filename.release_track_number",
                "filename.title",
            }:
                observed_fields.add(
                    observation["evidence_type"].split(".", 1)[1]
                )

        for attribute in record.get(
            "candidate_attributes",
            {}
        ):
            if attribute in forbidden_attributes:
                canonical_promotions.append(
                    (
                        record.get("candidate_record_id", ""),
                        attribute,
                    )
                )

    if observed_fields != EXPECTED_FIELDS:
        fail(
            "Candidate Records did not preserve expected TTT fields: "
            f"{sorted(observed_fields)}"
        )

    if canonical_promotions:
        fail(
            "TTT grammar fields were promoted to forbidden candidate "
            f"attributes: {canonical_promotions}"
        )

    print("PASS")
    print(f"Fixture rows: {EXPECTED_ROWS}")
    print(f"Source-specific observations: {EXPECTED_OBSERVATIONS}")
    print(
        "Decoded fields: "
        + ", ".join(sorted(EXPECTED_FIELDS))
    )
    print("Canonical promotion: NONE")
    print("Lineage validation: PASS")
    print("Candidate Record preservation: PASS")


if __name__ == "__main__":
    main()
