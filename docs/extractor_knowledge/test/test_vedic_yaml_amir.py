from __future__ import annotations

import json
from pathlib import Path

import yaml


def test_vedic_yaml_amir_parity() -> None:
    json_path = Path("references/out/amir_roozegari_full_pyjhora.json")
    yaml_path = Path("references/out/amir_roozegari_vedic_master_v2.yaml")

    json_payload = json.loads(json_path.read_text(encoding="utf-8"))
    vedic = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))

    d1_yaml = vedic["core_charts"]["D1"]["lagna"]["degree"]
    d1_json = json_payload["core_chart"]["lagna_longitude_deg"]
    assert abs(d1_yaml - d1_json) < 1e-6

    assert "D10" in vedic["core_charts"]
    assert vedic["core_charts"]["D10"]["lagna"]["sign"] == "Virgo"

    bav_yaml_sum = sum(vedic["ashtakavarga"]["BAV"]["Sun"])
    bav_json_sum = sum(json_payload["ashtakavarga"]["binna_ashtakavarga"]["Sun☉"])
    assert bav_yaml_sum == bav_json_sum

    assert (
        vedic["strength"]["shadbala"]["Jupiter"]["percent"]
        == json_payload["strength"]["shadbala"]["Jupiter"]["percent"]
    )
