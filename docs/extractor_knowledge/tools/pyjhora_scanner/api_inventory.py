from pathlib import Path
from typing import Dict, Any
from .model import ScanResult


def generate_api_inventory(scan: ScanResult) -> dict:
    """
    Build a machine-readable API inventory from ScanResult.

    Structure:
    {
      "root_package": "jhora",
      "version": "<version>",
      "modules": { ... }
    }
    """
    modules_block: Dict[str, Any] = {}

    for mname, minfo in scan.package_tree.items():
        # handle case where minfo may be None
        if not minfo:
            modules_block[mname] = {"experimental": False, "functions": {}}
            continue

        functions_block: Dict[str, Any] = {}
        for finfo in (minfo.functions or []):
            # include all functions (public and private) — consumer can filter by is_public
            functions_block[finfo.name] = {
                "signature": finfo.signature,
                "is_public": finfo.is_public,
                "experimental": getattr(finfo, "experimental", False),
                "docstring": (finfo.docstring or "").strip() or None,
            }

        modules_block[mname] = {
            "experimental": bool(minfo.experimental_flags),
            "experimental_flags": minfo.experimental_flags,
            "functions": functions_block,
        }

    return {
        "root_package": scan.root_package,
        "version": scan.version or "UNKNOWN",
        "modules": modules_block,
    }
