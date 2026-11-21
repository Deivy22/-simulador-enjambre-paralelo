"""Subpaquete de gestión pura de estado y cálculo de métricas."""

from core.state.transitions import (
    apply_input_transitions,
    apply_simulation_input,
    apply_start_screen_input,
    create_initial_state,
    spawn_boids,
)

__all__: tuple[str, ...] = (
    "apply_input_transitions",
    "apply_simulation_input",
    "apply_start_screen_input",
    "create_initial_state",
    "spawn_boids",
)
