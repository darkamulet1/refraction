from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from v0min.transit_extract import build_transit_snapshot


def test_transit_mehran_fixed_date() -> None:
    data = json.loads(Path("references/out/mehran_full_pyjhora.json").read_text(encoding="utf-8"))
    snapshot = build_transit_snapshot(
        data,
        transit_datetime_local=datetime(2025, 1, 1, 12, 0, 0),
    )
    assert snapshot.schema_version == "transit.v1"
    assert snapshot.reference_person == "Mehran"
    assert len(snapshot.grahas) == 9
    for graha in snapshot.grahas:
        assert 1 <= graha.transit_house_from_natal_lagna <= 12
    assert 1 <= snapshot.flags.saturn_house_from_lagna <= 12
    assert 1 <= snapshot.flags.jupiter_house_from_lagna <= 12
