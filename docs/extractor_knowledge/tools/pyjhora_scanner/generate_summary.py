import json
from pathlib import Path
from .model import ScanResult


def write_summary(scan: ScanResult, path: Path) -> None:
    summary = {
        "version": scan.version or "UNKNOWN",
        "root_package": scan.root_package,
        "default_ayanamsa": scan.defaults.get("ayanamsa_mode", "UNKNOWN"),
        "core_primitives": {
            "planets": len(scan.core_primitives.planets),
            "rasis": len(scan.core_primitives.rasis),
            "vargas": len(scan.core_primitives.vargas),
            "ayanamsa_modes": len(scan.core_primitives.ayanamsa),
            "house_systems": len(scan.core_primitives.house_systems),
        },
        "safe_entry_points": scan.safe_entry_points,
        "experimental_modules": scan.experimental_modules,
        "defaults": scan.defaults,
    }
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
