"""Funciones worker puras de nivel superior (picklables en Windows spawn)."""

from __future__ import annotations

from dataclasses import dataclass

from core.engine.spatial_grid import SpatialGridIndex
from core.parallel.ipc_codec import PackedBoidBuffer, buffer_as_readonly_tuples
from core.physics.integrator import integrate_boid_from_flat
from data.config import SimConfig
from data.input_state import InputState
from data.types import ChunkRange, FlatBoidTuple


@dataclass(frozen=True, slots=True)
class WorkerTask:
    """Carga inmutable enviada a un worker para procesar un segmento [start, end)."""

    chunk_range: ChunkRange
    buffer: PackedBoidBuffer
    grid: SpatialGridIndex
    input_state: InputState
    config: SimConfig
    dt: float


def process_boid_chunk(task: WorkerTask) -> tuple[FlatBoidTuple, ...]:
    """Función worker pura de nivel superior: evalúa su segmento sobre tuplas solo-lectura."""
    start, end = task.chunk_range
    xs, ys, vxs, vys = buffer_as_readonly_tuples(task.buffer)
    grid = task.grid
    cells = grid.cells
    cols = grid.cols
    rows = grid.rows
    inv_cell_size = 1.0 / grid.cell_size
    input_state = task.input_state
    config = task.config
    dt = task.dt

    return tuple(
        integrate_boid_from_flat(
            idx=idx,
            xs=xs,
            ys=ys,
            vxs=vxs,
            vys=vys,
            cells=cells,
            cols=cols,
            rows=rows,
            inv_cell_size=inv_cell_size,
            input_state=input_state,
            config=config,
            dt=dt,
        )
        for idx in range(start, end)
    )
