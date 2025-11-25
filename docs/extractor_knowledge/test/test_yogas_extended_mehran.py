from __future__ import annotations

import json
from pathlib import Path

from v0min.yogas_extended_extract import YogasExtendedConfig, compute_yogas_extended_from_payload


def _load_payload() -> dict:
    return json.loads(Path("references/out/mehran_full_pyjhora.json").read_text(encoding="utf-8"))


def test_yogas_extended_block_structure() -> None:
    payload = _load_payload()
    cfg = YogasExtendedConfig(charts=["D1", "D9"], language="en", include_kaala_sarpa_variants=True)
    block = compute_yogas_extended_from_payload(payload, cfg)
    assert block["schema_version"] == "yogas_extended.v1"
    entries = block["entries"]
    assert isinstance(entries, list)
    assert entries, "Expected at least one yoga entry."
    families = {entry.get("family") for entry in entries}
    assert families
    assert all(entry.get("present") for entry in entries)
    cfg_no_ks = YogasExtendedConfig(charts=["D1"], language="en", include_kaala_sarpa_variants=False)
    block_no_ks = compute_yogas_extended_from_payload(payload, cfg_no_ks)
    ks_entries = [entry for entry in block["entries"] if entry.get("family") == "kaala_sarpa"]
    if ks_entries:
        assert not any(entry.get("family") == "kaala_sarpa" for entry in block_no_ks["entries"])
