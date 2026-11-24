"""Capa 3 (ui): Presentación Pygame, captura de entradas y orquestación."""

from ui.app import run_simulator
from ui.layout import (
    RectBox,
    SimulationLayout,
    StartScreenLayout,
    build_simulation_layout,
    build_start_layout,
    point_in_rect,
)

__all__: tuple[str, ...] = (
    "RectBox",
    "SimulationLayout",
    "StartScreenLayout",
    "build_simulation_layout",
    "build_start_layout",
    "point_in_rect",
    "run_simulator",
)
