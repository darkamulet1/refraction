from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_planet_friendships_cli_smoke(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    out_path = tmp_path / "friendships.json"
    cmd = [
        sys.executable,
        "scripts/planet_friendships_cli.py",
        "--birth-json",
        "references/out/mehran_full_pyjhora.json",
        "--out",
        str(out_path),
        "--no-print",
    ]
    subprocess.check_call(cmd, cwd=repo_root)
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == "planet_friendships.v1"
    assert data["entries"]
