"""Construcción de tareas inmutables del motor paralelo."""

from __future__ import annotations

from collections.abc import Sequence

from core.engine.spatial_grid import build_spatial_grid
from core.parallel.ipc_codec import pack_boids_to_snapshot
from core.parallel.partition import compute_chunk_ranges
from core.parallel.worker import WorkerTask
from data.config import SimConfig
from data.entities import Boid
from data.input_state import InputState
from data.types import FlatBoidTuple


def build_worker_tasks(
    boids: tuple[Boid, ...],
    input_state: InputState,
    config: SimConfig,
    dt: float,
    workers: int,
    chunks_per_worker: int = 1,
) -> tuple[WorkerTask, ...]:
    """Fase 1: construye la grilla espacial, empaqueta el snapshot y segmenta chunks."""
    if not boids:
        return ()

    grid = build_spatial_grid(
        boids=boids,
        world_width=config.world_width,
        world_height=config.world_height,
        cell_size=config.perception_radius,
    )
    snapshot = pack_boids_to_snapshot(boids)
    ranges = compute_chunk_ranges(
        total_items=len(boids),
        workers=workers,
        chunks_per_worker=chunks_per_worker,
    )
    return tuple(
        WorkerTask(
            chunk_range=chunk_range,
            snapshot=snapshot,
            grid=grid,
            input_state=input_state,
            config=config,
            dt=dt,
        )
        for chunk_range in ranges
    )


def consolidate_chunk_results(
    chunk_results: Sequence[tuple[FlatBoidTuple, ...]],
) -> tuple[Boid, ...]:
    """Consolida en orden exacto los segmentos en una tupla inmutable de Boid."""
    return tuple(
        Boid(x=x, y=y, vx=vx, vy=vy)
        for segment in chunk_results
        for x, y, vx, vy in segment
    )
