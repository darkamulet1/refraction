from pathlib import Path
from typing import List

MARKERS = ["EXPERIMENTAL", "NOT FULLY IMPLEMENTED", "UNDER TESTING", "TODO"]


def scan_file_for_experimental(path: Path) -> List[str]:
    hits = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return hits
    upper = text.upper()
    for m in MARKERS:
        if m in upper:
            hits.append(m)
    return hits
