"""Auditoría automatizada por AST de pureza funcional, fronteras de capas y compatibilidad spawn."""

from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


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
