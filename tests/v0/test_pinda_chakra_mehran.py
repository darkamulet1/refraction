from __future__ import annotations

import json
from pathlib import Path

from v0min.special_points_extract import compute_special_points_block


def _load_payload() -> dict:
    payload_path = Path("references/out/mehran_full_pyjhora.json")
    return json.loads(payload_path.read_text(encoding="utf-8"))


def test_pinda_chakra_values() -> None:
    payload = _load_payload()
    cfg = {
        "enabled": True,
        "include_arudhas": False,
        "include_sphutas": False,
        "include_special_charts": False,
        "include_graha_drishti": False,
        "include_pinda": True,
    }
    block = compute_special_points_block(payload, config=cfg)
    pinda_section = block["pinda_chakra"]
    d1_entry = pinda_section["D1"]
    assert d1_entry["schema_version"] == "pinda_chakra.v1"
    values = d1_entry["values"]
    assert len(values) == 7
    for entry in values:
        assert entry["planet"]
        lhs = round(entry["raasi_pinda"] + entry["graha_pinda"], 6)
        rhs = round(entry["sodhya_pinda"], 6)
        assert lhs == rhs
