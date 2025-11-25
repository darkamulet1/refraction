from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from jhora import const

from v0min.core_time import make_birth_context
from v0min.full_extract import build_full_pyjhora_payload
from v0min.special_points_extract import compute_special_points_block


def _load_payload() -> dict:
    return json.loads(Path("references/out/mehran_full_pyjhora.json").read_text(encoding="utf-8"))


def _make_birth_context():
    return make_birth_context(
        datetime(1997, 6, 7, 20, 28, 36),
        35.6892,
        51.3890,
        tz_name="Asia/Tehran",
        location_name="Tehran",
    )


def test_special_points_block_structure() -> None:
    payload = _load_payload()
    block = compute_special_points_block(payload)
    assert block["schema_version"] == "special_points.v1"
    assert "arudhas" in block
    assert "sphutas" in block
    lagna_arudhas = block["arudhas"]["lagna_arudhas"]
    assert isinstance(lagna_arudhas, dict)
    first_entry = next(iter(lagna_arudhas.values()))
    assert 0 <= first_entry["sign_index"] <= 11
    points = block["sphutas"]["points"]
    assert points
    first_point = points[0]
    assert 0 <= first_point["longitude_deg"] < 360.0
    assert 1 <= first_point["house"] <= 12


def test_full_extract_special_points_gating() -> None:
    bc = _make_birth_context()
    payload = build_full_pyjhora_payload(bc, person="Mehran", location_name="Tehran")
    assert "special_points" not in payload

    cfg = {"special_points": {"enabled": True}}
    payload_with_special = build_full_pyjhora_payload(
        bc,
        person="Mehran",
        location_name="Tehran",
        extraction_config=cfg,
    )
    assert "special_points" in payload_with_special


def test_special_points_cli_smoke(tmp_path: Path) -> None:
    out_path = tmp_path / "mehran_special_points.json"
    cmd = [
        sys.executable,
        "scripts/special_points_cli.py",
        "--birth-json",
        "references/out/mehran_full_pyjhora.json",
        "--include-arudhas",
        "--include-sphutas",
        "--include-special-charts",
        "--out",
        str(out_path),
        "--no-print",
    ]
    subprocess.check_call(cmd, cwd=Path(__file__).resolve().parents[2])
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "special_points.v1"


def test_upagraha_block_mehran() -> None:
    payload = _load_payload()
    cfg = {
        "enabled": True,
        "include_arudhas": False,
        "include_sphutas": False,
        "include_special_charts": False,
        "include_upagrahas": True,
        "include_graha_drishti": False,
        "include_pinda": False,
        "include_sahamas": False,
        "include_star_metrics": False,
    }
    block = compute_special_points_block(payload, config=cfg)
    upagraha_block = block["upagraha"]
    assert upagraha_block["schema_version"] == "upagraha.v1"
    names = {entry["name"] for entry in upagraha_block["entries"]}
    ids = {entry["id"] for entry in upagraha_block["entries"]}
    expected = {"Dhuma", "Vyatipata", "Parivesha", "Indrachapa", "Kaala", "Mrityu", "Yamagandaka", "Gulika", "Mandi"}
    assert expected.issubset(names)
    for entry in upagraha_block["entries"]:
        assert entry["id"].startswith("UPAGRAHA_")


def test_sahama_block_has_all_entries() -> None:
    payload = _load_payload()
    cfg = {
        "enabled": True,
        "include_arudhas": False,
        "include_sphutas": False,
        "include_special_charts": False,
        "include_upagrahas": False,
        "include_graha_drishti": False,
        "include_pinda": False,
        "include_sahamas": True,
        "include_star_metrics": False,
    }
    block = compute_special_points_block(payload, config=cfg)
    saham_block = block["sahamas"]
    assert saham_block["schema_version"] == "sahama.v1"
    entries = saham_block["entries"]
    assert len(entries) == len(const._saham_list)
    ids = {entry["id"].lower() for entry in entries}
    expected_ids = {f"sahama_{name}" for name in const._saham_list}
    assert expected_ids.issubset(ids)


def test_star_metrics_block_structure() -> None:
    payload = _load_payload()
    cfg = {
        "enabled": True,
        "include_arudhas": False,
        "include_sphutas": False,
        "include_special_charts": False,
        "include_upagrahas": False,
        "include_graha_drishti": False,
        "include_pinda": False,
        "include_sahamas": False,
        "include_star_metrics": True,
    }
    block = compute_special_points_block(payload, config=cfg)
    metrics = block["star_metrics"]
    assert metrics["schema_version"] == "star_metrics.v1"
    assert "mrityu_bhaga" in metrics
    assert "pushkara_points" in metrics
    assert "meta" in metrics
    assert "supported_metrics" in metrics["meta"]
