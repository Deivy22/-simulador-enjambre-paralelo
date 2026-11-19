"""Estado global único e inmutable de toda la aplicación."""

from __future__ import annotations

from dataclasses import dataclass, field

from data.config import SimConfig, default_worker_count
from data.entities import Boid
from data.input_state import InputState
from data.metrics import MetricsSnapshot
from data.types import ScreenMode, SimMode


@dataclass(frozen=True, slots=True)
class GameState:
    """Fuente única de verdad congelada (pantallas, entidades, configuración y métricas)."""

    screen: ScreenMode = ScreenMode.START
    boids: tuple[Boid, ...] = ()
    config: SimConfig = field(default_factory=SimConfig)
    mode: SimMode = SimMode.PARALLEL
    workers: int = field(default_factory=default_worker_count)
    paused: bool = False
    frame: int = 0
    seed: int = 42
    metrics: MetricsSnapshot = field(default_factory=MetricsSnapshot)
    input_state: InputState = field(default_factory=InputState)
