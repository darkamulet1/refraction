from __future__ import annotations

from datetime import datetime

import pytest

from v0min.core_time import make_birth_context
from v0min.full_extract import build_full_pyjhora_payload


def test_full_payload_mehran_matches_core_expectations() -> None:
    bc = make_birth_context(
        datetime(1997, 6, 7, 20, 28, 36),
        35.6892,
        51.3890,
        tz_name="Asia/Tehran",
        location_name="Tehran",
    )
    payload = build_full_pyjhora_payload(bc, person="Mehran", location_name="Tehran")

    assert payload["birth_data"]["person"] == "Mehran"
    assert payload["core_chart"]["ayanamsa_mode"] == "LAHIRI"
    assert payload["core_chart"]["lagna_longitude_deg"] == pytest.approx(236.35187377299138, abs=1e-6)
