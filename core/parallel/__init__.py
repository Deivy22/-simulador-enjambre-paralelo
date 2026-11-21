"""Subpaquete de pipeline paralelo con multiprocessing."""

from core.parallel.engine import (
    build_worker_tasks,
    consolidate_chunk_results,
    step_boids_parallel,
    update_parallel,
)
from core.parallel.ipc_codec import (
    pack_boids_to_flat_tuples,
    pack_boids_to_snapshot,
    unpack_flat_tuples_to_boids,
    unpack_snapshot_to_boids,
)
from core.parallel.partition import (
    compute_chunk_ranges,
    detect_cpu_cores,
    normalize_worker_count,
    recommended_worker_count,
    verify_chunk_partition,
)
from core.parallel.pool_lifecycle import (
    PoolHandle,
    close_pool_handle,
    create_pool_handle,
    ensure_pool_workers,
    managed_worker_pool,
)
from core.parallel.worker import WorkerTask, process_boid_chunk

__all__: tuple[str, ...] = (
    "PoolHandle",
    "WorkerTask",
    "build_worker_tasks",
    "close_pool_handle",
    "compute_chunk_ranges",
    "consolidate_chunk_results",
    "create_pool_handle",
    "detect_cpu_cores",
    "ensure_pool_workers",
    "managed_worker_pool",
    "normalize_worker_count",
    "pack_boids_to_flat_tuples",
    "pack_boids_to_snapshot",
    "process_boid_chunk",
    "recommended_worker_count",
    "step_boids_parallel",
    "unpack_flat_tuples_to_boids",
    "unpack_snapshot_to_boids",
    "update_parallel",
    "verify_chunk_partition",
)
