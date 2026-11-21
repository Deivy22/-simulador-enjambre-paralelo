"""Funciones worker puras de nivel superior (picklables en Windows spawn)."""

from __future__ import annotations

from dataclasses import dataclass

from core.engine.spatial_grid import SpatialGridIndex, query_neighbor_indices
from core.physics.integrator import integrate_boid
from data.config import SimConfig
from data.entities import Boid, FlatBoidSnapshot
from data.input_state import InputState
from data.types import ChunkRange, FlatBoidTuple


@dataclass(frozen=True, slots=True)
class WorkerTask:
    """Carga inmutable enviada a un worker para procesar un segmento [start, end)."""

    chunk_range: ChunkRange
    snapshot: FlatBoidSnapshot
    grid: SpatialGridIndex
    input_state: InputState
    config: SimConfig
    dt: float


def _evaluate_boid_at_index(
    idx: int,
    snapshot: FlatBoidSnapshot,
    grid: SpatialGridIndex,
    input_state: InputState,
    config: SimConfig,
    dt: float,
) -> FlatBoidTuple:
    """Evalúa puramente el boid `idx` leyendo solo sus vecinos 3×3 del snapshot."""
    xs = snapshot.xs
    ys = snapshot.ys
    vxs = snapshot.vxs
    vys = snapshot.vys

    boid = Boid(x=xs[idx], y=ys[idx], vx=vxs[idx], vy=vys[idx])
    neighbor_indices = query_neighbor_indices(grid, boid.x, boid.y, exclude_index=idx)
    neighbors = tuple(
        Boid(x=xs[j], y=ys[j], vx=vxs[j], vy=vys[j])
        for j in neighbor_indices
    )
    updated = integrate_boid(
        boid=boid,
        neighbors=neighbors,
        input_state=input_state,
        config=config,
        dt=dt,
    )
    return (updated.x, updated.y, updated.vx, updated.vy)


def process_boid_chunk(task: WorkerTask) -> tuple[FlatBoidTuple, ...]:
    """Función worker pura de nivel superior: actualiza su segmento sin efectos secundarios."""
    start, end = task.chunk_range
    return tuple(
        _evaluate_boid_at_index(
            idx=idx,
            snapshot=task.snapshot,
            grid=task.grid,
            input_state=task.input_state,
            config=task.config,
            dt=task.dt,
        )
        for idx in range(start, end)
    )
