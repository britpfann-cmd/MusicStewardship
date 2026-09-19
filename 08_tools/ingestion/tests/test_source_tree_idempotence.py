from pathlib import Path
import sys

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[3] / "08_tools" / "ingestion")
)

from source_tree.source_tree import discover


def test_source_tree_repeat_walk_is_idempotent(tmp_path):
    root = tmp_path / "source"
    root.mkdir()

    (root / "A").mkdir()
    (root / "B").mkdir()
    (root / "empty").mkdir()

    (root / "track01.mp3").write_bytes(b"track-one")
    (root / "A" / "track02.wav").write_bytes(b"track-two")
    (root / "A" / "notes.txt").write_text("source evidence", encoding="utf-8")
    (root / "B" / "track03.flac").write_bytes(b"track-three")

    source_id = "TEST_SOURCE"

    first = discover(root, source_id)
    second = discover(root, source_id)

    assert first == second

    first_ids = [row["source_object_id"] for row in first]
    second_ids = [row["source_object_id"] for row in second]

    assert first_ids == second_ids
    assert len(first_ids) == len(set(first_ids))

    assert len(first) == 8
