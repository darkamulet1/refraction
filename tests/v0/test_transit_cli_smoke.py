from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


def test_transit_cli_smoke(tmp_path: Path) -> None:
    out_path = tmp_path / "transit.json"
    cmd = [
        sys.executable,
        "scripts/transit_cli.py",
        "--birth-json",
        "references/out/mehran_full_pyjhora.json",
        "--transit-date",
        "2025-01-01",
        "--transit-time",
        "12:00:00",
        "--out",
        str(out_path),
        "--print-only",
    ]
    subprocess.check_call(cmd, cwd=Path(__file__).resolve().parents[2])
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "transit.v1"
    assert payload["grahas"]
