from pathlib import Path
import sys
from .fs_utils import find_package_root
from .model import ScanResult, ModuleInfo, FunctionInfo
from .generate_markdown import generate_markdown
from .generate_summary import write_summary
from .api_inventory import generate_api_inventory
from .tests_scanner import scan_tests
from .experimental_scanner import scan_file_for_experimental
import ast


def sig_from_ast(fn: ast.FunctionDef) -> str:
    parts = []
    args = fn.args
    def arg_name(a):
        return a.arg
    # positional args
    names = [arg_name(a) for a in args.args]
    defaults = [None] * (len(names) - len(args.defaults)) + args.defaults
    sig_parts = []
    for n, d in zip(names, defaults):
        if d is not None:
            try:
                val = ast.unparse(d)
            except Exception:
                val = '...'
            sig_parts.append(f"{n}={val}")
        else:
            sig_parts.append(n)
    if args.vararg:
        sig_parts.append(f"*{args.vararg.arg}")
    if args.kwarg:
        sig_parts.append(f"**{args.kwarg.arg}")
    return "(" + ", ".join(sig_parts) + ")"


def scan_ast_package(start: Path) -> ScanResult:
    repo_root = find_package_root(start, "jhora")
    jhora_root = repo_root / "jhora"
    scan = ScanResult()
    scan.version = "UNKNOWN"
    scan.root_package = "jhora"

    for py in jhora_root.rglob("*.py"):
        rel = py.relative_to(repo_root)
        modname = str(rel).replace("\\", "/").replace('/', '.')[:-3]  # remove .py
        # module name like jhora.panchanga.drik
        if modname.endswith(".__init__"):
            modname = modname.rsplit('.', 1)[0]
        try:
            src = py.read_text(encoding='utf-8')
            tree = ast.parse(src)
            doc = ast.get_docstring(tree)
            m = ModuleInfo(name=modname, path=py, docstring=doc)
            # scan functions
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    name = node.name
                    signature = sig_from_ast(node)
                    docf = ast.get_docstring(node)
                    is_public = not name.startswith('_')
                    f = FunctionInfo(name=name, module=modname, signature=signature, docstring=docf, is_public=is_public)
                    m.functions.append(f)
                    # detect experimental markers in doc
                    if docf:
                        ud = docf.upper()
                        for marker in ("EXPERIMENTAL","NOT FULLY IMPLEMENTED","UNDER TESTING","TODO"):
                            if marker in ud and marker not in m.experimental_flags:
                                m.experimental_flags.append(marker)
            # module-level experimental scan
            upper = src.upper()
            for marker in ("EXPERIMENTAL","NOT FULLY IMPLEMENTED","UNDER TESTING","TODO"):
                if marker in upper and marker not in m.experimental_flags:
                    m.experimental_flags.append(marker)
            scan.package_tree[modname] = m
            if m.experimental_flags:
                scan.experimental_modules.append(modname)
        except Exception:
            continue

    # const parsing
    try:
        from .const_parser import parse_const
        cp, defaults = parse_const(repo_root)
        scan.core_primitives = cp
        scan.defaults.update(defaults)
    except Exception:
        pass

    # tests
    tests_root = jhora_root / 'tests'
    scan.tests = scan_tests(tests_root)

    # data files
    data_dir = jhora_root / 'data'
    if data_dir.exists():
        for f in data_dir.rglob('*'):
            if f.is_file():
                scan.data_files.append({'path': str(f.relative_to(repo_root)), 'purpose': '', 'consumers': []})

    # heuristics for safe entry points
    for modname, m in scan.package_tree.items():
        if not m:
            continue
        if modname.endswith('panchanga.drik') or modname.endswith('chart.charts') or modname.endswith('chart.strength'):
            for f in m.functions:
                if f.is_public and modname not in scan.experimental_modules:
                    scan.safe_entry_points.append(f"{modname}.{f.name}")

    # unique lists
    scan.safe_entry_points = sorted(set(scan.safe_entry_points))
    scan.experimental_modules = sorted(set(scan.experimental_modules))

    # generate outputs
    md = generate_markdown(scan)
    md_path = repo_root / 'PyJHora_Structural_Map.md'
    md_path.write_text(md, encoding='utf-8')
    summary_path = repo_root / 'PyJHora_Structural_Map_summary.json'
    write_summary(scan, summary_path)
    # generate API inventory as well
    try:
        api_inventory = generate_api_inventory(scan)
        import json

        api_path = repo_root / 'PyJHora_API_Inventory.json'
        api_path.write_text(json.dumps(api_inventory, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"Wrote: {md_path}")
        print(f"Wrote: {summary_path}")
        print(f"Wrote: {api_path}")
    except Exception as e:
        print(f"Wrote: {md_path}")
        print(f"Wrote: {summary_path}")
        print(f"Failed to write API inventory: {e}")


if __name__ == '__main__':
    start = Path.cwd()
    scan_ast_package(start)
