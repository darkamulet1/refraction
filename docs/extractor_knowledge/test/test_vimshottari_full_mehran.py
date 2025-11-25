from __future__ import annotations

import json
from pathlib import Path

from v0min.vedic_yaml import normalize_graha_key_from_json


EPS = 1e-6


def _load_payload(name: str) -> dict:
    path = Path(f"references/out/{name}")
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_continuous(periods: list[dict]) -> None:
    assert periods, "expected non-empty periods"
    last_end = None
    for period in periods:
        start = period["start_jd_local"]
        end = period["end_jd_local"]
        assert start < end
        if last_end is not None:
            assert abs(start - last_end) < 1e-4
        last_end = end


def test_vimshottari_full_mehran_structure() -> None:
    payload = _load_payload("mehran_full_pyjhora.json")
    vim_full = payload.get("vimshottari_full")
    assert vim_full is not None
    assert vim_full["engine"] == "PYJHORA_VIMSHOTTARI"

    md = vim_full["md"]
    md_ad = vim_full["md_ad"]
    md_ad_pd = vim_full["md_ad_pd"]
    assert md and md_ad and md_ad_pd
    _assert_continuous(md)
    _assert_continuous(md_ad)
    _assert_continuous(md_ad_pd)

    legacy_sequence = payload["dashas"]["vimshottari"]["sequence"]
    first_full = md[0]
    first_legacy = legacy_sequence[0]
    assert first_full["md_lord"] == normalize_graha_key_from_json(first_legacy["mahadasha_lord"]).upper()
    assert first_full["start_iso_local"].startswith(first_legacy["start"].split(" ")[0])


def test_vimshottari_full_afra_smoke() -> None:
    payload = _load_payload("afra_full_pyjhora.json")
    vim_full = payload.get("vimshottari_full")
    assert vim_full is not None
    assert vim_full["md"]
    assert vim_full["md_ad"]
