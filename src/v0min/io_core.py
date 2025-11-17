from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Union

import yaml


PathLike = Union[str, Path]


def save_core_chart(path: PathLike, payload: Dict[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return target


def load_core_chart(path: PathLike) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data or {}


__all__ = ["save_core_chart", "load_core_chart"]
