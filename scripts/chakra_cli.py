#!/usr/bin/env python
"""
CLI utility to export Chakra (Sarvatobhadra, Kaala, Kota, Shoola...) snapshots.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from v0min.chakra_extract import ChakraConfig, compute_chakra_snapshot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Chakra layers from a *_full_pyjhora.json payload.")
    parser.add_argument("--birth-json", required=True, help="Path to *_full_pyjhora.json payload.")
    parser.add_argument(
        "--datetime-override",
        help="ISO8601 datetime to compute chakras for (defaults to birth datetime).",
    )
    parser.add_argument(
        "--layers",
        help="Comma-separated list of chakra layers to include (e.g., sarvatobhadra,kaala,kota).",
    )
    parser.add_argument(
        "--out",
        help="Destination JSON file. Prints to stdout when omitted.",
    )
    return parser.parse_args()


def _load_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_payload(data: dict, destination: Optional[Path]) -> None:
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    if destination:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


def main() -> None:
    args = parse_args()
    layers = [token.strip() for token in args.layers.split(",")] if args.layers else None
    cfg = ChakraConfig(
        datetime_override=args.datetime_override,
        include_layers=layers,
    )
    payload = _load_payload(Path(args.birth_json))
    snapshot = compute_chakra_snapshot(payload, cfg)
    destination = Path(args.out) if args.out else None
    _write_payload(snapshot, destination)


if __name__ == "__main__":
    main()
