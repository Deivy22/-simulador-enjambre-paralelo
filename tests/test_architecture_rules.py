"""Auditoría automatizada por AST de pureza funcional, fronteras de capas y compatibilidad spawn."""

from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_PACKAGES: tuple[str, ...] = ("data", "core", "ui", "benchmarks")


def _iter_python_files(relative_dir: str) -> tuple[Path, ...]:
    """Retorna todos los archivos .py dentro de una carpeta del proyecto."""
    target = PROJECT_ROOT / relative_dir
    if not target.exists():
        return ()
    return tuple(sorted(target.rglob("*.py")))


def _parse_module(path: Path) -> ast.Module:
    """Parsea un archivo fuente Python en su árbol sintáctico AST."""
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _imported_roots(tree: ast.Module) -> tuple[str, ...]:
    """Extrae los nombres raíz de todos los módulos importados en un archivo."""
    roots: tuple[str, ...] = ()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots = roots + tuple(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            roots = roots + (node.module.split(".")[0],)
    return roots


def _is_frozen_dataclass_or_enum(cls_node: ast.ClassDef) -> bool:
    """Verifica que una clase sea Enum o esté decorada con @dataclass(frozen=True, ...)."""
    for base in cls_node.bases:
        if isinstance(base, ast.Name) and base.id == "Enum":
            return True
        if isinstance(base, ast.Attribute) and base.attr == "Enum":
            return True

    for dec in cls_node.decorator_list:
        if isinstance(dec, ast.Call):
            func_name = (
                dec.func.id
                if isinstance(dec.func, ast.Name)
                else (dec.func.attr if isinstance(dec.func, ast.Attribute) else "")
            )
            if func_name == "dataclass":
                has_frozen_true = any(
                    kw.arg == "frozen"
                    and isinstance(kw.value, ast.Constant)
                    and kw.value.value is True
                    for kw in dec.keywords
                )
                if has_frozen_true:
                    return True
    return False


def _is_mutable_literal_or_ctor(expr: ast.expr | None) -> bool:
    """Detecta literales o constructores de colecciones mutables (list, dict, set)."""
    if expr is None:
        return False
    if isinstance(expr, (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp)):
        return True
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name):
        return expr.func.id in ("list", "dict", "set", "bytearray")
    return False


def test_no_pygame_or_ui_imports_in_data_core_and_benchmarks() -> None:
    forbidden = {"pygame", "ui"}
    for pkg in ("data", "core", "benchmarks"):
        for path in _iter_python_files(pkg):
            imports = set(_imported_roots(_parse_module(path)))
            overlap = imports & forbidden
            assert not overlap, f"Import prohibido {overlap} en {path.relative_to(PROJECT_ROOT)}"


def test_data_layer_has_zero_internal_dependencies() -> None:
    forbidden = {"core", "ui", "pygame", "benchmarks"}
    for path in _iter_python_files("data"):
        imports = set(_imported_roots(_parse_module(path)))
        overlap = imports & forbidden
        assert not overlap, f"Capa data/ importa {overlap} en {path.relative_to(PROJECT_ROOT)}"


def test_no_mutable_classes_or_self_mutations_across_application() -> None:
    all_files = tuple(
        path
        for pkg in APP_PACKAGES
        for path in _iter_python_files(pkg)
    ) + (PROJECT_ROOT / "main.py",)

    for path in all_files:
        tree = _parse_module(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                assert _is_frozen_dataclass_or_enum(node), (
                    f"Clase no congelada '{node.name}' en {path.relative_to(PROJECT_ROOT)}"
                )
                for sub in ast.walk(node):
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        pytest_msg = (
                            f"Método '{sub.name}' encontrado en clase '{node.name}' "
                            f"({path.relative_to(PROJECT_ROOT)}); prohibido POO mutable."
                        )
                        raise AssertionError(pytest_msg)


def test_no_mutable_global_variables_at_module_level() -> None:
    all_files = tuple(
        path
        for pkg in APP_PACKAGES
        for path in _iter_python_files(pkg)
    ) + (PROJECT_ROOT / "main.py",)

    for path in all_files:
        tree = _parse_module(path)
        for stmt in tree.body:
            if isinstance(stmt, ast.Assign):
                assert not _is_mutable_literal_or_ctor(stmt.value), (
                    f"Variable global mutable en {path.relative_to(PROJECT_ROOT)}:{stmt.lineno}"
                )
            elif isinstance(stmt, ast.AnnAssign):
                assert not _is_mutable_literal_or_ctor(stmt.value), (
                    f"Variable global mutable anotada en {path.relative_to(PROJECT_ROOT)}:{stmt.lineno}"
                )
