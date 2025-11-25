from __future__ import annotations

import json
import random
from pathlib import Path

from v0min.prasna_extract import PrasnaConfig, compute_prasna_snapshot

REF_PATH = Path("references/out/mehran_full_pyjhora.json")


def _load_payload() -> dict:
    return json.loads(REF_PATH.read_text(encoding="utf-8"))


def test_prasna_snapshot_structure() -> None:
    payload = _load_payload()
    config = PrasnaConfig(scheme="KP_249", seed_mode="manual", manual_number=123)
    snapshot = compute_prasna_snapshot(payload, config=config)
    assert snapshot["schema_version"] == "prasna.v1"
    assert snapshot["mode"] == "KP_249"
    assert snapshot["number"] == 123
    chart = snapshot["chart"]
    assert "lagna" in chart and "planets" in chart
    assert len(chart["planets"]) == 9
    kp_block = snapshot["kp_adhipathi"]
    assert kp_block["scheme"] == "KP_249"
    assert len(kp_block["levels"]) == 6
    assert all(level["level"] for level in kp_block["levels"])
    kp_summary = snapshot["kp"]
    assert kp_summary["kp_number"] == kp_block["kp_number"]
    assert kp_summary["kp_chain"][0]["level"] == "nakshatra"


def test_prasna_kp_chain_depth() -> None:
    payload = _load_payload()
    full_config = PrasnaConfig(scheme="KP_249", seed_mode="manual", manual_number=111)
    full_snapshot = compute_prasna_snapshot(payload, config=full_config)
    assert len(full_snapshot["kp"]["kp_chain"]) == len(full_snapshot["kp_adhipathi"]["levels"])

    limited_config = PrasnaConfig(
        scheme="KP_249",
        seed_mode="manual",
        manual_number=111,
        kp_chain_max_depth=3,
    )
    limited_snapshot = compute_prasna_snapshot(payload, config=limited_config)
    chain = limited_snapshot["kp"]["kp_chain"]
    assert len(chain) == 3
    assert [entry["level"] for entry in chain] == ["nakshatra", "sub", "pratyanttara"]


def test_prasna_seed_modes_manual_and_time_seed() -> None:
    payload = _load_payload()
    manual_config = PrasnaConfig(scheme="KP_249", seed_mode="manual", manual_number=42)
    snap_a = compute_prasna_snapshot(payload, config=manual_config)
    snap_b = compute_prasna_snapshot(payload, config=manual_config)
    assert snap_a["number"] == snap_b["number"] == 42
    seed_info = snap_a["meta"]["seed_info"]
    assert seed_info["mode"] == "manual"
    assert seed_info["source"] == "user_input"

    time_config = PrasnaConfig(
        scheme="KP_249",
        seed_mode="time_seed",
        time_override="2025-01-01T12:00:00",
    )
    snap_time_a = compute_prasna_snapshot(payload, config=time_config)
    snap_time_b = compute_prasna_snapshot(payload, config=time_config)
    assert snap_time_a["number"] == snap_time_b["number"]
    time_seed_info = snap_time_a["meta"]["seed_info"]
    assert time_seed_info["mode"] == "time_seed"
    assert time_seed_info["source"] == "system_time"
    assert time_seed_info["value"] == "2025-01-01T12:00:00"


def test_prasna_random_seed_determinism() -> None:
    payload = _load_payload()
    random_config = PrasnaConfig(
        scheme="KP_249",
        seed_mode="random",
        random_seed=98765,
    )
    snap_a = compute_prasna_snapshot(payload, config=random_config)
    snap_b = compute_prasna_snapshot(payload, config=random_config)
    assert snap_a["number"] == snap_b["number"]
    assert snap_a["meta"]["seed_info"]["random_seed"] == 98765

    random_config_2 = PrasnaConfig(
        scheme="KP_249",
        seed_mode="random",
        random_seed=123,
    )
    snap_c = compute_prasna_snapshot(payload, config=random_config_2)
    expected = random.Random(123).randint(1, 249)
    assert snap_c["number"] == expected
