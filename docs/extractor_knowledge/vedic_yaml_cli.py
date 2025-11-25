#!/usr/bin/env python
from __future__ import annotations

"""
Generic converter: takes a full_pyjhora JSON payload and emits the vedic_master.v2 YAML.

Example:
    $env:PYTHONPATH="src"
    .\.venv\Scripts\python.exe scripts/vedic_yaml_cli.py ^
        --in references/out/amir_roozegari_full_pyjhora.json ^
        --out references/out/amir_roozegari_vedic_master_v1.yaml
"""

import argparse
from pathlib import Path

import yaml

from v0min import api


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a full_pyjhora JSON snapshot into vedic_master.v2 YAML."
    )
    parser.add_argument(
        "--in",
        dest="input_path",
        required=True,
        help="Path to full_pyjhora JSON payload (e.g., references/out/mehran_full_pyjhora.json)",
    )
    parser.add_argument(
        "--out",
        dest="output_path",
        required=True,
        help="Destination YAML path (e.g., references/out/mehran_vedic_master_v2.yaml)",
    )
    parser.add_argument(
        "--no-print",
        action="store_true",
        help="Suppress summary output after writing the YAML.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input_path)
    output_path = Path(args.output_path)

    vedic_payload = api.build_full_yaml_from_birth_json(str(input_path))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(vedic_payload, handle, sort_keys=False, allow_unicode=True)

    if not args.no_print:
        person = vedic_payload.get("meta", {}).get("person", "unknown")
        schema = vedic_payload.get("meta", {}).get("schema_version", "unknown")
        lagna = (
            vedic_payload.get("core_charts", {})
            .get("D1", {})
            .get("lagna", {})
            .get("sign", "unknown")
        )
        print("Vedic master YAML generated:")
        print(f"  person: {person}")
        print(f"  schema: {schema}")
        print(f"  D1 lagna sign: {lagna}")
        print(f"  output: {output_path}")


if __name__ == "__main__":
    main()
