"""Funciones puras de creación inicial y transiciones inmutables de GameState."""

from __future__ import annotations

import math
import random

from data.config import (
    SimConfig,
    clamp_worker_count,
    default_worker_count,
    detected_cpu_count,
    validate_config,
)
from data.entities import Boid
from data.game_state import GameState
from data.input_state import InputState
from data.metrics import MetricsSnapshot
from data.types import ScreenMode, SimMode


def _make_random_boid(rng: random.Random, config: SimConfig) -> Boid:
    """Genera un Boid determinista dentro del área segura del Canvas."""
    pad = config.margin
    x = rng.uniform(pad, float(config.world_width) - pad)
    y = rng.uniform(pad, float(config.world_height) - pad)
    angle = rng.uniform(0.0, math.tau)
    speed = rng.uniform(config.min_speed, config.max_speed)
    return Boid(
        x=x,
        y=y,
        vx=math.cos(angle) * speed,
        vy=math.sin(angle) * speed,
    )


def spawn_boids(count: int, config: SimConfig, seed: int) -> tuple[Boid, ...]:
    """Crea una tupla inmutable de `count` boids usando un PRNG local determinista."""
    if count < 0:
        raise ValueError("count no puede ser negativo.")
    rng = random.Random(seed)
    return tuple(_make_random_boid(rng, config) for _ in range(count))


def _reset_metrics(cpu_count: int, active_workers: int) -> MetricsSnapshot:
    """Retorna una instantánea limpia de métricas preservando hardware y workers."""
    return MetricsSnapshot(
        instant_fps=0.0,
        average_fps=0.0,
        physics_ms=0.0,
        frame_ms=0.0,
        fps_history=(),
        cpu_count=cpu_count,
        active_workers=active_workers,
    )


def create_initial_state(
    config: SimConfig | None = None,
    seed: int = 42,
    screen: ScreenMode = ScreenMode.START,
    mode: SimMode = SimMode.PARALLEL,
    workers: int | None = None,
    cpu_count: int | None = None,
    spawn_entities: bool | None = None,
) -> GameState:
    """Construye un GameState inicial válido e inmutable para Inicio o Simulación."""
    validated = validate_config(SimConfig() if config is None else config)
    detected_cpus = detected_cpu_count() if cpu_count is None else max(1, cpu_count)
    resolved_workers = (
        default_worker_count(detected_cpus)
        if workers is None
        else clamp_worker_count(workers, detected_cpus)
    )
    should_spawn = (screen is ScreenMode.SIMULATION) if spawn_entities is None else spawn_entities
    boids = spawn_boids(validated.entity_count, validated, seed) if should_spawn else ()

    return GameState(
        screen=screen,
        boids=boids,
        config=validated,
        mode=mode,
        workers=resolved_workers,
        paused=False,
        frame=0,
        seed=seed,
        metrics=_reset_metrics(detected_cpus, resolved_workers),
        input_state=InputState(),
    )
