from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_dosha_cli_smoke(tmp_path: Path) -> None:
    out_path = tmp_path / "mehran_dosha.json"
    cmd = [
        sys.executable,
        "scripts/dosha_cli.py",
        "--birth-json",
        "references/out/mehran_full_pyjhora.json",
        "--out",
        str(out_path),
        "--no-print",
    ]
    subprocess.check_call(cmd, cwd=Path(__file__).resolve().parents[2])
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "dosha.v1"
