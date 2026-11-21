"""Motor físico secuencial (1 núcleo) basado en transformaciones declarativas."""

from __future__ import annotations

from dataclasses import replace

from core.engine.spatial_grid import build_spatial_grid, query_neighbors
from core.physics.integrator import integrate_boid
from core.state.transitions import apply_input_transitions
from data.config import SimConfig
from data.entities import Boid
from data.game_state import GameState
from data.input_state import InputState
from data.types import ScreenMode


def step_boids_sequential(
    boids: tuple[Boid, ...],
    input_state: InputState,
    config: SimConfig,
    dt: float,
) -> tuple[Boid, ...]:
    """Avanza un paso físico puro sobre todos los boids usando Grilla Espacial Inmutable."""
    if not boids:
        return ()

    grid = build_spatial_grid(
        boids=boids,
        world_width=config.world_width,
        world_height=config.world_height,
        cell_size=config.perception_radius,
    )
    return tuple(
        integrate_boid(
            boid=boid,
            neighbors=query_neighbors(boids, grid, idx),
            input_state=input_state,
            config=config,
            dt=dt,
        )
        for idx, boid in enumerate(boids)
    )


def update_sequential(
    state: GameState,
    input_state: InputState,
    dt: float,
) -> GameState:
    """Función pura de actualización por frame en Modo Secuencial (1 núcleo)."""
    transitioned = apply_input_transitions(state, input_state)
    if transitioned.screen is not ScreenMode.SIMULATION or transitioned.paused:
        return transitioned

    next_boids = step_boids_sequential(
        boids=transitioned.boids,
        input_state=input_state,
        config=transitioned.config,
        dt=dt,
    )
    return replace(
        transitioned,
        boids=next_boids,
        frame=transitioned.frame + 1,
        input_state=input_state,
    )
