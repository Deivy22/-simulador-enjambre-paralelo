"""Pruebas unitarias de transiciones puras de GameState (Inicio ↔ Simulación y controles)."""

from __future__ import annotations

from dataclasses import replace

from core.engine import update_sequential
from core.state import apply_input_transitions, create_initial_state
from data import InputState, ScreenMode, SimConfig, SimMode, StartAction


def test_start_screen_selections_and_transition_to_simulation() -> None:
    state = create_initial_state(seed=7, screen=ScreenMode.START, cpu_count=8)
    assert state.screen is ScreenMode.START
    assert state.boids == ()
    assert state.workers == 7

    state = apply_input_transitions(state, InputState(start_action=StartAction.SELECT_3000))
    assert state.config.entity_count == 3000

    state = apply_input_transitions(state, InputState(start_action=StartAction.SELECT_SEQUENTIAL))
    assert state.mode is SimMode.SEQUENTIAL

    running = apply_input_transitions(state, InputState(start_action=StartAction.START_SIMULATION))
    assert running.screen is ScreenMode.SIMULATION
    assert len(running.boids) == 3000
    assert running.frame == 0
    assert running.paused is False


def test_simulation_controls_mode_workers_pause_entities_reset_and_menu() -> None:
    cfg = SimConfig(entity_count=50)
    state = create_initial_state(
        config=cfg,
        seed=42,
        screen=ScreenMode.SIMULATION,
        mode=SimMode.PARALLEL,
        workers=4,
        cpu_count=8,
    )
    state = replace(state, metrics=replace(state.metrics, fps_history=(60.0, 59.0)))

    # Alternar modo (M) reinicia historial FPS
    toggled = apply_input_transitions(state, InputState(toggle_mode=True))
    assert toggled.mode is SimMode.SEQUENTIAL
    assert toggled.metrics.fps_history == ()

    # Aumentar y acotar workers (+/-)
    more_workers = apply_input_transitions(toggled, InputState(worker_delta=10))
    assert more_workers.workers == 8
    assert more_workers.metrics.active_workers == 8

    less_workers = apply_input_transitions(more_workers, InputState(worker_delta=-20))
    assert less_workers.workers == 1
    assert less_workers.metrics.active_workers == 1

    # Pausa detiene el avance físico en update_sequential
    paused = update_sequential(less_workers, InputState(toggle_pause=True), dt=cfg.fixed_dt)
    assert paused.paused is True
    assert paused.frame == 0
    still_paused = update_sequential(paused, InputState(), dt=cfg.fixed_dt)
    assert still_paused.boids == paused.boids
    assert still_paused.frame == 0

    # Cambio de carga (1/3/5) regenera boids y limpia métricas
    scaled = apply_input_transitions(paused, InputState(requested_entity_count=100))
    assert scaled.config.entity_count == 100
    assert len(scaled.boids) == 100
    assert scaled.frame == 0

    # Avanza 1 frame y luego reinicia con R a la misma semilla determinista
    resumed = apply_input_transitions(scaled, InputState(toggle_pause=True))
    stepped = update_sequential(resumed, InputState(), dt=cfg.fixed_dt)
    assert stepped.frame == 1
    assert stepped.boids != scaled.boids

    reset_state = apply_input_transitions(stepped, InputState(reset_requested=True))
    assert reset_state.frame == 0
    assert reset_state.boids == scaled.boids

    # Regreso al Menú limpia boids y vuelve a START
    back_menu = apply_input_transitions(reset_state, InputState(return_to_menu=True))
    assert back_menu.screen is ScreenMode.START
    assert back_menu.boids == ()
    assert back_menu.frame == 0
