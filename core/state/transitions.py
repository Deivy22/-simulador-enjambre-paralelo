"""Funciones puras de creación inicial y transiciones inmutables de GameState."""

from __future__ import annotations

from dataclasses import replace
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
from data.types import ScreenMode, SimMode, StartAction


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


def apply_start_screen_input(state: GameState, input_state: InputState) -> GameState:
    """Aplica puramente las selecciones y el inicio desde la Pantalla de Inicio."""
    action = input_state.start_action
    updated = replace(state, input_state=input_state)

    if action is StartAction.SELECT_1000:
        return replace(updated, config=replace(updated.config, entity_count=1000))
    if action is StartAction.SELECT_3000:
        return replace(updated, config=replace(updated.config, entity_count=3000))
    if action is StartAction.SELECT_5000:
        return replace(updated, config=replace(updated.config, entity_count=5000))
    if action is StartAction.SELECT_SEQUENTIAL:
        return replace(updated, mode=SimMode.SEQUENTIAL)
    if action is StartAction.SELECT_PARALLEL:
        return replace(updated, mode=SimMode.PARALLEL)
    if action is StartAction.START_SIMULATION:
        boids = spawn_boids(updated.config.entity_count, updated.config, updated.seed)
        return replace(
            updated,
            screen=ScreenMode.SIMULATION,
            boids=boids,
            paused=False,
            frame=0,
            metrics=_reset_metrics(updated.metrics.cpu_count, updated.workers),
        )
    return updated


def apply_simulation_input(state: GameState, input_state: InputState) -> GameState:
    """Aplica puramente atajos en vivo (1/3/5, M, +/-, R, Espacio, Menú) sin mutación."""
    if input_state.return_to_menu:
        return replace(
            state,
            screen=ScreenMode.START,
            boids=(),
            paused=False,
            frame=0,
            metrics=_reset_metrics(state.metrics.cpu_count, state.workers),
            input_state=input_state,
        )

    next_config = state.config
    next_boids = state.boids
    next_mode = state.mode
    next_workers = state.workers
    next_paused = (not state.paused) if input_state.toggle_pause else state.paused
    next_frame = state.frame
    next_metrics = state.metrics

    if input_state.toggle_mode:
        next_mode = (
            SimMode.SEQUENTIAL if state.mode is SimMode.PARALLEL else SimMode.PARALLEL
        )
        next_metrics = _reset_metrics(state.metrics.cpu_count, next_workers)

    if input_state.worker_delta != 0:
        next_workers = clamp_worker_count(
            state.workers + input_state.worker_delta,
            cpu_count=state.metrics.cpu_count,
        )
        next_metrics = replace(next_metrics, active_workers=next_workers)

    if (
        input_state.requested_entity_count is not None
        and input_state.requested_entity_count > 0
        and input_state.requested_entity_count != next_config.entity_count
    ):
        next_config = replace(next_config, entity_count=input_state.requested_entity_count)
        next_boids = spawn_boids(next_config.entity_count, next_config, state.seed)
        next_frame = 0
        next_metrics = _reset_metrics(state.metrics.cpu_count, next_workers)
    elif input_state.reset_requested:
        next_boids = spawn_boids(next_config.entity_count, next_config, state.seed)
        next_frame = 0
        next_metrics = _reset_metrics(state.metrics.cpu_count, next_workers)

    return replace(
        state,
        boids=next_boids,
        config=next_config,
        mode=next_mode,
        workers=next_workers,
        paused=next_paused,
        frame=next_frame,
        metrics=next_metrics,
        input_state=input_state,
    )


def apply_input_transitions(state: GameState, input_state: InputState) -> GameState:
    """Despacha puramente las entradas según la pantalla activa (START / SIMULATION)."""
    if state.screen is ScreenMode.START:
        return apply_start_screen_input(state, input_state)
    return apply_simulation_input(state, input_state)
