from __future__ import annotations

from datetime import datetime

from v0min.core_time import make_birth_context
from v0min.full_extract import build_full_pyjhora_payload


def _make_birth_context():
    return make_birth_context(
        datetime(1997, 6, 7, 20, 28, 36),
        35.6892,
        51.3890,
        tz_name="Asia/Tehran",
        location_name="Tehran",
    )


def test_dosha_raja_gating() -> None:
    bc = _make_birth_context()
    payload = build_full_pyjhora_payload(bc, person="Mehran", location_name="Tehran")
    assert "dosha" not in payload
    assert "raja_yoga" not in payload

    payload_with_dosha = build_full_pyjhora_payload(
        bc,
        person="Mehran",
        location_name="Tehran",
        extraction_config={"dosha": {"enabled": True}},
    )
    assert "dosha" in payload_with_dosha

    payload_with_raja = build_full_pyjhora_payload(
        bc,
        person="Mehran",
        location_name="Tehran",
        extraction_config={"raja_yoga": {"enabled": True}},
    )
    assert "raja_yoga" in payload_with_raja


def test_predictions_and_panchanga_gating() -> None:
    bc = _make_birth_context()
    payload = build_full_pyjhora_payload(bc, person="Mehran", location_name="Tehran")
    assert "predictions" not in payload
    assert "panchanga_extras" not in payload

    predictions_payload = build_full_pyjhora_payload(
        bc,
        person="Mehran",
        location_name="Tehran",
        extraction_config={"predictions": {"enabled": True}},
    )
    assert "predictions" in predictions_payload

    panchanga_payload = build_full_pyjhora_payload(
        bc,
        person="Mehran",
        location_name="Tehran",
        extraction_config={"panchanga_extras": {"enabled": True}},
    )
    assert "panchanga_extras" in panchanga_payload
    muhurta_payload = build_full_pyjhora_payload(
        bc,
        person="Mehran",
        location_name="Tehran",
        extraction_config={
            "muhurta": {
                "enabled": True,
                "activity_type": "CLASS_START",
                "start_date": "2025-06-07",
                "end_date": "2025-06-07",
                "step_minutes": 60,
            }
        },
    )
    assert "muhurta" in muhurta_payload
    prasna_payload = build_full_pyjhora_payload(
        bc,
        person="Mehran",
        location_name="Tehran",
        extraction_config={
            "prasna": {
                "enabled": True,
                "mode": "KP_249",
                "numbers": [123],
            }
        },
    )
    assert "prasna" in prasna_payload


def test_dasha_multi_gating() -> None:
    bc = _make_birth_context()
    base_payload = build_full_pyjhora_payload(bc, person="Mehran", location_name="Tehran")
    assert "systems" not in base_payload["dashas"]

    cfg = {"dasha": {"systems": ["LAGNAMSAKA_RAASI", "PATTAYINI_VARSHIKA"]}}
    payload = build_full_pyjhora_payload(bc, person="Mehran", location_name="Tehran", extraction_config=cfg)
    systems_block = payload["dashas"]["systems"]
    assert set(systems_block.keys()) == {"LAGNAMSAKA_RAASI", "PATTAYINI_VARSHIKA"}
    assert systems_block["LAGNAMSAKA_RAASI"]["system_type"] == "RAASI"
    assert systems_block["PATTAYINI_VARSHIKA"]["system_type"] == "ANNUAL"
