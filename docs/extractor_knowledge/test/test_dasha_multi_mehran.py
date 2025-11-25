from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from jhora import utils

from v0min.dasha_extract import (
    build_all_dasha_timelines,
    build_dasha_full_payload,
    build_dasha_timeline_from_snapshot,
)


REF_PATH = Path("references/out/mehran_full_pyjhora.json")


def _load_snapshot() -> dict:
    return json.loads(REF_PATH.read_text(encoding="utf-8"))


def _jd_from_local_string(value: str) -> float:
    dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    dob = (dt.year, dt.month, dt.day)
    tob = (dt.hour, dt.minute, dt.second)
    return utils.julian_day_number(dob, tob)


def test_vimshottari_matches_sequence_start() -> None:
    snapshot = _load_snapshot()
    timeline = build_dasha_timeline_from_snapshot(snapshot, "VIMSHOTTARI")
    md_periods = [period for period in timeline.periods if period.level == "MD"]
    assert md_periods, "Expected at least one Mahadasha period"
    assert md_periods[0].lord == "JUPITER"

    seq = snapshot["dashas"]["vimshottari"]["sequence"][0]
    expected_jd = _jd_from_local_string(seq["start"])
    assert abs(md_periods[0].start_jd - expected_jd) < 1e-3
    assert any(period.level == "PD" for period in timeline.periods)


def test_other_systems_produce_periods() -> None:
    snapshot = _load_snapshot()
    timelines = build_all_dasha_timelines(snapshot, systems=["YOGINI", "KALACHAKRA"])

    yogini = timelines["YOGINI"]
    assert yogini.schema_version == "dasha.v1"
    assert yogini.system_type == "GRAHA"
    assert any(period.level == "AD" for period in yogini.periods)

    kalachakra = timelines["KALACHAKRA"]
    valid_raasi = {
        "ARIES",
        "TAURUS",
        "GEMINI",
        "CANCER",
        "LEO",
        "VIRGO",
        "LIBRA",
        "SCORPIO",
        "SAGITTARIUS",
        "CAPRICORN",
        "AQUARIUS",
        "PISCES",
    }
    assert kalachakra.periods
    assert kalachakra.periods[0].lord in valid_raasi
    assert kalachakra.system_type == "RAASI"


def test_extended_systems_available() -> None:
    snapshot = _load_snapshot()
    timelines = build_all_dasha_timelines(snapshot, systems=["LAGNAMSAKA_RAASI", "PATTAYINI_VARSHIKA"])

    lagnamsaka = timelines["LAGNAMSAKA_RAASI"]
    assert lagnamsaka.system_type == "RAASI"
    assert any(period.level == "AD" for period in lagnamsaka.periods)

    patyayini = timelines["PATTAYINI_VARSHIKA"]
    assert patyayini.system_type == "ANNUAL"
    assert patyayini.levels  # ensure non-empty
    assert patyayini.periods


def test_full_payload_structure() -> None:
    snapshot = _load_snapshot()
    payload = build_dasha_full_payload(snapshot, systems=["VIMSHOTTARI", "YOGINI"], reference_source=str(REF_PATH))
    assert payload["schema_version"] == "dasha.full.v1"
    systems = payload["systems"]
    assert set(systems.keys()) == {"VIMSHOTTARI", "YOGINI"}
    for system, info in systems.items():
        meta = info["meta"]
        assert meta["schema_version"] == "dasha.v1"
        assert meta["system_type"]
        assert meta["levels"]
        assert info["timeline"]
        first = info["timeline"][0]
        assert first["start_jd"] < (first["end_jd"] or first["start_jd"] + 1)
