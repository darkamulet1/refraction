from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_prasna_cli_smoke(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    out_path = tmp_path / "prasna_manual.json"
    cmd_manual = [
        sys.executable,
        "scripts/prasna_cli.py",
        "--birth-json",
        "references/out/mehran_full_pyjhora.json",
        "--scheme",
        "KP_249",
        "--mode",
        "manual",
        "--number",
        "123",
        "--kp-max-depth",
        "3",
        "--out",
        str(out_path),
    ]
    subprocess.check_call(cmd_manual, cwd=repo_root)
    data_manual = json.loads(out_path.read_text(encoding="utf-8"))
    assert data_manual["schema_version"] == "prasna.v1"
    assert len(data_manual["kp"]["kp_chain"]) == 3

    out_random = tmp_path / "prasna_random.json"
    cmd_random = [
        sys.executable,
        "scripts/prasna_cli.py",
        "--birth-json",
        "references/out/mehran_full_pyjhora.json",
        "--scheme",
        "PRASNA_108",
        "--mode",
        "random",
        "--random-seed",
        "77",
        "--out",
        str(out_random),
    ]
    subprocess.check_call(cmd_random, cwd=repo_root)
    data_random = json.loads(out_random.read_text(encoding="utf-8"))
    assert data_random["meta"]["seed_info"]["mode"] == "random"
    assert data_random["meta"]["seed_info"]["random_seed"] == 77
