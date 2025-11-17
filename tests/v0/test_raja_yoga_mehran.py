from __future__ import annotations

import json
from pathlib import Path

from v0min.raja_yoga_extract import compute_raja_yoga_block


def _load_payload() -> dict:
    return json.loads(Path("references/out/mehran_full_pyjhora.json").read_text(encoding="utf-8"))


def test_raja_yoga_block_structure() -> None:
    payload = _load_payload()
    block = compute_raja_yoga_block(payload)
    assert block["schema_version"] == "raja_yoga.v1"
    assert block["engine"] == "PYJHORA_RAJA_YOGA"
    assert "D1" in block["by_chart"]
    entries = block["by_chart"]["D1"]
    assert isinstance(entries, list)
    assert all(entry.get("is_present") for entry in entries)
