"""Grilla Espacial Inmutable O(N·k) compartida por los motores secuencial y paralelo."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import groupby
import math
from operator import itemgetter

from data.entities import Boid
from data.types import SpatialGrid


@dataclass(frozen=True, slots=True)
class SpatialGridIndex:
    """Índice espacial congelado con celdas de índices de boids (tuple[tuple[int, ...], ...])."""

    cols: int
    rows: int
    cell_size: float
    cells: SpatialGrid


def grid_dimensions(world_width: int, world_height: int, cell_size: float) -> tuple[int, int]:
    """Calcula la cantidad de columnas y filas necesarias para cubrir el Canvas."""
    if cell_size <= 0.0:
        raise ValueError("cell_size debe ser mayor que cero.")
    cols = max(1, math.ceil(world_width / cell_size))
    rows = max(1, math.ceil(world_height / cell_size))
    return (cols, rows)


def cell_coords(
    x: float,
    y: float,
    cell_size: float,
    cols: int,
    rows: int,
) -> tuple[int, int]:
    """Mapea una coordenada (x, y) a su celda válida (cx, cy) dentro de la grilla."""
    cx = int(x // cell_size)
    cy = int(y // cell_size)
    clamped_cx = 0 if cx < 0 else (cols - 1 if cx >= cols else cx)
    clamped_cy = 0 if cy < 0 else (rows - 1 if cy >= rows else cy)
    return (clamped_cx, clamped_cy)


def _cell_id_for_xy(
    x: float,
    y: float,
    inv_cell_size: float,
    cols: int,
    max_col: int,
    max_row: int,
) -> int:
    """Calcula el índice plano de celda (cy * cols + cx) en una sola operación."""
    cx = int(x * inv_cell_size)
    cy = int(y * inv_cell_size)
    if cx < 0:
        cx = 0
    elif cx > max_col:
        cx = max_col
    if cy < 0:
        cy = 0
    elif cy > max_row:
        cy = max_row
    return cy * cols + cx


def build_spatial_grid_from_coords(
    xs: Sequence[float] | memoryview,
    ys: Sequence[float] | memoryview,
    world_width: int,
    world_height: int,
    cell_size: float,
) -> SpatialGridIndex:
    """Construye declarativamente la Grilla Espacial Inmutable desde coordenadas planas."""
    cols, rows = grid_dimensions(world_width, world_height, cell_size)
    total_cells = cols * rows
    inv_cell_size = 1.0 / cell_size
    max_col = cols - 1
    max_row = rows - 1
    count = len(xs)

    cell_entries = sorted(
        (
            (_cell_id_for_xy(xs[idx], ys[idx], inv_cell_size, cols, max_col, max_row), idx)
            for idx in range(count)
        ),
        key=itemgetter(0),
    )

    grouped = {
        cell_id: tuple(idx for _, idx in group)
        for cell_id, group in groupby(cell_entries, key=itemgetter(0))
    }
    cells: SpatialGrid = tuple(grouped.get(cid, ()) for cid in range(total_cells))
    return SpatialGridIndex(cols=cols, rows=rows, cell_size=cell_size, cells=cells)


def build_spatial_grid(
    boids: tuple[Boid, ...],
    world_width: int,
    world_height: int,
    cell_size: float,
) -> SpatialGridIndex:
    """Construye declarativamente la Grilla Espacial Inmutable en una sola pasada."""
    cols, rows = grid_dimensions(world_width, world_height, cell_size)
    total_cells = cols * rows
    inv_cell_size = 1.0 / cell_size
    max_col = cols - 1
    max_row = rows - 1

    cell_entries = sorted(
        (
            (_cell_id_for_xy(boid.x, boid.y, inv_cell_size, cols, max_col, max_row), idx)
            for idx, boid in enumerate(boids)
        ),
        key=itemgetter(0),
    )

    grouped = {
        cell_id: tuple(idx for _, idx in group)
        for cell_id, group in groupby(cell_entries, key=itemgetter(0))
    }
    cells: SpatialGrid = tuple(grouped.get(cid, ()) for cid in range(total_cells))
    return SpatialGridIndex(cols=cols, rows=rows, cell_size=cell_size, cells=cells)


def query_neighbor_indices(
    grid: SpatialGridIndex,
    x: float,
    y: float,
    exclude_index: int = -1,
) -> tuple[int, ...]:
    """Retorna los índices de boids en la vecindad 3×3 de (x, y), excluyendo exclude_index."""
    cx, cy = cell_coords(x, y, grid.cell_size, grid.cols, grid.rows)
    min_cx = 0 if cx == 0 else cx - 1
    max_cx = grid.cols - 1 if cx >= grid.cols - 1 else cx + 1
    min_cy = 0 if cy == 0 else cy - 1
    max_cy = grid.rows - 1 if cy >= grid.rows - 1 else cy + 1

    cols = grid.cols
    cells = grid.cells
    return tuple(
        idx
        for gy in range(min_cy, max_cy + 1)
        for gx in range(min_cx, max_cx + 1)
        for idx in cells[gy * cols + gx]
        if idx != exclude_index
    )


def query_neighbors(
    boids: tuple[Boid, ...],
    grid: SpatialGridIndex,
    boid_index: int,
) -> tuple[Boid, ...]:
    """Obtiene la tupla inmutable de vecinos candidatos 3×3 para un boid dado."""
    target = boids[boid_index]
    indices = query_neighbor_indices(grid, target.x, target.y, exclude_index=boid_index)
    return tuple(boids[idx] for idx in indices)
