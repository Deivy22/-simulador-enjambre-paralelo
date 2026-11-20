"""Fuerza ambiental pura de límites suaves para el Canvas."""

from __future__ import annotations

from core.math_utils import ZERO_VEC
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
