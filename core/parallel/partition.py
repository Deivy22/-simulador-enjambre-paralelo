"""Particionamiento determinista en chunks y detección dinámica de núcleos CPU."""

from __future__ import annotations

import os

from data.config import clamp_worker_count, default_worker_count
from data.types import ChunkRange


def detect_cpu_cores() -> int:
    """Detecta dinámicamente los núcleos lógicos disponibles (mínimo 1)."""
    detected = os.cpu_count()
    return detected if detected is not None and detected > 0 else 1


def recommended_worker_count(cpu_count: int | None = None) -> int:
    """Retorna la cantidad recomendada de workers: max(1, cpu_count - 1)."""
    total = detect_cpu_cores() if cpu_count is None else max(1, cpu_count)
    return default_worker_count(total)


def normalize_worker_count(workers: int, cpu_count: int | None = None) -> int:
    """Acota la cantidad de workers solicitada al rango válido [1, cpu_count]."""
    total = detect_cpu_cores() if cpu_count is None else max(1, cpu_count)
    return clamp_worker_count(workers, cpu_count=total)


def compute_chunk_ranges(
    total_items: int,
    workers: int,
    chunks_per_worker: int = 1,
) -> tuple[ChunkRange, ...]:
    """Divide [0, total_items) en segmentos balanceados sin solapamientos ni pérdidas."""
    if total_items < 0:
        raise ValueError("total_items no puede ser negativo.")
    if workers <= 0:
        raise ValueError("workers debe ser mayor que cero.")
    if chunks_per_worker <= 0:
        raise ValueError("chunks_per_worker debe ser mayor que cero.")
    if total_items == 0:
        return ()

    chunk_count = min(total_items, workers * chunks_per_worker)
    base_size, remainder = divmod(total_items, chunk_count)

    return tuple(
        (
            idx * base_size + (idx if idx < remainder else remainder),
            (idx + 1) * base_size + ((idx + 1) if (idx + 1) < remainder else remainder),
        )
        for idx in range(chunk_count)
    )


def verify_chunk_partition(ranges: tuple[ChunkRange, ...], total_items: int) -> bool:
    """Comprueba puramente que los chunks cubran exactamente [0, total_items)."""
    if total_items == 0:
        return ranges == ()
    if not ranges:
        return False
    if ranges[0][0] != 0 or ranges[-1][1] != total_items:
        return False
    return all(
        start < end and (idx == 0 or ranges[idx - 1][1] == start)
        for idx, (start, end) in enumerate(ranges)
    )
