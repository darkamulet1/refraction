#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from v0min.planet_friendships_extract import (
    PlanetFriendshipsConfig,
    compute_planet_friendships_from_payload,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export planet_friendships.v1 from a *_full_pyjhora.json payload.")
    parser.add_argument("--birth-json", required=True, help="Path to *_full_pyjhora.json payload.")
    parser.add_argument("--out", help="Destination path for the JSON output.")
    parser.add_argument("--no-print", action="store_true", help="Suppress stdout when --out is used.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = json.loads(Path(args.birth_json).read_text(encoding="utf-8"))
    cfg = PlanetFriendshipsConfig.from_dict({"enabled": True})
    block = compute_planet_friendships_from_payload(payload, cfg)
    output = json.dumps(block, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(output + "\n", encoding="utf-8")
        if not args.no_print:
            print(f"Wrote planet friendships payload to {Path(args.out).resolve()}")
    else:
        print(output)


if __name__ == "__main__":
    main()
