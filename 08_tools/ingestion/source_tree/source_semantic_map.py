#!/usr/bin/env python3
"""Inspect one level of a source tree at a time.

The supplied -root establishes the source boundary.  Optional -subdir values
select nodes beneath that root.  Each selected node is inspected only at its
own level: the node itself is recorded and its immediate children are listed;
children are not recursively traversed.

The operation is intentionally idempotent and source-preserving.  It does not
rename, move, modify, normalize, or infer canonical meaning for source items.
Semantic observations are deliberately conservative and evidence-based.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "musicstewardship.source_tree_semantic_map.v2"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Inspect a source root and optionally selected immediate subdirectories."
    )
    p.add_argument("-root", required=True, help="Supplied source root / source boundary")
    p.add_argument(
        "-subdir",
        nargs="*",
        default=[],
        help="Optional relative subdirectory path(s) to inspect; each is inspected one level only",
    )
    p.add_argument("-o", "--output", required=True, help="Output path without .json/.md")
    return p.parse_args()


def entry_info(path: Path, root: Path, relative_path: str | None = None) -> dict[str, Any]:
    try:
        is_dir = path.is_dir()
        is_file = path.is_file()
        stat = path.stat()
        size = stat.st_size if is_file else None
        mtime = datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()
    except OSError as exc:
        is_dir = is_file = False
        size = None
        mtime = None
        error = str(exc)
    else:
        error = None

    rel = relative_path if relative_path is not None else path.relative_to(root).as_posix()
    name = path.name if path != root else root.name
    return {
        "relative_path": rel,
        "name": name,
        "entry_type": "DIRECTORY" if is_dir else "FILE" if is_file else "OTHER",
        "size": size,
        "modified_utc": mtime,
        "error": error,
    }


def filename_observations(name: str) -> dict[str, Any]:
    stem = Path(name).stem
    return {
        "stem": stem,
        "extension": Path(name).suffix.lower(),
        "numeric_components": [t for t in stem.replace("-", " ").replace("_", " ").split() if t.isdigit()],
    }


def pattern_shape(name: str) -> str:
    """Conservatively replace numeric runs while preserving observed text."""
    stem = Path(name).stem
    return re.sub(r"\d+(?:-\d+)?", "<NUM>", stem)


def file_name_structure(name: str) -> dict[str, Any]:
    """Extract observable filename structure without assigning meanings."""
    stem = Path(name).stem
    numbers = re.findall(r"\d+(?:-\d+)?", stem)
    suffix = None
    if numbers:
        matches = list(re.finditer(r"\d+(?:-\d+)?", stem))
        last_number = matches[-1]
        trailing = stem[last_number.end():]
        suffix_match = re.fullmatch(r"[_-]([A-Za-z][A-Za-z0-9]*)", trailing)
        if suffix_match:
            suffix = suffix_match.group(1)

    return {
        "shape": pattern_shape(name),
        "numeric_components": numbers,
        "terminal_suffix": suffix,
    }


def observed_pattern_analysis(children: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize stable filename components and positions; no semantic interpretation."""
    from collections import Counter

    files = [x for x in children if x["entry_type"] == "FILE"]
    dirs = [x for x in children if x["entry_type"] == "DIRECTORY"]

    extension_counts = Counter(
        x["filename"]["extension"] or "[none]"
        for x in files if "filename" in x
    )

    audio_exts = {".aif", ".aiff", ".wav", ".flac", ".mp3", ".m4a", ".alac"}
    audio_files = [
        x for x in files
        if x.get("filename", {}).get("extension", "").lower() in audio_exts
    ]

    numeric_present = 0
    text_before_numeric = 0
    suffix_counts = Counter()
    underscore_before_suffix = 0
    numeric_forms = Counter()

    for item in audio_files:
        stem = Path(item["name"]).stem
        match = re.search(r"\d+(?:-\d+)?", stem)
        if not match:
            continue

        numeric_present += 1
        before = stem[:match.start()].rstrip(" _-")
        if before:
            text_before_numeric += 1

        numeric_forms[match.group(0)] += 1

        after = stem[match.end():]
        suffix = re.search(r"[_-]([A-Za-z][A-Za-z0-9]*)$", after)
        if suffix:
            suffix_counts[suffix.group(1)] += 1
            if after.startswith("_"):
                underscore_before_suffix += 1

    return {
        "directory_count": len(dirs),
        "file_count": len(files),
        "file_extension_counts": dict(sorted(extension_counts.items())),
        "audio_like_file_count": len(audio_files),
        "audio_filename_numeric_component": {
            "present": numeric_present,
            "absent": len(audio_files) - numeric_present,
        },
        "audio_filename_text_before_numeric": {
            "present": text_before_numeric,
            "absent": len(audio_files) - text_before_numeric,
        },
        "audio_filename_terminal_suffixes": dict(sorted(suffix_counts.items())),
        "audio_filename_underscore_before_suffix": {
            "present": underscore_before_suffix,
            "absent": len(audio_files) - underscore_before_suffix,
        },
        "audio_filename_numeric_values": dict(sorted(numeric_forms.items())),
    }



def pattern_markdown(patterns: dict[str, Any]) -> list[str]:
    lines = ["### Observed pattern analysis", ""]
    lines.append("Component-position observations among immediate children:")

    lines.append(f"- Audio-like files analyzed: {patterns['audio_like_file_count']}")

    if patterns["file_extension_counts"]:
        lines.append("- File extensions:")
        for ext, count in patterns["file_extension_counts"].items():
            lines.append(f"  - `{ext}`: {count}")

    numeric = patterns["audio_filename_numeric_component"]
    lines.append(
        f"- Audio filename numeric component: "
        f"{numeric['present']} present, {numeric['absent']} absent"
    )

    text_before = patterns["audio_filename_text_before_numeric"]
    lines.append(
        f"- Text before numeric component: "
        f"{text_before['present']} present, {text_before['absent']} absent"
    )

    suffixes = patterns["audio_filename_terminal_suffixes"]
    if suffixes:
        lines.append("- Audio filename terminal suffixes:")
        for suffix, count in suffixes.items():
            lines.append(f"  - `{suffix}`: {count}")

    underscore = patterns["audio_filename_underscore_before_suffix"]
    lines.append(
        f"- Underscore immediately before terminal suffix: "
        f"{underscore['present']} present, {underscore['absent']} absent"
    )

    if patterns["audio_filename_numeric_values"]:
        lines.append("- Audio filename numeric components:")
        for value, count in patterns["audio_filename_numeric_values"].items():
            lines.append(f"  - `{value}`: {count}")

    lines += [
        "",
        "> Component analysis reports observed structure only; "
        "it does not assign semantic meaning.",
        "",
    ]
    return lines



def inspect_node(root: Path, rel: str) -> dict[str, Any]:
    node = root / rel if rel else root
    node = node.resolve()
    root_resolved = root.resolve()

    try:
        node.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(f"-subdir escapes -root: {rel}") from exc

    if not node.exists():
        raise FileNotFoundError(f"Subdirectory does not exist: {rel}")
    if not node.is_dir():
        raise NotADirectoryError(f"-subdir is not a directory: {rel}")

    node_rel = node.relative_to(root_resolved).as_posix() if node != root_resolved else "."
    result: dict[str, Any] = {
        "node": entry_info(node, root_resolved, node_rel),
        "depth_from_root": 0 if node == root_resolved else len(Path(node_rel).parts),
        "children": [],
        "observations": {},
    }

    try:
        children = sorted(node.iterdir(), key=lambda p: (not p.is_dir(), p.name.casefold(), p.name))
    except OSError as exc:
        result["observations"]["read_error"] = str(exc)
        return result

    for child in children:
        info = entry_info(child, root_resolved)
        if info["entry_type"] == "FILE":
            info["filename"] = filename_observations(child.name)
            info["filename"]["structure"] = file_name_structure(child.name)
        result["children"].append(info)

    dirs = [x for x in result["children"] if x["entry_type"] == "DIRECTORY"]
    files = [x for x in result["children"] if x["entry_type"] == "FILE"]
    extensions: dict[str, int] = {}
    for item in files:
        ext = item["filename"]["extension"] or "[none]"
        extensions[ext] = extensions.get(ext, 0) + 1

    result["observations"] = {
        "child_count": len(result["children"]),
        "directory_count": len(dirs),
        "file_count": len(files),
        "file_extensions": dict(sorted(extensions.items())),
        "directory_names": [x["name"] for x in dirs],
        "file_names": [x["name"] for x in files],
        "pattern_analysis": observed_pattern_analysis(result["children"]),
        "semantic_note": "Observed structure only; semantic labels require downstream interpretation.",
    }
    return result


def markdown(data: dict[str, Any]) -> str:
    root = data["source_root"]
    lines = [
        "# Source Semantic Map",
        "",
        "> Observed source structure is preserved. This map records one inspected level at a time; semantic interpretations are observations for downstream decoding, not canonical assertions.",
        "",
        "## Source root",
        "",
        f"- **Name:** `{root['name']}`",
        f"- **Path:** `{root['path']}`",
        f"- **Inspection:** `{data['inspection_mode']}`",
        "",
    ]

    for inspection in data["inspections"]:
        node = inspection["node"]
        obs = inspection["observations"]
        lines += [
            "## Inspected node",
            "",
            f"`{node['relative_path']}` — **{node['name']}**",
            "",
            f"- Children: {obs.get('child_count', 0)}",
            f"- Directories: {obs.get('directory_count', 0)}",
            f"- Files: {obs.get('file_count', 0)}",
        ]
        if obs.get("file_extensions"):
            lines += ["- File extensions:"]
            for ext, count in obs["file_extensions"].items():
                lines.append(f"  - `{ext}`: {count}")
        lines += ["", "### Immediate children", ""]
        for child in inspection["children"]:
            kind = child["entry_type"]
            lines.append(f"- `{child['name']}` — {kind}")
        lines.extend(pattern_markdown(obs.get("pattern_analysis", {})))
        lines += ["", "### Semantic observation", "", f"{obs.get('semantic_note', '')}", ""]

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"-root must be an existing directory: {args.root}")

    # Always establish and record the supplied root.  It is not recursively walked.
    inspections = [inspect_node(root, "")]
    for rel in args.subdir:
        inspections.append(inspect_node(root, rel))

    data = {
        "schema": SCHEMA,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": {
            "name": root.name,
            "path": str(root),
        },
        "inspection_mode": "root_plus_selected_subdirectories_one_level",
        "selected_subdirectories": args.subdir,
        "inspections": inspections,
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    json_path = output.with_suffix(".json")
    md_path = output.with_suffix(".md")
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(markdown(data), encoding="utf-8")

    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    print(f"Inspections: {len(inspections)}")
    for inspection in inspections:
        node = inspection["node"]
        print(f"  {node['relative_path']}: {len(inspection['children'])} immediate children")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
