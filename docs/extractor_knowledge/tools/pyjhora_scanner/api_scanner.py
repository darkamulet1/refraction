import inspect
from types import ModuleType
from .model import ModuleInfo, FunctionInfo
from typing import List

EXPERIMENTAL_MARKERS = ["EXPERIMENTAL", "NOT FULLY IMPLEMENTED", "UNDER TESTING", "TODO"]


def scan_module(mod: ModuleType) -> ModuleInfo:
    name = getattr(mod, "__name__", "<unknown>")
    path = None
    doc = None
    try:
        path = inspect.getsourcefile(mod)
    except Exception:
        path = None
    try:
        doc = inspect.getdoc(mod)
    except Exception:
        doc = None

    m = ModuleInfo(name=name, path=path and __import__('pathlib').Path(path), docstring=doc)

    # collect functions
    try:
        for _, obj in inspect.getmembers(mod, inspect.isfunction):
            try:
                sig = str(inspect.signature(obj))
            except Exception:
                sig = "()"
            docf = inspect.getdoc(obj)
            is_public = not obj.__name__.startswith("_")

            # determine function-level experimental: if any marker appears in function doc or module doc
            function_experimental = False
            if docf:
                for marker in EXPERIMENTAL_MARKERS:
                    if marker in docf.upper():
                        function_experimental = True
                        if marker not in m.experimental_flags:
                            m.experimental_flags.append(marker)
            if doc:
                for marker in EXPERIMENTAL_MARKERS:
                    if marker in doc.upper():
                        function_experimental = True
                        if marker not in m.experimental_flags:
                            m.experimental_flags.append(marker)

            finfo = FunctionInfo(
                name=obj.__name__,
                module=name,
                signature=sig,
                docstring=docf,
                is_public=is_public,
                experimental=function_experimental,
            )
            m.functions.append(finfo)
    except Exception:
        # ignore introspection errors
        pass

    # deduplicate experimental flags
    m.experimental_flags = list(dict.fromkeys(m.experimental_flags))

    return m
