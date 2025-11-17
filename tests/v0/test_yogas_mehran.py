from __future__ import annotations

from datetime import datetime

from v0min.core_time import make_birth_context
from v0min.full_extract import build_full_pyjhora_payload


def _build_mehran_birth_context():
    return make_birth_context(
        datetime(1997, 6, 7, 20, 28, 36),
        35.6892,
        51.3890,
        tz_name="Asia/Tehran",
        location_name="Tehran",
    )


def test_mehran_yogas_block_exists() -> None:
    bc = _build_mehran_birth_context()
    payload = build_full_pyjhora_payload(bc, person="Mehran", location_name="Tehran")

    yogas = payload.get("yogas_pyjhora")
    assert yogas is not None
    assert yogas.get("engine") == "PYJHORA_YOGA"

    charts = yogas.get("by_chart", {})
    assert "D1" in charts and len(charts["D1"]) > 0
    assert "D9" in charts and len(charts["D9"]) > 0
