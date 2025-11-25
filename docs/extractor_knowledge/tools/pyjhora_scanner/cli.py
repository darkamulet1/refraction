from pathlib import Path
import sys
import os
from .fs_utils import find_package_root
from .config import ScannerConfig
from .module_loader import iter_modules
from .api_scanner import scan_module
from .const_parser import parse_const
from .experimental_scanner import scan_file_for_experimental
from .tests_scanner import scan_tests
from .model import ScanResult
from .generate_markdown import generate_markdown
from .generate_summary import write_summary
from .api_inventory import generate_api_inventory


def run_scanner(start: Path | None = None) -> None:
    start = Path(start or Path.cwd())
    repo_root = find_package_root(start, "jhora")
    # ensure repo root is on path so imports work
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    config = ScannerConfig(pyjhora_root=repo_root)

    # import modules
    try:
        modules = iter_modules(config.root_package)
    except Exception as e:
        print(f"Failed to iter modules: {e}")
        modules = {}

    scan = ScanResult()
    scan.version = getattr(__import__(config.root_package), "__version__", None) or "4.5.5"
    scan.root_package = config.root_package

    # scan modules
    for name, mod in modules.items():
        if mod is None:
            # attempt to locate file
            scan.package_tree[name] = None
            continue
        try:
            minfo = scan_module(mod)
            scan.package_tree[name] = minfo
            # detect experimental by file scan
            if minfo.path:
                hits = scan_file_for_experimental(minfo.path)
                if hits:
                    scan.experimental_modules.append(name)
                    for h in hits:
                        if h not in minfo.experimental_flags:
                            minfo.experimental_flags.append(h)
        except Exception:
            continue

    # parse const.py
    cp, defaults = parse_const(repo_root)
    scan.core_primitives = cp
    scan.defaults.update(defaults)

    # scan tests
    tests_root = repo_root / "jhora" / "tests"
    scan.tests = scan_tests(tests_root)

    # discover data files under jhora/data
    data_dir = repo_root / "jhora" / "data"
    if data_dir.exists():
        for f in data_dir.rglob("*"):
            if f.is_file():
                scan.data_files.append({"path": str(f.relative_to(repo_root)), "purpose": "", "consumers": []})

    # categorize modules
    for name, minfo in list(scan.package_tree.items()):
        if name and ".horoscope.dhasa" in name:
            scan.dasha_modules[name] = minfo
        if name and ".horoscope.transit" in name:
            scan.transit_modules[name] = minfo
        if name and ".horoscope.match" in name:
            scan.match_modules[name] = minfo
        if name and ".horoscope.prediction" in name:
            scan.prediction_modules[name] = minfo

    # Determine safe entry points: functions in panchanga.drik, horoscope.chart.charts, horoscope.chart.strength
    for modname, minfo in scan.package_tree.items():
        if not minfo:
            continue
        if modname.startswith("jhora.panchanga.drik") or ".horoscope.chart.charts" in modname or ".horoscope.chart.strength" in modname:
            for f in minfo.functions:
                if f.is_public and modname not in scan.experimental_modules:
                    scan.safe_entry_points.append(f"{modname}.{f.name}")

    # ensure unique
    scan.safe_entry_points = sorted(set(scan.safe_entry_points))
    scan.experimental_modules = sorted(set(scan.experimental_modules))

    # generate markdown & summary
    md = generate_markdown(scan)
    md_path = repo_root / "PyJHora_Structural_Map.md"
    md_path.write_text(md, encoding="utf-8")

    summary_path = repo_root / "PyJHora_Structural_Map_summary.json"
    write_summary(scan, summary_path)

    # generate API inventory JSON
    try:
        api_inventory = generate_api_inventory(scan)
        import json

        api_path = repo_root / "PyJHora_API_Inventory.json"
        api_path.write_text(json.dumps(api_inventory, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote: {api_path}")
    except Exception as e:
        print(f"Failed to write API inventory: {e}")

    print(f"Wrote: {md_path}")
    print(f"Wrote: {summary_path}")


if __name__ == "__main__":
    run_scanner(Path.cwd())
