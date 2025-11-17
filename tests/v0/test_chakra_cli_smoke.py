from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_chakra_cli_smoke(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    out_path = tmp_path / "chakra_full.json"
    cmd_full = [
        sys.executable,
        "scripts/chakra_cli.py",
        "--birth-json",
        "references/out/mehran_full_pyjhora.json",
        "--out",
        str(out_path),
    ]
    subprocess.check_call(cmd_full, cwd=repo_root)
    data_full = json.loads(out_path.read_text(encoding="utf-8"))
    assert data_full["schema_version"] == "chakra.v1"
    assert "surya_kalanala" in data_full["layers"]

    filtered_path = tmp_path / "chakra_filtered.json"
    cmd_filtered = [
        sys.executable,
        "scripts/chakra_cli.py",
        "--birth-json",
        "references/out/mehran_full_pyjhora.json",
        "--layers",
        "tripataki,surya_kalanala",
        "--out",
        str(filtered_path),
    ]
    subprocess.check_call(cmd_filtered, cwd=repo_root)
    data_filtered = json.loads(filtered_path.read_text(encoding="utf-8"))
    assert set(data_filtered["layers"].keys()) == {"tripataki", "surya_kalanala"}
