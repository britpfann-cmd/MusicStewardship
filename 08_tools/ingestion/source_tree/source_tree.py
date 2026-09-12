import argparse
import csv
import hashlib
from pathlib import Path

RECOGNIZED_AUDIO_EXTENSIONS = {
    ".flac", ".mp3", ".wav", ".m4a",
    ".mp4", ".aac", ".ogg", ".opus",
}

OUTPUT_FIELDS = [
    "source_id",
    "source_root",
    "relative_path",
    "filename",
    "extension",
    "source_object_type",
    "artifact_reason",
    "top_level_collection",
    "directory_path",
    "directory_depth",
    "file_stem",
    "file_size",
    "file_mtime_ns",
    "source_object_id",
    "metadata_status",
]


def stable_object_id(source_id, relative_path):
    value = f"{source_id}|{relative_path}".encode("utf-8")
    return hashlib.sha256(value).hexdigest()[:24]


def classify_file(path):
    name = path.name
    parts = {part.lower() for part in path.parts}

    if name.startswith("._"):
        return "SOURCE_ARTIFACT", "APPLEDOUBLE"

    if "__macosx" in parts:
        return "SOURCE_ARTIFACT", "MACOSX_DIRECTORY"

    if path.suffix.lower() in RECOGNIZED_AUDIO_EXTENSIONS:
        return "AUDIO", ""

    if path.suffix.lower() in {".csv", ".tsv", ".xlsx", ".xls", ".ods"}:
        return "CATALOG_DATA", ""

    if path.suffix.lower() in {
        ".pdf", ".txt", ".md", ".rtf", ".doc", ".docx"
    }:
        return "DOCUMENTATION", ""

    if path.suffix.lower() in {
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif", ".tiff", ".bmp"
    }:
        return "GRAPHIC", ""

    return "OTHER_SOURCE_FILE", ""


def discover(root, source_id):
    root = Path(root).resolve()
    records = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue

        relative = path.relative_to(root)
        object_type, artifact_reason = classify_file(path)

        top_level = (
            relative.parts[0]
            if len(relative.parts) > 0
            else ""
        )

        directory_path = (
            str(relative.parent)
            if str(relative.parent) != "."
            else ""
        )

        records.append({
            "source_id": source_id,
            "source_root": str(root),
            "relative_path": str(relative),
            "filename": path.name,
            "extension": path.suffix.lower(),
            "source_object_type": object_type,
            "artifact_reason": artifact_reason,
            "top_level_collection": top_level,
            "directory_path": directory_path,
            "directory_depth": len(relative.parts) - 1,
            "file_stem": path.stem,
            "file_size": path.stat().st_size,
            "file_mtime_ns": path.stat().st_mtime_ns,
            "source_object_id": stable_object_id(
                source_id, str(relative)
            ),
            "metadata_status": "NOT_YET_READ",
        })

    return records


def write_csv(records, output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(records)


def main():
    parser = argparse.ArgumentParser(
        description="Discover and classify every file in a source package."
    )
    parser.add_argument("root")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    records = discover(args.root, args.source_id)
    write_csv(records, args.output)

    counts = {}
    for record in records:
        kind = record["source_object_type"]
        counts[kind] = counts.get(kind, 0) + 1

    print(f"Source objects: {len(records)}")

    for kind in sorted(counts):
        print(f"{kind}: {counts[kind]}")

    print(f"CSV written: {args.output}")


if __name__ == "__main__":
    main()
