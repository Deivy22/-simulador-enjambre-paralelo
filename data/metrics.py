"""Instantánea inmutable de métricas de rendimiento en vivo."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetricsSnapshot:
    """Telemetría congelada de FPS, tiempo exclusivo de física y hardware."""

    instant_fps: float = 0.0
    average_fps: float = 0.0
    physics_ms: float = 0.0
    frame_ms: float = 0.0
    fps_history: tuple[float, ...] = ()
    cpu_count: int = 1
    active_workers: int = 1
