#!/usr/bin/env python
"""
CLI utility to export panchanga_extras.v1 from a *_full_pyjhora.json snapshot.
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

from v0min.panchanga_extras_extract import compute_panchanga_extras_block


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate PyJHora Panchanga extras payloads.")
    parser.add_argument("--birth-json", required=True, help="Path to *_full_pyjhora.json payload.")
    parser.add_argument("--out", help="Destination JSON file; stdout if omitted.")
    parser.add_argument(
        "--no-pancha-pakshi",
        action="store_true",
        help="Skip Pancha Pakshi computation.",
    )
    parser.add_argument(
        "--no-vratha-festivals",
        action="store_true",
        help="Skip vratha/festival detection.",
    )
    parser.add_argument(
        "--no-print",
        action="store_true",
        help="Suppress stdout confirmation when --out is provided.",
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
    config = {
        "include_pancha_pakshi": not args.no_pancha_pakshi,
        "include_vratha_festivals": not args.no_vratha_festivals,
    }
    block = compute_panchanga_extras_block(payload, config=config)
    if args.out:
        write_json(block, Path(args.out))
        if not args.no_print:
            print(f"Wrote panchanga extras payload to {Path(args.out).resolve()}")
    else:
        print(json.dumps(block, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
