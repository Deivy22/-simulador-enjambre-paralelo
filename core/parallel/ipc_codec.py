"""Empaquetado ligero e inmutable de Boids para comunicación entre procesos (IPC)."""

from __future__ import annotations

from collections.abc import Sequence

from data.entities import Boid, FlatBoidSnapshot
from data.types import FlatBoidTuple


def pack_boids_to_flat_tuples(boids: tuple[Boid, ...]) -> tuple[FlatBoidTuple, ...]:
    """Convierte una tupla de Boid en tuplas planas (x, y, vx, vy) ligeras para IPC."""
    return tuple((b.x, b.y, b.vx, b.vy) for b in boids)


def unpack_flat_tuples_to_boids(flat: Sequence[FlatBoidTuple]) -> tuple[Boid, ...]:
    """Reconstruye una tupla inmutable de Boid desde tuplas planas (x, y, vx, vy)."""
    return tuple(Boid(x=x, y=y, vx=vx, vy=vy) for x, y, vx, vy in flat)


def pack_boids_to_snapshot(boids: tuple[Boid, ...]) -> FlatBoidSnapshot:
    """Empaqueta Boids en 4 tuplas planas inmutables (xs, ys, vxs, vys)."""
    if not boids:
        return FlatBoidSnapshot(xs=(), ys=(), vxs=(), vys=())
    return FlatBoidSnapshot(
        xs=tuple(b.x for b in boids),
        ys=tuple(b.y for b in boids),
        vxs=tuple(b.vx for b in boids),
        vys=tuple(b.vy for b in boids),
    )


def unpack_snapshot_to_boids(snapshot: FlatBoidSnapshot) -> tuple[Boid, ...]:
    """Reconstruye la tupla completa de Boids desde un FlatBoidSnapshot congelado."""
    return tuple(
        Boid(x=x, y=y, vx=vx, vy=vy)
        for x, y, vx, vy in zip(snapshot.xs, snapshot.ys, snapshot.vxs, snapshot.vys)
    )
