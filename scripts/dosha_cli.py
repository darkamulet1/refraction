#!/usr/bin/env python
"""
CLI utility to export the dosha.v1 block from a *_full_pyjhora.json snapshot.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from v0min import api


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the PyJHora dosha.v1 payload from an existing *_full_pyjhora.json file."
    )
    parser.add_argument("--birth-json", required=True, help="Path to *_full_pyjhora.json payload.")
    parser.add_argument(
        "--out",
        help="Destination path for the dosha JSON. If omitted, the payload is printed to stdout.",
    )
    parser.add_argument(
        "--no-print",
        action="store_true",
        help="Suppress stdout output when --out is used.",
    )
    return parser.parse_args()


def load_payload(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    payload = load_payload(Path(args.birth_json))
    block = api.compute_dosha(payload)
    if args.out:
        write_json(block, Path(args.out))
        if not args.no_print:
            print(f"Wrote dosha payload to {Path(args.out).resolve()}")
    else:
        print(json.dumps(block, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
