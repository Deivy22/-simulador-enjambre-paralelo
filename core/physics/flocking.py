"""Reglas físicas puras del enjambre."""

from __future__ import annotations

from data.config import SimConfig
from data.entities import Boid
from data.types import Vec2
from core.math_utils import ZERO_VEC


def compute_separation(
    boid: Boid,
    neighbors: tuple[Boid, ...],
    config: SimConfig,
) -> Vec2:
    """Calcula la fuerza pura de Separación con piso ε y reescalado r_sep²."""
    sep_r = config.separation_radius
    sep_r_sq = sep_r * sep_r
    eps_sq = config.separation_epsilon * config.separation_epsilon
    bx = boid.x
    by = boid.y

    contributions = tuple(
        (
            (bx - other.x) * (sep_r_sq / max((bx - other.x) ** 2 + (by - other.y) ** 2, eps_sq)),
            (by - other.y) * (sep_r_sq / max((bx - other.x) ** 2 + (by - other.y) ** 2, eps_sq)),
        )
        for other in neighbors
        if other is not boid
        and ((bx - other.x) ** 2 + (by - other.y) ** 2) < sep_r_sq
    )
    if not contributions:
        return ZERO_VEC
    return (
        sum(fx for fx, _ in contributions),
        sum(fy for _, fy in contributions),
    )


