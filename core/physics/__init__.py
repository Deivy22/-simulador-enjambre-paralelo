"""Subpaquete de reglas físicas puras del modelo Boids."""

from core.physics.environment import (
    clamp_position_and_velocity,
    compute_boundary_force,
    compute_mouse_force,
)
from core.physics.flocking import (
    compute_alignment,
    compute_cohesion,
    compute_flocking_forces,
    compute_separation,
)
from core.physics.integrator import integrate_boid, integrate_boid_from_flat

__all__: tuple[str, ...] = (
    "clamp_position_and_velocity",
    "compute_alignment",
    "compute_boundary_force",
    "compute_cohesion",
    "compute_flocking_forces",
    "compute_mouse_force",
    "compute_separation",
    "integrate_boid",
    "integrate_boid_from_flat",
)
