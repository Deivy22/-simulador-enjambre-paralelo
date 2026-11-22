"""Orquestación del motor paralelo (Segmentación -> Pool.map -> Consolidación inmutable)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from multiprocessing.pool import Pool

from core.engine.spatial_grid import build_spatial_grid_from_coords
from core.parallel.ipc_codec import buffer_as_readonly_views, pack_boids_to_buffer
from core.parallel.partition import compute_chunk_ranges
from core.parallel.worker import WorkerTask, process_boid_chunk
from core.state.transitions import apply_input_transitions
from data.config import SimConfig
from data.entities import Boid
from data.game_state import GameState
from data.input_state import InputState
from data.types import FlatBoidTuple, ScreenMode


def build_worker_tasks(
    boids: tuple[Boid, ...],
    input_state: InputState,
    config: SimConfig,
    dt: float,
    workers: int,
    chunks_per_worker: int = 1,
) -> tuple[WorkerTask, ...]:
    """Fase 1: empaqueta buffer binario compacto, construye Grilla Espacial y segmenta chunks."""
    if not boids:
        return ()

    packed_buffer = pack_boids_to_buffer(boids)
    xs_view, ys_view, _, _ = buffer_as_readonly_views(packed_buffer)
    grid = build_spatial_grid_from_coords(
        xs=xs_view,
        ys=ys_view,
        world_width=config.world_width,
        world_height=config.world_height,
        cell_size=config.perception_radius,
    )
    ranges = compute_chunk_ranges(
        total_items=len(boids),
        workers=workers,
        chunks_per_worker=chunks_per_worker,
    )
    return tuple(
        WorkerTask(
            chunk_range=chunk_range,
            buffer=packed_buffer,
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
    """Fase 3: consolida en orden exacto todos los segmentos en una tupla inmutable de Boid."""
    return tuple(
        Boid(x=x, y=y, vx=vx, vy=vy)
        for segment in chunk_results
        for x, y, vx, vy in segment
    )


def step_boids_parallel(
    boids: tuple[Boid, ...],
    input_state: InputState,
    config: SimConfig,
    dt: float,
    pool: Pool,
    workers: int,
    chunks_per_worker: int = 1,
) -> tuple[Boid, ...]:
    """Ejecuta el pipeline paralelo de 3 fases con barrera de sincronización en Pool.map."""
    if not boids:
        return ()

    tasks = build_worker_tasks(
        boids=boids,
        input_state=input_state,
        config=config,
        dt=dt,
        workers=workers,
        chunks_per_worker=chunks_per_worker,
    )
    # Fase 2: Mapeo paralelo y barrera de sincronización obligatoria
    chunk_results = pool.map(process_boid_chunk, tasks)
    # Fase 3: Consolidación ordenada e inmutable
    return consolidate_chunk_results(chunk_results)


def update_parallel(
    state: GameState,
    input_state: InputState,
    dt: float,
    pool: Pool,
    chunks_per_worker: int = 1,
) -> GameState:
    """Función pura de actualización por frame en Modo Paralelo (N workers)."""
    transitioned = apply_input_transitions(state, input_state)
    if transitioned.screen is not ScreenMode.SIMULATION or transitioned.paused:
        return transitioned

    next_boids = step_boids_parallel(
        boids=transitioned.boids,
        input_state=input_state,
        config=transitioned.config,
        dt=dt,
        pool=pool,
        workers=transitioned.workers,
        chunks_per_worker=chunks_per_worker,
    )
    return replace(
        transitioned,
        boids=next_boids,
        frame=transitioned.frame + 1,
        input_state=input_state,
    )
