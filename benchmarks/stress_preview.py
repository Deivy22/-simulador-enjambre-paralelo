"""Prueba preliminar de estrés en consola y perfilado de IPC."""

from __future__ import annotations

from dataclasses import dataclass

from core.engine import step_boids_sequential
from core.parallel import managed_worker_pool, step_boids_parallel
from core.state import measure_execution_ms, spawn_boids
from data import InputState, SimConfig


@dataclass(frozen=True, slots=True)
class StressResult:
    """Resumen inmutable de una corrida preliminar secuencial frente a paralela."""

    entity_count: int
    workers: int
    seq_ms: float
    par_ms: float
    speedup: float


def run_stress_case(
    entity_count: int,
    workers: int,
    frames: int = 5,
    seed: int = 42,
) -> StressResult:
    """Ejecuta pasos headless con dt fijo (1/60) para medir los motores."""
    cfg = SimConfig(entity_count=entity_count)
    dt = cfg.fixed_dt
    boids_seq = spawn_boids(entity_count, cfg, seed=seed)
    boids_par = boids_seq
    inp = InputState()

    step_boids_sequential(boids_seq, inp, cfg, dt)

    seq_times: tuple[float, ...] = ()
    for _ in range(frames):
        boids_seq, elapsed = measure_execution_ms(step_boids_sequential, boids_seq, inp, cfg, dt)
        seq_times = seq_times + (elapsed,)
    avg_seq_ms = sum(seq_times) / len(seq_times)

    with managed_worker_pool(workers=workers) as handle:
        assert handle.pool is not None
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
    return StressResult(
        entity_count=entity_count,
        workers=workers,
        seq_ms=avg_seq_ms,
        par_ms=avg_par_ms,
        speedup=speedup,
    )
