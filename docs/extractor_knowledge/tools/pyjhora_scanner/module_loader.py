import importlib
import pkgutil
import sys
from types import ModuleType
from typing import Dict


def iter_modules(package_name: str) -> Dict[str, ModuleType]:
    """
    Import `package_name` and walk all submodules using pkgutil.walk_packages.
    Return a dict: full_module_name -> module object.
    """
    modules = {}
    # Ensure package is importable
    pkg = importlib.import_module(package_name)
    if not hasattr(pkg, "__path__"):
        # single-file package
        modules[package_name] = pkg
        return modules

    for finder, name, ispkg in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        if name.split(".")[-1] == "setup":
            continue
        try:
            mod = importlib.import_module(name)
            modules[name] = mod
        except Exception:
            # import failures are tolerated; add placeholder
            modules[name] = None
    # ensure base package present
    modules.setdefault(package_name, pkg)
    return modules
