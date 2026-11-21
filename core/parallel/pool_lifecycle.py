"""Gestión headless del ciclo de vida del multiprocessing.Pool."""

from __future__ import annotations

from dataclasses import dataclass
import multiprocessing
from multiprocessing.pool import Pool

from core.parallel.partition import normalize_worker_count


@dataclass(frozen=True, slots=True)
class PoolHandle:
    """Referencia congelada a un Pool persistente y su cantidad de workers configurada."""

    pool: Pool | None = None
    workers: int = 1


def create_pool_handle(
    workers: int,
    cpu_count: int | None = None,
) -> PoolHandle:
    """Crea un Pool persistente con cantidad de workers acotada al hardware."""
    resolved = normalize_worker_count(workers, cpu_count=cpu_count)
    pool = multiprocessing.Pool(processes=resolved)
    return PoolHandle(pool=pool, workers=resolved)


def close_pool_handle(
    handle: PoolHandle,
    *,
    terminate_immediately: bool = False,
) -> PoolHandle:
    """Cierra y espera el Pool de forma idempotente para garantizar cero procesos zombis."""
    if handle.pool is None:
        return handle

    try:
        if terminate_immediately:
            handle.pool.terminate()
        else:
            handle.pool.close()
        handle.pool.join()
    except Exception:
        handle.pool.terminate()
        handle.pool.join()

    return PoolHandle(pool=None, workers=handle.workers)
