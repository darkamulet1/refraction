import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


def load_json(relative_path: str):
    path = BASE_DIR / relative_path
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
