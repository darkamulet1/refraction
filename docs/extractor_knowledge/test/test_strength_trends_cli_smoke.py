from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_strength_trends_cli_smoke(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    out_path = tmp_path / "strength_trends.json"
    cmd = [
        sys.executable,
        "scripts/strength_trends_cli.py",
        "--birth-json",
        "references/out/mehran_full_pyjhora.json",
        "--out",
        str(out_path),
        "--no-print",
    ]
    subprocess.check_call(cmd, cwd=repo_root)
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == "strength_trends.v1"
    assert data["planet_ranking"]
