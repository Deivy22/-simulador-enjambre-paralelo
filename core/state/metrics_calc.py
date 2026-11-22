"""Cálculo puro de métricas de rendimiento y utilidades de tiempo."""

from __future__ import annotations

from data.config import SimConfig


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
