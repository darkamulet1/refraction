from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Dict, Optional


@dataclass
class FunctionInfo:
    name: str
    module: str
    signature: str
    docstring: Optional[str]
    is_public: bool
    experimental: bool = False


@dataclass
class ModuleInfo:
    name: str
    path: Optional[Path]
    docstring: Optional[str]
    functions: List[FunctionInfo] = field(default_factory=list)
    experimental_flags: List[str] = field(default_factory=list)


@dataclass
class CorePrimitives:
    planets: List[Dict[str, Any]] = field(default_factory=list)
    rasis: List[Dict[str, Any]] = field(default_factory=list)
    vargas: List[Dict[str, Any]] = field(default_factory=list)
    ayanamsa: List[Dict[str, Any]] = field(default_factory=list)
    house_systems: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TestCaseInfo:
    file: str
    test_name: str
    description: Optional[str] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    expected: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScanResult:
    version: Optional[str] = None
    root_package: str = "jhora"
    package_tree: Dict[str, ModuleInfo] = field(default_factory=dict)
    core_primitives: CorePrimitives = field(default_factory=CorePrimitives)
    dasha_modules: Dict[str, ModuleInfo] = field(default_factory=dict)
    transit_modules: Dict[str, ModuleInfo] = field(default_factory=dict)
    match_modules: Dict[str, ModuleInfo] = field(default_factory=dict)
    prediction_modules: Dict[str, ModuleInfo] = field(default_factory=dict)
    data_files: List[Dict[str, Any]] = field(default_factory=list)
    tests: List[TestCaseInfo] = field(default_factory=list)
    experimental_modules: List[str] = field(default_factory=list)
    safe_entry_points: List[str] = field(default_factory=list)
    defaults: Dict[str, Any] = field(default_factory=dict)
