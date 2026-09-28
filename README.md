# MusicStewardship Processing-State Amendment

These files implement the architecture amendment discussed on 2026-09-27.

Copy the files into `_from_chat` first, inspect them, then move/copy them into the
production tree as appropriate.

Important: this package intentionally does NOT modify `rosetta_engine.py` or its
report generator yet. The next implementation step should wire the new vocabulary
into those existing components after inspecting their current source in the local
tree. This avoids guessing at the current implementation and accidentally
overwriting unrelated work.

The design amendment and CSV are paired human/machine artifacts.
