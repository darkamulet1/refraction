from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_yogas_extended_cli_smoke(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    out_path = tmp_path / "yogas_extended.json"
    cmd = [
        sys.executable,
        "scripts/yogas_extended_cli.py",
        "--birth-json",
        "references/out/mehran_full_pyjhora.json",
        "--charts",
        "D1",
        "--language",
        "en",
        "--out",
        str(out_path),
        "--no-print",
    ]
    subprocess.check_call(cmd, cwd=repo_root)
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "yogas_extended.v1"
    assert isinstance(payload.get("entries"), list)
