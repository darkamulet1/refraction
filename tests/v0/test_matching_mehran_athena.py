from __future__ import annotations

import json
from pathlib import Path

from v0min.matching_extract import compute_ashtakoota_matching


def _load_payload(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_matching_mehran_athena_summary() -> None:
    mehran = _load_payload("references/out/mehran_full_pyjhora.json")
    athena = _load_payload("references/out/athena_full_pyjhora.json")

    report = compute_ashtakoota_matching(mehran, athena)
    total = report["total"]
    assert total["score"] is not None
    assert total["max"] == 36.0
    ashtakoota = report["ashtakoota"]["components"]
    assert "nadi" in ashtakoota
    assert ashtakoota["nadi"]["max"] == 8.0

    doshas = report["dosha_flags"]
    bool_count = sum(isinstance(value, bool) for value in doshas.values())
    assert bool_count >= 2
    assert isinstance(report["narrative_flags"], list)
    assert "naalu_porutham" in report
    assert report["naalu_porutham"]["Mahendra"]["is_compatible"] in (True, False)
    assert "filters" in report
    assert report["filters"]["flags"]["meets_min_score"] in (True, False)


def test_matching_optional_blocks_can_be_disabled() -> None:
    mehran = _load_payload("references/out/mehran_full_pyjhora.json")
    athena = _load_payload("references/out/athena_full_pyjhora.json")

    report = compute_ashtakoota_matching(
        mehran,
        athena,
        include_naalu_porutham=False,
        include_filters=False,
    )
    assert "naalu_porutham" not in report
    assert "filters" not in report
