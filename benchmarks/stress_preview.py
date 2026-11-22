"""Prueba preliminar de estrés en consola (1k, 3k y 5k entidades) y perfilado de IPC."""

from __future__ import annotations

from dataclasses import dataclass
import pickle
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


@dataclass(frozen=True, slots=True)
class StressResult:
    """Resumen inmutable de una corrida preliminar Secuencial vs Paralelo."""

    entity_count: int
    workers: int
    seq_ms: float
    par_ms: float
    speedup: float
    ipc_pickle_ms: float
    ipc_share_pct: float
    payload_kb: float


def run_stress_case(
    entity_count: int,
    workers: int,
    frames: int = 5,
    seed: int = 42,
) -> StressResult:
    """Ejecuta `frames` pasos headless con dt fijo (1/60) para medir física e IPC."""
    cfg = SimConfig(entity_count=entity_count)
    dt = cfg.fixed_dt
    boids_seq = spawn_boids(entity_count, cfg, seed=seed)
    boids_par = boids_seq
    inp = InputState()

    # Calentamiento secuencial (1 frame)
    step_boids_sequential(boids_seq, inp, cfg, dt)

    seq_times: tuple[float, ...] = ()
    for _ in range(frames):
        boids_seq, elapsed = measure_execution_ms(step_boids_sequential, boids_seq, inp, cfg, dt)
        seq_times = seq_times + (elapsed,)
    avg_seq_ms = sum(seq_times) / len(seq_times)

    # Perfilado de serialización IPC (pickle de todas las tareas de un frame)
    tasks = build_worker_tasks(boids_par, inp, cfg, dt, workers=workers)
    t_pkl = time.perf_counter()
    blobs = tuple(pickle.dumps(task) for task in tasks)
    ipc_pickle_ms = (time.perf_counter() - t_pkl) * 1000.0
    payload_kb = sum(len(b) for b in blobs) / 1024.0

    with managed_worker_pool(workers=workers) as handle:
        assert handle.pool is not None
        # Calentamiento del pool persistente
        step_boids_parallel(boids_par, inp, cfg, dt, handle.pool, workers=workers)

        par_times: tuple[float, ...] = ()
        for _ in range(frames):
            boids_par, elapsed = measure_execution_ms(
                step_boids_parallel,
                boids_par,
                inp,
                cfg,
                dt,
                handle.pool,
                workers,
            )
            par_times = par_times + (elapsed,)
    avg_par_ms = sum(par_times) / len(par_times)

    speedup = avg_seq_ms / avg_par_ms if avg_par_ms > 0.0 else 0.0
    ipc_share_pct = (ipc_pickle_ms / avg_par_ms * 100.0) if avg_par_ms > 0.0 else 0.0

    return StressResult(
        entity_count=entity_count,
        workers=workers,
        seq_ms=avg_seq_ms,
        par_ms=avg_par_ms,
        speedup=speedup,
        ipc_pickle_ms=ipc_pickle_ms,
        ipc_share_pct=ipc_share_pct,
        payload_kb=payload_kb,
    )


def main() -> None:
    """Punto de entrada protegido para pruebas preliminares de 1k, 3k y 5k en consola."""
    cpus = detect_cpu_cores()
    workers = recommended_worker_count(cpus)
    print(f"Hardware detectado: {cpus} núcleos lógicos | Workers activos: {workers} | dt = 1/60 s")
    print("-" * 92)
    print(
        f"{'Entidades':>10} | {'Secuencial (ms / FPS)':>22} | {'Paralelo (ms / FPS)':>22} | "
        f"{'Speedup':>8} | {'IPC pickle':>16}"
    )
    print("-" * 92)

    for count in (1000, 3000, 5000):
        res = run_stress_case(entity_count=count, workers=workers, frames=5)
        seq_fps = 1000.0 / res.seq_ms if res.seq_ms > 0.0 else 0.0
        par_fps = 1000.0 / res.par_ms if res.par_ms > 0.0 else 0.0
        print(
            f"{res.entity_count:10,d} | {res.seq_ms:7.2f} ms ({seq_fps:6.1f} FPS) | "
            f"{res.par_ms:7.2f} ms ({par_fps:6.1f} FPS) | {res.speedup:7.2f}x | "
            f"{res.ipc_pickle_ms:4.2f} ms ({res.ipc_share_pct:4.1f}%)"
        )


if __name__ == "__main__":
    main()
