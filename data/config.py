"""Configuración inmutable de simulación y geometría de 2 zonas."""

from __future__ import annotations

from dataclasses import dataclass

VALID_ENTITY_COUNTS = (1000, 3000, 5000)


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
