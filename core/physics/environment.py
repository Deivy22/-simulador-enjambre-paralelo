"""Fuerza ambiental pura de límites suaves para el Canvas."""

from __future__ import annotations

from core.math_utils import ZERO_VEC, clamp_scalar
from data.config import SimConfig
from data.entities import Boid
from data.types import Vec2


def compute_boundary_force(boid: Boid, config: SimConfig) -> Vec2:
    """Calcula la fuerza progresiva de margen suave dentro de world_width × world_height."""
    margin = config.margin
    if margin <= 0.0:
        return ZERO_VEC

    turn = config.turn_factor
    inv_margin = 1.0 / margin
    right_limit = float(config.world_width) - margin
    bottom_limit = float(config.world_height) - margin

    fx_left = turn * ((margin - boid.x) * inv_margin) if boid.x < margin else 0.0
    fx_right = -turn * ((boid.x - right_limit) * inv_margin) if boid.x > right_limit else 0.0
    fy_top = turn * ((margin - boid.y) * inv_margin) if boid.y < margin else 0.0
    fy_bottom = -turn * ((boid.y - bottom_limit) * inv_margin) if boid.y > bottom_limit else 0.0

    return (fx_left + fx_right, fy_top + fy_bottom)


def clamp_position_and_velocity(
    pos: Vec2,
    vel: Vec2,
    config: SimConfig,
) -> tuple[Vec2, Vec2]:
    """Respaldo hard clamp en [0, world_width] × [0, world_height] sin fugas."""
    max_x = float(config.world_width)
    max_y = float(config.world_height)
    px, py = pos
    vx, vy = vel

    clamped_x = clamp_scalar(px, 0.0, max_x)
    clamped_y = clamp_scalar(py, 0.0, max_y)

    new_vx = abs(vx) if px < 0.0 else (-abs(vx) if px > max_x else vx)
    new_vy = abs(vy) if py < 0.0 else (-abs(vy) if py > max_y else vy)

    return ((clamped_x, clamped_y), (new_vx, new_vy))
