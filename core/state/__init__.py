"""Subpaquete de gestión pura de estado y cálculo de métricas."""

from core.state.transitions import create_initial_state, spawn_boids

__all__: tuple[str, ...] = ("create_initial_state", "spawn_boids")
