#!/usr/bin/env python
"""
CLI utility to export yogas_extended.v1 from a *_full_pyjhora.json payload.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from v0min.yogas_extended_extract import YogasExtendedConfig, compute_yogas_extended_from_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the PyJHora yogas_extended.v1 payload from a *_full_pyjhora.json file."
    )
    parser.add_argument("--birth-json", required=True, help="Path to *_full_pyjhora.json payload.")
    parser.add_argument(
        "--charts",
        help="Comma-separated list of D-charts to include (e.g., D1,D9). Defaults to D1.",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Language code for yoga resources (default: en).",
    )
    parser.add_argument(
        "--no-kaala-sarpa",
        action="store_true",
        help="Disable Kaala Sarpa variant export.",
    )
    parser.add_argument(
        "--out",
        help="Destination path for the JSON output. If omitted, writes to stdout.",
    )
    parser.add_argument(
        "--no-print",
        action="store_true",
        help="Suppress stdout when --out is provided.",
    )
    return parser.parse_args()


def _parse_charts(arg_value: Optional[str]) -> List[str]:
    if not arg_value:
        return ["D1"]
    charts = [token.strip() for token in arg_value.split(",") if token.strip()]
    return charts or ["D1"]


def _build_config(args: argparse.Namespace) -> YogasExtendedConfig:
    charts = _parse_charts(args.charts)
    cfg_dict: Dict[str, Any] = {
        "enabled": True,
        "charts": charts,
        "language": args.language or "en",
        "include_kaala_sarpa_variants": not args.no_kaala_sarpa,
    }
    return YogasExtendedConfig.from_dict(cfg_dict)


def load_payload(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    payload = load_payload(Path(args.birth_json))
    cfg = _build_config(args)
    block = compute_yogas_extended_from_payload(payload, cfg)
    if args.out:
        write_json(block, Path(args.out))
        if not args.no_print:
            print(f"Wrote yogas_extended payload to {Path(args.out).resolve()}")
    else:
        print(json.dumps(block, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
