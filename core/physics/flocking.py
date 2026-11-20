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


def compute_alignment(
    boid: Boid,
    neighbors: tuple[Boid, ...],
    config: SimConfig,
) -> Vec2:
    """Calcula la fuerza pura de Alineación respecto a vecinos en perception_radius."""
    perc_r_sq = config.perception_radius * config.perception_radius
    bx = boid.x
    by = boid.y

    in_range = tuple(
        other
        for other in neighbors
        if other is not boid
        and ((bx - other.x) ** 2 + (by - other.y) ** 2) < perc_r_sq
    )
    count = len(in_range)
    if count == 0:
        return ZERO_VEC

    inv_count = 1.0 / count
    avg_vx = sum(other.vx for other in in_range) * inv_count
    avg_vy = sum(other.vy for other in in_range) * inv_count
    return (avg_vx - boid.vx, avg_vy - boid.vy)


def compute_flocking_forces(
    boid: Boid,
    neighbors: tuple[Boid, ...],
    config: SimConfig,
) -> tuple[Vec2, Vec2, Vec2]:
    """Evalúa Separación, Alineación y Cohesión en un único filtrado de vecinos."""
    perc_r_sq = config.perception_radius * config.perception_radius
    bx = boid.x
    by = boid.y

    perceived = tuple(
        other
        for other in neighbors
        if other is not boid
        and ((bx - other.x) ** 2 + (by - other.y) ** 2) < perc_r_sq
    )
    if not perceived:
        return (ZERO_VEC, ZERO_VEC, ZERO_VEC)

    sep_force = compute_separation(boid, perceived, config)
    inv_count = 1.0 / len(perceived)
    ali_force = (
        sum(other.vx for other in perceived) * inv_count - boid.vx,
        sum(other.vy for other in perceived) * inv_count - boid.vy,
    )
    coh_force = (
        sum(other.x for other in perceived) * inv_count - bx,
        sum(other.y for other in perceived) * inv_count - by,
    )
    return (sep_force, ali_force, coh_force)


