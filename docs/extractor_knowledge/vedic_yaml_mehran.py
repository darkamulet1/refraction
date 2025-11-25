#!/usr/bin/env python
"""
Produce the vedic_master.v2 YAML snapshot for Mehran from the full_pyjhora payload.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from v0min.vedic_yaml import build_vedic_master_from_full, SCHEMA_VERSION


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "references" / "out" / "mehran_full_pyjhora.json"
    dst = root / "references" / "out" / "mehran_vedic_master_v2.yaml"

    with src.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    vedic = build_vedic_master_from_full(payload)

    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(vedic, handle, sort_keys=False, allow_unicode=True)

    person = vedic.get("meta", {}).get("person", "unknown")
    print("Vedic master YAML generated:")
    print(f"  person: {person}")
    print(f"  schema: {SCHEMA_VERSION}")
    print(f"  output: {dst}")


if __name__ == "__main__":
    main()
