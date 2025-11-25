from __future__ import annotations

import json
from pathlib import Path

from v0min.dosha_extract import compute_dosha_block


def _load_payload() -> dict:
    return json.loads(Path("references/out/mehran_full_pyjhora.json").read_text(encoding="utf-8"))


def test_dosha_block_structure() -> None:
    payload = _load_payload()
    block = compute_dosha_block(payload)
    assert block["schema_version"] == "dosha.v1"
    assert block["engine"] == "PYJHORA_DOSHA"
    d1_entries = block["by_chart"].get("D1")
    assert isinstance(d1_entries, list)
    assert all("id" in entry for entry in d1_entries)
    # ensure summary is coherent
    summary = block["summary"]
    assert "counts_by_category" in summary
    assert isinstance(summary["counts_by_category"], dict)
