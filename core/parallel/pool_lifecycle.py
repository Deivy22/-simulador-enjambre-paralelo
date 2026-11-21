"""Gestión headless del ciclo de vida del multiprocessing.Pool."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
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


def ensure_pool_workers(
    handle: PoolHandle,
    desired_workers: int,
    *,
    active: bool = True,
    cpu_count: int | None = None,
) -> PoolHandle:
    """Reutiliza el Pool persistente o lo recrea limpiamente si cambia active/workers."""
    resolved = normalize_worker_count(desired_workers, cpu_count=cpu_count)

    if not active:
        close_pool_handle(handle)
        return PoolHandle(pool=None, workers=resolved)

    if handle.pool is not None and handle.workers == resolved:
        return handle

    close_pool_handle(handle)
    return create_pool_handle(resolved, cpu_count=cpu_count)


@contextmanager
def managed_worker_pool(
    workers: int,
    cpu_count: int | None = None,
) -> Iterator[PoolHandle]:
    """Gestor de contexto seguro que garantiza cierre limpio incluso ante excepciones."""
    handle = create_pool_handle(workers, cpu_count=cpu_count)
    try:
        yield handle
    finally:
        close_pool_handle(handle)
