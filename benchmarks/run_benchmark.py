"""Suite formal de benchmarking headless (1,000, 3,000 y 5,000 entidades) con salida Markdown."""

from __future__ import annotations

from dataclasses import dataclass
import pickle
import platform
import sys
import time

from core.engine import step_boids_sequential
from core.parallel import (
    build_worker_tasks,
    detect_cpu_cores,
    managed_worker_pool,
    recommended_worker_count,
    step_boids_parallel,
)
from core.state import measure_execution_ms, spawn_boids
from data import InputState, SimConfig

DEFAULT_ENTITY_LOADS: tuple[int, ...] = (1000, 3000, 5000)


@dataclass(frozen=True, slots=True)
class HardwareInfo:
    """Metadatos inmutables del hardware y entorno de ejecución detectados dinámicamente."""

    processor: str
    os_name: str
    python_version: str
    logical_cores: int
    active_workers: int


@dataclass(frozen=True, slots=True)
class BenchmarkRow:
    """Resultado congelado de una carga (Secuencial vs. Paralelo) con dt = 1/60 fijo."""

    entity_count: int
    frames: int
    seq_ms: float
    seq_fps: float
    par_ms: float
    par_fps: float
    speedup: float
    ipc_pickle_ms: float
    ipc_share_pct: float
    payload_kb: float


@dataclass(frozen=True, slots=True)
class BenchmarkReport:
    """Reporte completo inmutable listo para exportar a tabla Markdown."""

    hardware: HardwareInfo
    partition_strategy: str
    seed: int
    fixed_dt: float
    rows: tuple[BenchmarkRow, ...]


def collect_hardware_info(workers: int) -> HardwareInfo:
    """Captura información del hardware y runtime actual sin mutar estado global."""
    cores = detect_cpu_cores()
    processor = platform.processor() or platform.machine() or "Desconocido"
    os_name = f"{platform.system()} {platform.release()}"
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    return HardwareInfo(
        processor=processor,
        os_name=os_name,
        python_version=py_ver,
        logical_cores=cores,
        active_workers=workers,
    )


def run_benchmark_case(
    entity_count: int,
    workers: int,
    frames: int = 8,
    seed: int = 42,
) -> BenchmarkRow:
    """Mide Secuencial vs. Paralelo de forma headless y reproducible con dt = 1/60 fijo."""
    cfg = SimConfig(entity_count=entity_count)
    dt = cfg.fixed_dt
    initial_boids = spawn_boids(entity_count, cfg, seed=seed)
    idle_input = InputState()

    # Calentamiento secuencial
    boids_seq = step_boids_sequential(initial_boids, idle_input, cfg, dt)
    seq_times: tuple[float, ...] = ()
    for _ in range(frames):
        boids_seq, elapsed_ms = measure_execution_ms(
            step_boids_sequential,
            boids_seq,
            idle_input,
            cfg,
            dt,
        )
        seq_times = seq_times + (elapsed_ms,)
    avg_seq_ms = sum(seq_times) / len(seq_times)
    seq_fps = 1000.0 / avg_seq_ms if avg_seq_ms > 0.0 else 0.0

    # Medición de serialización IPC (pickle de las tareas de 1 frame)
    tasks = build_worker_tasks(initial_boids, idle_input, cfg, dt, workers=workers)
    t0 = time.perf_counter()
    serialized = tuple(pickle.dumps(task) for task in tasks)
    ipc_pickle_ms = (time.perf_counter() - t0) * 1000.0
    payload_kb = sum(len(blob) for blob in serialized) / 1024.0

    # Corrida paralela con Pool persistente
    with managed_worker_pool(workers=workers) as handle:
        assert handle.pool is not None
        boids_par = step_boids_parallel(
            initial_boids,
            idle_input,
            cfg,
            dt,
            handle.pool,
            workers=workers,
        )
        par_times: tuple[float, ...] = ()
        for _ in range(frames):
            boids_par, elapsed_ms = measure_execution_ms(
                step_boids_parallel,
                boids_par,
                idle_input,
                cfg,
                dt,
                handle.pool,
                workers,
            )
            par_times = par_times + (elapsed_ms,)

    avg_par_ms = sum(par_times) / len(par_times)
    par_fps = 1000.0 / avg_par_ms if avg_par_ms > 0.0 else 0.0
    speedup = avg_seq_ms / avg_par_ms if avg_par_ms > 0.0 else 0.0
    ipc_share_pct = (ipc_pickle_ms / avg_par_ms * 100.0) if avg_par_ms > 0.0 else 0.0

    return BenchmarkRow(
        entity_count=entity_count,
        frames=frames,
        seq_ms=avg_seq_ms,
        seq_fps=seq_fps,
        par_ms=avg_par_ms,
        par_fps=par_fps,
        speedup=speedup,
        ipc_pickle_ms=ipc_pickle_ms,
        ipc_share_pct=ipc_share_pct,
        payload_kb=payload_kb,
    )


def run_full_benchmark(
    loads: tuple[int, ...] = DEFAULT_ENTITY_LOADS,
    workers: int | None = None,
    frames: int = 8,
    seed: int = 42,
) -> BenchmarkReport:
    """Ejecuta la batería completa (1k, 3k y 5k) y retorna un BenchmarkReport congelado."""
    resolved_workers = recommended_worker_count() if workers is None else max(1, workers)
    hw = collect_hardware_info(resolved_workers)
    rows = tuple(
        run_benchmark_case(entity_count=n, workers=resolved_workers, frames=frames, seed=seed)
        for n in loads
    )
    strategy = (
        f"1 chunk balanceado por worker ({resolved_workers} chunks) sobre Grilla Espacial "
        "Inmutable O(N·k) + PackedBoidBuffer (bytes float64)"
    )
    return BenchmarkReport(
        hardware=hw,
        partition_strategy=strategy,
        seed=seed,
        fixed_dt=SimConfig().fixed_dt,
        rows=rows,
    )
