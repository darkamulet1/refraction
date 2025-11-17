from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from jhora.panchanga import drik

from v0min.core_time import BirthContext, make_birth_context
from v0min.full_extract import build_full_pyjhora_payload
from v0min.varshaphal_extract import (
    compute_maasa_snapshots,
    compute_sixty_hour_snapshots,
    compute_varshaphal_snapshot,
)


def _make_birth_context() -> BirthContext:
    return make_birth_context(
        datetime(1997, 6, 7, 20, 28, 36),
        35.6892,
        51.3890,
        tz_name="Asia/Tehran",
        location_name="Tehran",
    )


def _make_context() -> dict:
    bc = _make_birth_context()
    place = drik.Place("Tehran", bc.latitude, bc.longitude, bc.utc_offset_hours)
    return {
        "birth_context": bc,
        "place": place,
        "ayanamsa_mode": "LAHIRI",
        "location_name": "Tehran",
    }


def test_varshaphal_snapshot_structure() -> None:
    ctx = _make_context()
    snapshot = compute_varshaphal_snapshot(ctx, 2025)
    assert snapshot["schema_version"] == "varshaphal.v1"
    assert snapshot["year"] == 2025
    assert "chart" in snapshot and "lagna" in snapshot["chart"]
    assert snapshot["varshesh"]["planet"]
    assert snapshot["muntha"]["house_number"] == snapshot["muntha"]["house_index"] + 1
    assert snapshot["sahams"]
    assert snapshot["dashas"]["varsha_vimsottari"]
    assert snapshot["dashas"]["varsha_narayana"]
    assert snapshot["tajaka_aspects"]["benefic_aspects"]


def test_full_extract_varshaphal_gate() -> None:
    bc = _make_birth_context()
    payload_no_varshaphal = build_full_pyjhora_payload(bc, person="Mehran", location_name="Tehran")
    assert "varshaphal" not in payload_no_varshaphal

    cfg = {"varshaphal": {"years": [2025]}}
    payload_with_varshaphal = build_full_pyjhora_payload(
        bc,
        person="Mehran",
        location_name="Tehran",
        extraction_config=cfg,
    )
    assert "varshaphal" in payload_with_varshaphal
    assert "2025" in payload_with_varshaphal["varshaphal"]
    assert "subperiods" not in payload_with_varshaphal["varshaphal"]["2025"]

    cfg_sub = {
        "varshaphal": {
            "years": [2025],
            "include_maasa": True,
            "include_sixty_hour": True,
        }
    }
    payload_with_subperiods = build_full_pyjhora_payload(
        bc,
        person="Mehran",
        location_name="Tehran",
        extraction_config=cfg_sub,
    )
    year_block = payload_with_subperiods["varshaphal"]["2025"]
    assert "subperiods" in year_block
    assert year_block["subperiods"]["maasa"]
    assert year_block["subperiods"]["sixty_hour"]


def test_maasa_snapshots_mehran() -> None:
    ctx = _make_context()
    maasa = compute_maasa_snapshots(ctx, 2025, months=[1, 2])
    assert len(maasa) == 2
    snap = maasa[0]
    assert snap["schema_version"] == "varshaphal.maasa.v1"
    assert "chart" in snap
    assert "return_datetime_local" in snap


def test_sixty_hour_snapshots_mehran() -> None:
    ctx = _make_context()
    sixty = compute_sixty_hour_snapshots(ctx, 2025, indices=[0, 1])
    assert len(sixty) == 2
    snap = sixty[0]
    assert snap["schema_version"] == "varshaphal.sixty_hour.v1"
    assert snap["index"] == 0
    assert "chart" in snap


def test_varshaphal_cli_smoke(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    out_path = tmp_path / "mehran_varshaphal_2025.json"
    cmd = [
        sys.executable,
        "scripts/varshaphal_cli.py",
        "--birth-json",
        "references/out/mehran_full_pyjhora.json",
        "--year",
        "2025",
        "--include",
        "sahams",
        "--include-maasa",
        "--maasa-months",
        "1",
        "2",
        "--include-sixty-hour",
        "--sixty-indices",
        "0",
        "1",
        "--out",
        str(out_path),
        "--no-print",
    ]
    subprocess.check_call(cmd, cwd=repo_root)
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "varshaphal.v1"
    assert payload["year"] == 2025
    assert "subperiods" in payload
    assert payload["subperiods"]["maasa"]
    assert payload["subperiods"]["sixty_hour"]
