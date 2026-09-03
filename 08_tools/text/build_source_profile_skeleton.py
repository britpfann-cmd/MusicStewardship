#!/usr/bin/env python3
"""Create a source-profile skeleton without inventing source facts."""
from __future__ import annotations
import argparse
from pathlib import Path

T="""# Source profile: {source}
# Generated skeleton. Add only verified source-specific evidence rules.

source:
  - {source}

directory_semantics:
  use_hierarchy: true
  preserve_original_path: true
  directory_names_are_evidence_only: true

filename:
  rules: []

embedded_metadata:
  fields: []

external_references:
  references: []

normalization:
  rules: []

resolution:
  canonical_identity_requires_corroboration: true
  unresolved_assets: retain
"""
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--output-dir",type=Path,required=True)
    a=ap.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
    p=a.output_dir/f"{a.source}.yaml"
    if p.exists(): raise SystemExit(f"Refusing to overwrite: {p}")
    p.write_text(T.format(source=a.source),encoding="utf-8")
    print(f"Profile skeleton: {p}")
if __name__=="__main__": main()
