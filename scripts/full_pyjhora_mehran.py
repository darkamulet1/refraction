#!/usr/bin/env python
"""
full_pyjhora_mehran.py

Thin wrapper around build_full_pyjhora_payload that regenerates Mehran's
canonical snapshot at references/out/mehran_full_pyjhora.json.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from v0min.core_time import make_birth_context
from v0min.full_extract import build_full_pyjhora_payload, save_payload, summarize_payload


BIRTH_NAME = "Mehran"
LOCATION_NAME = "Tehran"
LATITUDE = 35.6892
LONGITUDE = 51.3890
TIMEZONE = "Asia/Tehran"
BIRTH_DATETIME = datetime(1997, 6, 7, 20, 28, 36)
OUTPUT_PATH = Path("references/out/mehran_full_pyjhora.json")


def main() -> None:
    bc = make_birth_context(
        BIRTH_DATETIME,
        LATITUDE,
        LONGITUDE,
        tz_name=TIMEZONE,
        location_name=LOCATION_NAME,
    )
    payload = build_full_pyjhora_payload(bc, person=BIRTH_NAME, location_name=LOCATION_NAME)
    save_payload(payload, OUTPUT_PATH)

    for line in summarize_payload(payload):
        print(line)
    print(f"\nSnapshot written to {OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    main()
