from dataclasses import dataclass
from pathlib import Path


@dataclass
class ScannerConfig:
    pyjhora_root: Path
    root_package: str = "jhora"
