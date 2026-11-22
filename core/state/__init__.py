"""Subpaquete de gestión pura de estado y cálculo de métricas."""

from core.state.metrics_calc import (
    clamp_interactive_dt,
    compute_instant_fps,
    measure_execution_ms,
    update_metrics_snapshot,
)
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
    "clamp_interactive_dt",
    "compute_instant_fps",
    "create_initial_state",
    "measure_execution_ms",
    "spawn_boids",
    "update_metrics_snapshot",
)
