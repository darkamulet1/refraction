from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_muhurta_cli_smoke(tmp_path: Path) -> None:
    out_path = tmp_path / "mehran_muhurta.json"
    cmd = [
        sys.executable,
        "scripts/muhurta_cli.py",
        "--birth-json",
        "references/out/mehran_full_pyjhora.json",
        "--activity",
        "CLASS_START",
        "--start-date",
        "2025-06-07",
        "--end-date",
        "2025-06-07",
        "--step-minutes",
        "60",
        "--max-windows",
        "5",
        "--out",
        str(out_path),
        "--no-print",
    ]
    subprocess.check_call(cmd, cwd=Path(__file__).resolve().parents[2])
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == "muhurta.v1"
