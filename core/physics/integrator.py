"""Integrador puro de fuerzas ponderadas hacia un nuevo Boid congelado."""

from __future__ import annotations

from core.math_utils import clamp_speed
from core.physics.environment import (
    clamp_position_and_velocity,
    compute_boundary_force,
    compute_mouse_force,
)
from core.physics.flocking import compute_flocking_forces
from data.config import SimConfig
from data.entities import Boid
from data.input_state import InputState


def integrate_boid(
    boid: Boid,
    neighbors: tuple[Boid, ...],
    input_state: InputState,
    config: SimConfig,
    dt: float,
) -> Boid:
    """Calcula la nueva posición y velocidad de un Boid sin mutar el original."""
    sep, ali, coh = compute_flocking_forces(boid, neighbors, config)
    mouse_f = compute_mouse_force(boid, input_state, config)
    border_f = compute_boundary_force(boid, config)

    total_fx = (
        sep[0] * config.weight_separation
        + ali[0] * config.weight_alignment
        + coh[0] * config.weight_cohesion
        + mouse_f[0] * config.weight_mouse
        + border_f[0]
    )
    total_fy = (
        sep[1] * config.weight_separation
        + ali[1] * config.weight_alignment
        + coh[1] * config.weight_cohesion
        + mouse_f[1] * config.weight_mouse
        + border_f[1]
    )

    raw_vel = (boid.vx + total_fx * dt, boid.vy + total_fy * dt)
    clamped_vel = clamp_speed(
        velocity=raw_vel,
        min_speed=config.min_speed,
        max_speed=config.max_speed,
        fallback_dir=(boid.vx, boid.vy),
    )

    raw_pos = (boid.x + clamped_vel[0] * dt, boid.y + clamped_vel[1] * dt)
    final_pos, final_vel = clamp_position_and_velocity(raw_pos, clamped_vel, config)

    return Boid(
        x=final_pos[0],
        y=final_pos[1],
        vx=final_vel[0],
        vy=final_vel[1],
    )
