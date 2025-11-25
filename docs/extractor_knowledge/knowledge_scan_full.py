import ast
import importlib
import json
import sys
from pathlib import Path

# set up paths (this script runs from repo root)
repo_root = Path(__file__).resolve().parents[1]
venv_site = repo_root / ".venv" / "Lib" / "site-packages"
src_path = repo_root / "src"
for candidate in (str(venv_site), str(src_path), str(repo_root)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from tools.pyjhora_scanner.fs_utils import find_package_root
from tools.pyjhora_scanner.config import ScannerConfig
from tools.pyjhora_scanner.module_loader import iter_modules
from tools.pyjhora_scanner.api_scanner import scan_module
from tools.pyjhora_scanner.const_parser import parse_const
from tools.pyjhora_scanner.experimental_scanner import scan_file_for_experimental
from tools.pyjhora_scanner.tests_scanner import scan_tests
from tools.pyjhora_scanner.model import ScanResult, ModuleInfo, FunctionInfo
from tools.pyjhora_scanner.generate_markdown import generate_markdown
from tools.pyjhora_scanner.generate_summary import write_summary
from tools.pyjhora_scanner.api_inventory import generate_api_inventory

EXPERIMENTAL_MARKERS = ["EXPERIMENTAL", "NOT FULLY IMPLEMENTED", "UNDER TESTING", "TODO"]


def _resolve_package_package_dir(repo_dir: Path) -> Path:
    candidates = [
        repo_dir / "jhora",
        repo_dir / "src" / "jhora",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Cannot locate the jhora package directory under repository root")


def _find_module_path(package_dir: Path, module_name: str) -> Path | None:
    parts = module_name.split(".")
    if not parts or parts[0] != "jhora":
        return None
    rel_parts = parts[1:]
    if rel_parts and rel_parts[-1] == "__init__":
        rel_parts = rel_parts[:-1]
    if not rel_parts:
        candidate = package_dir / "__init__.py"
        return candidate if candidate.exists() else None

    module_rel = Path(*rel_parts)
    candidates = [
        package_dir / module_rel.with_suffix(".py"),
        package_dir / module_rel / "__init__.py",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _signature_from_ast(node: ast.FunctionDef) -> str:
    args = node.args
    params = []
    names = [arg.arg for arg in args.args]
    defaults = [None] * (len(names) - len(args.defaults)) + list(args.defaults)
    for name, default in zip(names, defaults):
        if default is not None:
            try:
                value = ast.unparse(default)
            except Exception:
                value = "..."
            params.append(f"{name}={value}")
        else:
            params.append(name)

    for name, default in zip(args.kwonlyargs, args.kw_defaults):
        if default is not None:
            try:
                value = ast.unparse(default)
            except Exception:
                value = "..."
            params.append(f"{name}={value}")
        else:
            params.append(name)

    if args.vararg:
        params.append(f"*{args.vararg.arg}")
    if args.kwarg:
        params.append(f"**{args.kwarg.arg}")
    return "(" + ", ".join(params) + ")"


def _scan_module_from_ast(module_name: str, package_dir: Path) -> ModuleInfo | None:
    module_path = _find_module_path(package_dir, module_name)
    if not module_path:
        return None
    try:
        source = module_path.read_text(encoding="utf-8")
    except Exception:
        return None

    try:
        tree = ast.parse(source)
    except Exception:
        return None

    docstring = ast.get_docstring(tree)
    m = ModuleInfo(name=module_name, path=module_path, docstring=docstring)

    normalized = source.upper()
    for marker in EXPERIMENTAL_MARKERS:
        if marker in normalized and marker not in m.experimental_flags:
            m.experimental_flags.append(marker)

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            name = node.name
            signature = _signature_from_ast(node)
            doc = ast.get_docstring(node)
            is_public = not name.startswith("_")
            experimental = False
            upper_doc = (doc or "").upper()
            upper_module = (docstring or "").upper()
            if any(marker in upper_doc for marker in EXPERIMENTAL_MARKERS) or any(
                marker in upper_module for marker in EXPERIMENTAL_MARKERS
            ):
                experimental = True
                for marker in EXPERIMENTAL_MARKERS:
                    if marker in upper_doc or marker in upper_module:
                        if marker not in m.experimental_flags:
                            m.experimental_flags.append(marker)

            m.functions.append(
                FunctionInfo(
                    name=name,
                    module=module_name,
                    signature=signature,
                    docstring=doc,
                    is_public=is_public,
                    experimental=experimental,
                )
            )

    return m


def _module_name_from_path(package_dir: Path, path: Path) -> str:
    rel = path.relative_to(package_dir)
    if rel.name == "__init__.py":
        parts = rel.parts[:-1]
    else:
        parts = rel.with_suffix("").parts
    if not parts:
        return "jhora"
    return "jhora." + ".".join(parts)

def build_scan() -> ScanResult:
    start = Path.cwd()
    repo_dir = find_package_root(start, "jhora")
    config = ScannerConfig(pyjhora_root=repo_dir)

    try:
        modules = iter_modules(config.root_package)
    except Exception:
        modules = {}

    package_dir = _resolve_package_package_dir(repo_dir)

    failures: dict[str, str] = {}
    for name, mod in list(modules.items()):
        if mod is None:
            try:
                importlib.import_module(name)
            except Exception as err:
                failures[name] = str(err)
            else:
                modules[name] = sys.modules.get(name)
    scan = ScanResult()
    try:
        pkg = importlib.import_module(config.root_package)
        scan.version = getattr(pkg, "__version__", None) or "UNKNOWN"
    except Exception:
        scan.version = "UNKNOWN"
    scan.root_package = config.root_package

    for name, mod in modules.items():
        if mod is None:
            ast_mod = _scan_module_from_ast(name, package_dir)
            if ast_mod:
                scan.package_tree[name] = ast_mod
                if ast_mod.path:
                    hits = scan_file_for_experimental(ast_mod.path)
                    if hits:
                        if name not in scan.experimental_modules:
                            scan.experimental_modules.append(name)
                        for h in hits:
                            if h not in ast_mod.experimental_flags:
                                ast_mod.experimental_flags.append(h)
                if ast_mod.experimental_flags and name not in scan.experimental_modules:
                    scan.experimental_modules.append(name)
            else:
                scan.package_tree[name] = None
            continue
        try:
            minfo = scan_module(mod)
        except Exception as err:
            failures[name] = failures.get(name, str(err))
            scan.package_tree[name] = None
            continue
        scan.package_tree[name] = minfo
        if minfo.path:
            hits = scan_file_for_experimental(minfo.path)
            if hits:
                if name not in scan.experimental_modules:
                    scan.experimental_modules.append(name)
                for h in hits:
                    if h not in minfo.experimental_flags:
                        minfo.experimental_flags.append(h)
        if minfo.experimental_flags and name not in scan.experimental_modules:
            scan.experimental_modules.append(name)

    cp, defaults = parse_const(repo_dir)
    scan.core_primitives = cp
    scan.defaults.update(defaults)

    tests_root = repo_dir / "jhora" / "tests"
    scan.tests = scan_tests(tests_root)

    data_dir = repo_dir / "jhora" / "data"
    if data_dir.exists():
        for f in sorted(data_dir.rglob("*")):
            if f.is_file():
                scan.data_files.append({"path": str(f.relative_to(repo_dir)), "purpose": "", "consumers": []})

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

    for py in package_dir.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        module_name = _module_name_from_path(package_dir, py)
        if not module_name:
            continue
        if scan.package_tree.get(module_name):
            continue
        ast_mod = _scan_module_from_ast(module_name, package_dir)
        if ast_mod:
            scan.package_tree[module_name] = ast_mod
            if ast_mod.experimental_flags and module_name not in scan.experimental_modules:
                scan.experimental_modules.append(module_name)

    # store failures for later logging
    scan.defaults.setdefault("module_failures", failures)
    scan.defaults.setdefault("scan_mode", "import-based (import + AST fallback)")
    return scan


def write_outputs(scan: ScanResult) -> dict[str, Path]:
    repo_dir = scan.defaults.get("pyjhora_root") or str(Path.cwd())
    root = Path(repo_dir)
    md_path = root / "PyJHora_Structural_Map.md"
    summary_path = root / "PyJHora_Structural_Map_summary.json"
    inv_path = root / "PyJHora_API_Inventory.json"

    md_path.write_text(generate_markdown(scan), encoding="utf-8")
    write_summary(scan, summary_path)
    inventory = generate_api_inventory(scan)
    inv_path.write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "structural_map": md_path,
        "summary": summary_path,
        "api_inventory": inv_path,
    }


def write_knowledge_copies(paths: dict[str, Path]) -> None:
    dest = Path("pyjhora_knowledge")
    dest.mkdir(exist_ok=True)
    (dest / "maps").mkdir(exist_ok=True)
    (dest / "inventory").mkdir(exist_ok=True)
    dest_map = dest / "maps" / paths["structural_map"].name
    dest_map.write_text(paths["structural_map"].read_text(encoding="utf-8"), encoding="utf-8")
    (dest / "maps" / paths["summary"].name).write_text(paths["summary"].read_text(encoding="utf-8"), encoding="utf-8")
    (dest / "inventory" / paths["api_inventory"].name).write_text(paths["api_inventory"].read_text(encoding="utf-8"), encoding="utf-8")


def main():
    scan = build_scan()
    output_paths = write_outputs(scan)
    write_knowledge_copies(output_paths)
    log_path = Path("pyjhora_knowledge/logs/scan_log.txt")
    failures = scan.defaults.get("module_failures", {})
    total_modules = len(scan.package_tree)
    total_public_functions = sum(
        len([f for f in minfo.functions if f.is_public]) if minfo else 0
        for minfo in scan.package_tree.values()
    )
    total_experimental_flags = sum(
        len(minfo.experimental_flags) if minfo else 0
        for minfo in scan.package_tree.values()
    )
    produced_files = [str(p) for p in output_paths.values()]
    log_lines = [
        f"Scan mode: {scan.defaults.get('scan_mode', 'import-based')}",
        f"Modules failed to import ({len(failures)}):",
    ]
    for name, reason in failures.items():
        log_lines.append(f"- {name}: {reason}")
    log_lines.extend(
        [
            f"Total modules: {total_modules}",
            f"Total public functions: {total_public_functions}",
            f"Total experimental flags: {total_experimental_flags}",
            "Files produced:",
        ]
    )
    log_lines.extend(f"- {p}" for p in produced_files)
    log_path.parent.mkdir(exist_ok=True, parents=True)
    log_path.write_text("\n".join(log_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
