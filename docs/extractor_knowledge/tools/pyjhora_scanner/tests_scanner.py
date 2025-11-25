from pathlib import Path
import ast
from .model import TestCaseInfo
from typing import List


def scan_tests(tests_root: Path) -> List[TestCaseInfo]:
    results = []
    if not tests_root.exists():
        return results
    for py in tests_root.rglob("*.py"):
        try:
            src = py.read_text(encoding="utf-8")
            tree = ast.parse(src)
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    # try to get a leading comment description
                    desc = None
                    # look for a preceding Expr string as docstring in function
                    if ast.get_docstring(node):
                        desc = ast.get_docstring(node)
                    results.append(TestCaseInfo(file=str(py), test_name=node.name, description=desc))
        except Exception:
            continue
    return results
