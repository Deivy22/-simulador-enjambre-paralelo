"""Geometría rápida para renderizar boids sin trigonometría."""

from __future__ import annotations

import math

from data.entities import Boid


def compute_boid_chevron_points(
    boid: Boid,
    length: float = 7.5,
    half_width: float = 3.2,
) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    """Calcula los vértices del boid desde su vector de velocidad, sin coseno ni seno."""
    vx = boid.vx
    vy = boid.vy
    speed_sq = vx * vx + vy * vy
    if speed_sq > 1e-8:
        inv_speed = 1.0 / math.sqrt(speed_sq)
        ux = vx * inv_speed
        uy = vy * inv_speed
    else:
        ux = 1.0
        uy = 0.0

    px = -uy * half_width
    py = ux * half_width
    bx = boid.x
    by = boid.y
    tip_x = bx + ux * length
    tip_y = by + uy * length
    tail_x = bx - ux * (length * 0.55)
    tail_y = by - uy * (length * 0.55)

    return (
        (tip_x, tip_y),
        (tail_x + px, tail_y + py),
        (tail_x - px, tail_y - py),
    )
