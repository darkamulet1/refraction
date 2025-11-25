from __future__ import annotations

import json
from pathlib import Path

from v0min.bhava_systems_extract import BhavaSystemsConfig, compute_bhava_systems_from_payload


def _load_payload() -> dict:
    return json.loads(Path("references/out/mehran_full_pyjhora.json").read_text(encoding="utf-8"))


def test_bhava_systems_multiple_methods() -> None:
    payload = _load_payload()
    cfg = BhavaSystemsConfig(methods=["1", "3", "P"])
    block = compute_bhava_systems_from_payload(payload, cfg)
    assert block["schema_version"] == "bhava_systems.v1"
    methods = block["methods"]
    assert len(methods) == 3
    codes = {entry["method_code"] for entry in methods}
    assert {"1", "3", "P"}.issubset(codes)
    sripati = next(entry for entry in methods if entry["method_code"] == "3")
    placidus = next(entry for entry in methods if entry["method_code"].upper() == "P")
    sripati_cusps = [round(h["cusp_deg"], 4) for h in sripati["houses"]]
    placidus_cusps = [round(h["cusp_deg"], 4) for h in placidus["houses"]]
    assert sripati_cusps != placidus_cusps
