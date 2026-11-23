"""Empaquetado ligero e inmutable de Boids para IPC (tuplas planas y buffers binarios)."""

from __future__ import annotations

from array import array
from collections.abc import Sequence
from dataclasses import dataclass

from data.entities import Boid, FlatBoidSnapshot
from data.types import FlatBoidTuple


@dataclass(frozen=True, slots=True)
class PackedBoidBuffer:
    """Buffer binario 100% inmutable (bytes IEEE-754) para serialización IPC ultra-rápida."""

    xs_bytes: bytes
    ys_bytes: bytes
    vxs_bytes: bytes
    vys_bytes: bytes
    count: int


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


def pack_boids_to_buffer(boids: tuple[Boid, ...]) -> PackedBoidBuffer:
    """Empaqueta Boids en 4 bloques inmutables de flotantes C contiguos (bytes)."""
    return PackedBoidBuffer(
        xs_bytes=array("d", (b.x for b in boids)).tobytes(),
        ys_bytes=array("d", (b.y for b in boids)).tobytes(),
        vxs_bytes=array("d", (b.vx for b in boids)).tobytes(),
        vys_bytes=array("d", (b.vy for b in boids)).tobytes(),
        count=len(boids),
    )


def buffer_as_readonly_views(
    buf: PackedBoidBuffer,
) -> tuple[memoryview, memoryview, memoryview, memoryview]:
    """Expone vistas float64 de solo lectura sin copias (zero-copy) sobre PackedBoidBuffer."""
    return (
        memoryview(buf.xs_bytes).cast("d"),
        memoryview(buf.ys_bytes).cast("d"),
        memoryview(buf.vxs_bytes).cast("d"),
        memoryview(buf.vys_bytes).cast("d"),
    )


def buffer_as_readonly_tuples(
    buf: PackedBoidBuffer,
) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[float, ...]]:
    """Materializa una sola vez por chunk 4 tuplas inmutables para indexación C sin asignaciones."""
    xs_v, ys_v, vxs_v, vys_v = buffer_as_readonly_views(buf)
    return (tuple(xs_v), tuple(ys_v), tuple(vxs_v), tuple(vys_v))


def unpack_buffer_to_boids(buf: PackedBoidBuffer) -> tuple[Boid, ...]:
    """Reconstruye una tupla inmutable de Boids desde un PackedBoidBuffer."""
    xs, ys, vxs, vys = buffer_as_readonly_views(buf)
    return tuple(
        Boid(x=xs[i], y=ys[i], vx=vxs[i], vy=vys[i])
        for i in range(buf.count)
    )
