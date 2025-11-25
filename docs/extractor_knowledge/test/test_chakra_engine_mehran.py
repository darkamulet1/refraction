from __future__ import annotations

import json
from pathlib import Path

from v0min.chakra_extract import ChakraConfig, compute_chakra_snapshot

REF_PATH = Path("references/out/mehran_full_pyjhora.json")


def _load_payload() -> dict:
    return json.loads(REF_PATH.read_text(encoding="utf-8"))


def test_chakra_engine_sarvatobhadra_layer() -> None:
    payload = _load_payload()
    cfg = ChakraConfig(include_layers=["sarvatobhadra"])
    snapshot = compute_chakra_snapshot(payload, cfg)
    assert snapshot["schema_version"] == "chakra.v1"
    layers = snapshot["layers"]
    assert "sarvatobhadra" in layers
    layer = layers["sarvatobhadra"]
    assert layer["name"] == "Sarvatobhadra"
    assert layer["grid"], "Grid should not be empty"
    assert isinstance(layer["hits"], list)


def test_chakra_engine_kota_metadata() -> None:
    payload = _load_payload()
    cfg = ChakraConfig(include_layers=["kota"])
    snapshot = compute_chakra_snapshot(payload, cfg)
    layer = snapshot["layers"]["kota"]
    assert layer["meta"]["kota_lord"]
    assert layer["meta"]["kota_paala"]


def test_chakra_engine_extended_layers_present() -> None:
    payload = _load_payload()
    snapshot = compute_chakra_snapshot(payload, ChakraConfig())
    layers = snapshot["layers"]
    for key in ["tripataki", "surya_kalanala", "chandra_kalanala", "saptha_shalaka", "pancha_shalaka"]:
        assert key in layers
        assert layers[key]["grid"]


def test_chakra_layer_filtering() -> None:
    payload = _load_payload()
    cfg = ChakraConfig(include_layers=["tripataki", "surya_kalanala"])
    snapshot = compute_chakra_snapshot(payload, cfg)
    assert set(snapshot["layers"].keys()) == {"tripataki", "surya_kalanala"}
