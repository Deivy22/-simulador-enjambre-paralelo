"""Cálculo puro de métricas de rendimiento y utilidades de tiempo."""

from __future__ import annotations

from collections.abc import Callable
import time
from typing import ParamSpec, TypeVar

from data.config import SimConfig
from data.metrics import MetricsSnapshot

P = ParamSpec("P")
R = TypeVar("R")


def clamp_interactive_dt(raw_dt: float, config: SimConfig) -> float:
    """Acota el dt real del Game Loop interactivo a [0.0, config.max_dt]."""
    if raw_dt <= 0.0:
        return 0.0
    if raw_dt > config.max_dt:
        return config.max_dt
    return raw_dt


def compute_instant_fps(frame_ms: float) -> float:
    """Convierte la duración de frame en milisegundos a FPS instantáneos."""
    if frame_ms <= 0.0:
        return 0.0
    return 1000.0 / frame_ms


def update_metrics_snapshot(
    prev: MetricsSnapshot,
    physics_ms: float,
    frame_ms: float,
    window_size: int = 60,
    cpu_count: int | None = None,
    active_workers: int | None = None,
) -> MetricsSnapshot:
    """Construye un MetricsSnapshot congelado con una ventana móvil inmutable de FPS."""
    if window_size <= 0:
        raise ValueError("window_size debe ser mayor que cero.")

    instant_fps = compute_instant_fps(frame_ms)
    history = (prev.fps_history + (instant_fps,))[-window_size:]
    average_fps = sum(history) / len(history) if history else 0.0

    return MetricsSnapshot(
        instant_fps=instant_fps,
        average_fps=average_fps,
        physics_ms=max(0.0, physics_ms),
        frame_ms=max(0.0, frame_ms),
        fps_history=history,
        cpu_count=prev.cpu_count if cpu_count is None else cpu_count,
        active_workers=prev.active_workers if active_workers is None else active_workers,
    )


def measure_execution_ms(
    fn: Callable[P, R],
    *args: P.args,
    **kwargs: P.kwargs,
) -> tuple[R, float]:
    """Mide el tiempo de ejecución de una función con time.perf_counter."""
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return (result, elapsed_ms)
