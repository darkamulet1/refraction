from pathlib import Path
import sys

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))

from tools.pyjhora_scanner.fs_utils import find_package_root
from tools.pyjhora_scanner.config import ScannerConfig
from tools.pyjhora_scanner.module_loader import iter_modules
from tools.pyjhora_scanner.api_scanner import scan_module
from tools.pyjhora_scanner.const_parser import parse_const
from tools.pyjhora_scanner.experimental_scanner import scan_file_for_experimental
from tools.pyjhora_scanner.tests_scanner import scan_tests
from tools.pyjhora_scanner.model import ScanResult
from tools.pyjhora_scanner.generate_markdown import generate_markdown
from tools.pyjhora_scanner.generate_summary import write_summary


def main():
    start = Path.cwd()
    try:
        repo_root = find_package_root(start, "jhora")
    except RuntimeError as e:
        print(str(e))
        return

    config = ScannerConfig(pyjhora_root=repo_root)

    try:
        modules = iter_modules(config.root_package)
    except Exception as e:
        print(f"Failed to import modules: {e}")
        modules = {}

    scan = ScanResult()
    # try to get version
    try:
        pkg = __import__(config.root_package)
        scan.version = getattr(pkg, "__version__", None) or "UNKNOWN"
    except Exception:
        scan.version = "UNKNOWN"

    scan.root_package = config.root_package

    for name, mod in modules.items():
        if mod is None:
            scan.package_tree[name] = None
            continue
        try:
            minfo = scan_module(mod)
            scan.package_tree[name] = minfo
            if minfo.path:
                hits = scan_file_for_experimental(minfo.path)
                if hits:
                    scan.experimental_modules.append(name)
                    for h in hits:
                        if h not in minfo.experimental_flags:
                            minfo.experimental_flags.append(h)
        except Exception:
            continue

    cp, defaults = parse_const(repo_root)
    scan.core_primitives = cp
    scan.defaults.update(defaults)

    tests_root = repo_root / "jhora" / "tests"
    scan.tests = scan_tests(tests_root)

    data_dir = repo_root / "jhora" / "data"
    if data_dir.exists():
        for f in data_dir.rglob("*"):
            if f.is_file():
                scan.data_files.append({"path": str(f.relative_to(repo_root)), "purpose": "", "consumers": []})

    for name, minfo in list(scan.package_tree.items()):
        if name and ".horoscope.dhasa" in name:
            scan.dasha_modules[name] = minfo
        if name and ".horoscope.transit" in name:
            scan.transit_modules[name] = minfo
        if name and ".horoscope.match" in name:
            scan.match_modules[name] = minfo
        if name and ".horoscope.prediction" in name:
            scan.prediction_modules[name] = minfo

    for modname, minfo in scan.package_tree.items():
        if not minfo:
            continue
        if modname.startswith("jhora.panchanga.drik") or ".horoscope.chart.charts" in modname or ".horoscope.chart.strength" in modname:
            for f in minfo.functions:
                if f.is_public and modname not in scan.experimental_modules:
                    scan.safe_entry_points.append(f"{modname}.{f.name}")

    scan.safe_entry_points = sorted(set(scan.safe_entry_points))
    scan.experimental_modules = sorted(set(scan.experimental_modules))

    md = generate_markdown(scan)
    md_path = repo_root / "PyJHora_Structural_Map.md"
    md_path.write_text(md, encoding="utf-8")

    summary_path = repo_root / "PyJHora_Structural_Map_summary.json"
    write_summary(scan, summary_path)

    print(f"Wrote: {md_path}")
    print(f"Wrote: {summary_path}")


if __name__ == '__main__':
    main()

