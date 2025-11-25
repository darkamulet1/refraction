#!/usr/bin/env python
"""
CLI utility to export predictions.v1 from a *_full_pyjhora.json snapshot.
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

from v0min.prediction_extract import compute_predictions_block


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate PyJHora predictions.v1 payloads.")
    parser.add_argument("--birth-json", required=True, help="Path to *_full_pyjhora.json payload.")
    parser.add_argument("--out", help="Destination JSON file; stdout if omitted.")
    parser.add_argument("--language", default="en", help="Language code for predictions (default: en).")
    parser.add_argument(
        "--no-general",
        action="store_true",
        help="Skip the general predictions block.",
    )
    parser.add_argument(
        "--no-naadi-marriage",
        action="store_true",
        help="Skip the Naadi marriage analysis.",
    )
    parser.add_argument(
        "--no-longevity",
        action="store_true",
        help="Skip the longevity summary.",
    )
    parser.add_argument(
        "--gender",
        choices=["male", "female"],
        help="Override gender for Naadi prediction (defaults to male).",
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
        "language": args.language,
        "include_general": not args.no_general,
        "include_naadi_marriage": not args.no_naadi_marriage,
        "include_longevity": not args.no_longevity,
    }
    if args.gender:
        config["gender"] = args.gender
    block = compute_predictions_block(payload, config=config)
    if args.out:
        write_json(block, Path(args.out))
        if not args.no_print:
            print(f"Wrote predictions payload to {Path(args.out).resolve()}")
    else:
        print(json.dumps(block, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
