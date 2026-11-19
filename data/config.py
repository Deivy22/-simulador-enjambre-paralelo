"""Configuración inmutable de simulación y geometría de 2 zonas."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Final

VALID_ENTITY_COUNTS: Final[tuple[int, ...]] = (1000, 3000, 5000)


@dataclass(frozen=True, slots=True)
class SimConfig:
    """Parámetros inmutables del simulador, geometría de 2 zonas y física Boids."""

    window_width: int = 1280
    window_height: int = 720
    world_width: int = 960
    world_height: int = 720
    panel_width: int = 320
    entity_count: int = 1000
    perception_radius: float = 45.0
    separation_radius: float = 18.0
    separation_epsilon: float = 1.0
    mouse_radius: float = 150.0
    mouse_strength: float = 260.0
    max_speed: float = 220.0
    min_speed: float = 90.0
    margin: float = 60.0
    turn_factor: float = 280.0
    max_dt: float = 0.05
    fixed_dt: float = 1.0 / 60.0
    weight_separation: float = 1.8
    weight_alignment: float = 1.0
    weight_cohesion: float = 0.9
    weight_mouse: float = 2.5
    fps_window_size: int = 60


def detected_cpu_count() -> int:
    """Retorna la cantidad de núcleos lógicos detectados (mínimo 1)."""
    count = os.cpu_count()
    return count if count is not None and count > 0 else 1


def default_worker_count(cpu_count: int | None = None) -> int:
    """Calcula el número inicial de workers: max(1, cpu_count - 1)."""
    total = detected_cpu_count() if cpu_count is None else max(1, cpu_count)
    return max(1, total - 1)


def clamp_worker_count(workers: int, cpu_count: int | None = None) -> int:
    """Acota la cantidad de workers al rango válido [1, cpu_count]."""
    max_workers = detected_cpu_count() if cpu_count is None else max(1, cpu_count)
    return max(1, min(workers, max_workers))


def validate_config(config: SimConfig) -> SimConfig:
    """Valida las invariantes físicas y geométricas de SimConfig sin mutarlo."""
    if config.window_width <= 0 or config.window_height <= 0:
        raise ValueError("Las dimensiones de ventana deben ser positivas.")
    if config.world_width <= 0 or config.world_height <= 0 or config.panel_width < 0:
        raise ValueError("Las dimensiones del mundo y panel deben ser válidas.")
    if config.world_width + config.panel_width != config.window_width:
        raise ValueError("world_width + panel_width debe ser igual a window_width.")
    if config.world_height != config.window_height:
        raise ValueError("world_height debe coincidir con window_height.")
    if config.entity_count <= 0:
        raise ValueError("entity_count debe ser mayor que cero.")
    if config.perception_radius <= 0.0 or config.separation_radius <= 0.0:
        raise ValueError("Los radios de percepción y separación deben ser positivos.")
    if config.separation_radius > config.perception_radius:
        raise ValueError("separation_radius no puede exceder perception_radius.")
    if config.separation_epsilon <= 0.0:
        raise ValueError("separation_epsilon debe ser mayor que cero.")
    if config.min_speed <= 0.0 or config.max_speed < config.min_speed:
        raise ValueError("Debe cumplirse 0 < min_speed <= max_speed.")
    if config.margin < 0.0 or config.margin * 2.0 >= min(config.world_width, config.world_height):
        raise ValueError("margin debe ser no negativo y menor que la mitad del mundo.")
    if config.max_dt <= 0.0 or config.fixed_dt <= 0.0:
        raise ValueError("max_dt y fixed_dt deben ser positivos.")
    if config.fps_window_size <= 0:
        raise ValueError("fps_window_size debe ser mayor que cero.")
    return config
