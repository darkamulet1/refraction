from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_dasha_cli_smoke(tmp_path: Path) -> None:
    out_path = tmp_path / "mehran_VIMSHOTTARI_dasha_full.json"
    cmd = [
        sys.executable,
        "scripts/dasha_cli.py",
        "--birth-json",
        "references/out/mehran_full_pyjhora.json",
        "--system",
        "VIMSHOTTARI",
        "--out",
        str(out_path),
        "--no-print",
    ]
    subprocess.check_call(cmd, cwd=Path(__file__).resolve().parents[2])
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["meta"]["system"] == "VIMSHOTTARI"
    assert payload["meta"]["system_type"] == "GRAHA"
    assert payload["timeline"]

    raasi_out = tmp_path / "mehran_LAGNAMSAKA_dasha_full.json"
    cmd_raasi = [
        sys.executable,
        "scripts/dasha_cli.py",
        "--birth-json",
        "references/out/mehran_full_pyjhora.json",
        "--system",
        "LAGNAMSAKA_RAASI",
        "--out",
        str(raasi_out),
        "--no-print",
    ]
    subprocess.check_call(cmd_raasi, cwd=Path(__file__).resolve().parents[2])
    raasi_payload = json.loads(raasi_out.read_text(encoding="utf-8"))
    assert raasi_payload["meta"]["system"] == "LAGNAMSAKA_RAASI"
    assert raasi_payload["meta"]["system_type"] == "RAASI"
    assert raasi_payload["timeline"]
