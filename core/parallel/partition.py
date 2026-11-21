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


