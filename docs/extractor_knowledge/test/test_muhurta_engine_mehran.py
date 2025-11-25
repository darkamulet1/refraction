from __future__ import annotations

import json
from pathlib import Path

from jhora import const, utils
from v0min.muhurta_extract import MuhurtaConfig, compute_muhurta_windows

REF_PATH = Path("references/out/mehran_full_pyjhora.json")


def _load_payload() -> dict:
    return json.loads(REF_PATH.read_text(encoding="utf-8"))


def test_muhurta_engine_basic_structure() -> None:
    payload = _load_payload()
    config = MuhurtaConfig(
        activity_type="CLASS_START",
        start_date="2025-06-07",
        end_date="2025-06-08",
        step_minutes=60,
        max_windows=10,
    )
    result = compute_muhurta_windows(payload, config)
    assert result["schema_version"] == "muhurta.v1"
    assert result["activity_type"] == "CLASS_START"
    assert result["range"]["start_date"] == "2025-06-07"
    assert result["range"]["end_date"] == "2025-06-08"
    windows = result["windows"]
    assert windows, "Expected at least one muhurta window"
    for window in windows:
        assert "start_iso" in window and "end_iso" in window
        assert isinstance(window["score"], (int, float))
        assert window["tier"] in {"AVOID", "NEUTRAL", "GOOD", "EXCELLENT"}
        assert isinstance(window.get("reasons", []), list)


def test_muhurta_restores_language() -> None:
    payload = _load_payload()
    original_language = getattr(const, "_DEFAULT_LANGUAGE", "en")
    alternate_language = next(
        (code for code in const.available_languages.values() if code != original_language),
        original_language,
    )
    utils.set_language(alternate_language)
    try:
        config = MuhurtaConfig(
            activity_type="GENERIC",
            start_date="2025-06-07",
            end_date="2025-06-07",
            step_minutes=120,
            max_windows=2,
        )
        compute_muhurta_windows(payload, config)
        restored_language = getattr(const, "_DEFAULT_LANGUAGE", None)
        assert restored_language == alternate_language
    finally:
        utils.set_language(original_language)
