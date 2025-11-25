from pathlib import Path
from typing import Optional


def find_package_root(start: Path, package: str = "jhora") -> Path:
    """
    Walk upwards from `start` until a directory containing `package/` is found.
    Raise RuntimeError if not found.
    """
    start = start.resolve()
    for directory in [start] + list(start.parents):
        candidate = directory / package
        if candidate.exists() and candidate.is_dir():
            return directory
        # also check common src layout: src/<package>
        candidate2 = directory / "src" / package
        if candidate2.exists() and candidate2.is_dir():
            return directory
    raise RuntimeError(f"Package root containing '{package}' not found starting from {start}")
