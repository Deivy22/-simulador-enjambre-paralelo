"""Entidades inmutables del enjambre y representaciones compactas para IPC."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Boid:
    """Representa una entidad inmutable del enjambre en 2D."""

    x: float
    y: float
    vx: float
    vy: float


@dataclass(frozen=True, slots=True)
class FlatBoidSnapshot:
    """Instantánea plana e inmutable de posiciones y velocidades para IPC ligero."""

    xs: tuple[float, ...]
    ys: tuple[float, ...]
    vxs: tuple[float, ...]
    vys: tuple[float, ...]
