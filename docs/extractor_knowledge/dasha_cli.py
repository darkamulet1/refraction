#!/usr/bin/env python
"""
dasha_cli.py

Command-line utility to export PyJHora dasha timelines (per-system or multi-system).
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from v0min.dasha_common import DASHAS_SUPPORTED, DashaTimeline
from v0min.dasha_extract import build_all_dasha_timelines


def slugify(value: str) -> str:
    """Simple slug helper reused in multiple CLIs."""
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in value.strip())
    cleaned = "_".join(filter(None, cleaned.split("_")))
    return cleaned or "person"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def summarize_md(periods: List[dict]) -> str:
    """Return a short textual summary of the first few MD periods."""
    head = periods[:3]
    parts = []
    for period in head:
        start = period.get("start_iso")
        end = period.get("end_iso") or "..."
        parts.append(f"{period['lord']}({start}->{end})")
    suffix = "..." if len(periods) > 3 else ""
    return ", ".join(parts) + suffix


def load_birth_snapshot(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(data: dict, path: Path) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate PyJHora dasha timelines from an existing *_full_pyjhora.json snapshot."
    )
    parser.add_argument("--birth-json", required=True, help="Path to *_full_pyjhora.json payload.")
    parser.add_argument(
        "--system",
        action="append",
        choices=DASHAS_SUPPORTED,
        help="Dasha system(s) to export (can be provided multiple times). Defaults to VIMSHOTTARI.",
    )
    parser.add_argument(
        "--all-systems",
        action="store_true",
        help="Export every system supported by the CLI.",
    )
    parser.add_argument(
        "--out",
        help="Destination JSON path for a single-system export (requires exactly one --system).",
    )
    parser.add_argument(
        "--out-dir",
        help="Directory where per-system files will be written using the pattern <slug>_<SYSTEM>_dasha_full.json.",
    )
    parser.add_argument(
        "--full-out",
        help="When provided, write a dasha.full.v1 payload that bundles all requested systems.",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Print summaries only, without writing individual system JSON files.",
    )
    parser.add_argument(
        "--no-print",
        action="store_true",
        help="Write JSON artifacts only; suppress CLI summaries.",
    )
    return parser.parse_args()


def resolve_systems(args: argparse.Namespace) -> List[str]:
    systems: List[str]
    if args.all_systems:
        systems = list(DASHAS_SUPPORTED)
    elif args.system:
        systems = args.system
    else:
        systems = ["VIMSHOTTARI"]
    return systems


def build_output_path(base_dir: Path | None, slug: str, system: str) -> Path | None:
    if base_dir is None:
        return None
    return Path(base_dir) / f"{slug}_{system}_dasha_full.json"


def timeline_to_payload(
    timeline: DashaTimeline,
    birth_snapshot: dict,
    source_birth_file: str,
) -> dict:
    birth_data = birth_snapshot["birth_data"]
    meta = {
        "schema_version": timeline.schema_version,
        "engine": timeline.engine,
        "system": timeline.system,
        "system_type": timeline.system_type,
        "levels": timeline.levels,
        "source_birth_file": source_birth_file,
    }
    birth_ref = {
        "person": birth_data["person"],
        "datetime_local": birth_data["datetime_local"],
        "timezone": birth_data["timezone_name"],
    }
    timeline_entries = [
        {
            "level": period.level,
            "lord": period.lord,
            "sublord": period.sublord,
            "start_jd": period.start_jd,
            "end_jd": period.end_jd,
            "start_iso": period.start_iso,
            "end_iso": period.end_iso,
        }
        for period in timeline.periods
    ]
    return {
        "meta": meta,
        "birth_ref": birth_ref,
        "timeline": timeline_entries,
    }


def print_summary(person: str, systems: Iterable[str], timelines: Dict[str, DashaTimeline]) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    print(f"[{now}] Dasha summary for {person}: systems={', '.join(systems)}")
    for system in systems:
        timeline = timelines[system]
        md_periods = [
            {
                "lord": period.lord,
                "start_iso": period.start_iso,
                "end_iso": period.end_iso,
            }
            for period in timeline.periods
            if period.level == "MD"
        ]
        print(
            f"  - {system} ({timeline.system_type}): engine={timeline.engine}, MD count={len(md_periods)} :: {summarize_md(md_periods)}"
        )


def main() -> None:
    args = parse_args()
    systems = resolve_systems(args)
    birth_path = Path(args.birth_json)
    birth_snapshot = load_birth_snapshot(birth_path)
    person = birth_snapshot["birth_data"]["person"]
    slug = slugify(person)

    if args.out and len(systems) != 1:
        raise SystemExit("--out can only be used when exactly one --system is requested.")

    timelines = build_all_dasha_timelines(birth_snapshot, systems=systems)
    json_payloads = {
        system: timeline_to_payload(timeline, birth_snapshot, birth_path.name)
        for system, timeline in timelines.items()
    }

    def make_full_payload_dict() -> dict:
        return {
            "schema_version": "dasha.full.v1",
            "generated_at_utc": datetime.utcnow().isoformat(),
            "reference_source": str(birth_path),
            "person": person,
            "systems": json_payloads,
        }

    wrote_artifact = False
    full_payload_cache: dict | None = None

    if args.full_out:
        full_payload_cache = make_full_payload_dict()
        write_json(full_payload_cache, Path(args.full_out))
        wrote_artifact = True
        if not args.no_print:
            print(f"Wrote multi-system payload to {Path(args.full_out).resolve()}")

    if not args.print_only:
        if args.out:
            path = Path(args.out)
            write_json(next(iter(json_payloads.values())), path)
            if not args.no_print:
                print(f"Wrote {systems[0]} timeline to {path.resolve()}")
            wrote_artifact = True
        else:
            out_dir = Path(args.out_dir) if args.out_dir else None
            if out_dir:
                out_dir.mkdir(parents=True, exist_ok=True)
            for system, payload in json_payloads.items():
                path = build_output_path(out_dir, slug, system)
                if path is None:
                    continue
                write_json(payload, path)
                if not args.no_print:
                    print(f"Wrote {system} timeline to {path.resolve()}")
                wrote_artifact = True

        if not wrote_artifact:
            if len(systems) == 1:
                payload = next(iter(json_payloads.values()))
                print(json.dumps(payload, indent=2, ensure_ascii=False))
            else:
                if full_payload_cache is None:
                    full_payload_cache = make_full_payload_dict()
                print(json.dumps(full_payload_cache, indent=2, ensure_ascii=False))

    if not args.no_print:
        print_summary(person, systems, timelines)


if __name__ == "__main__":
    main()
