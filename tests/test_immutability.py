"""Pruebas unitarias de inmutabilidad estricta de contratos base."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import pytest

from data import (
    Boid,
    FlatBoidSnapshot,
    GameState,
    InputState,
    MetricsSnapshot,
    MouseAction,
    ScreenMode,
    SimConfig,
    SimMode,
    StartAction,
    clamp_worker_count,
    default_worker_count,
    resolve_mouse_action,
    validate_config,
)


def test_boid_is_frozen_and_uses_slots() -> None:
    boid = Boid(x=10.0, y=20.0, vx=100.0, vy=-50.0)
    with pytest.raises(FrozenInstanceError):
        boid.x = 99.0  # type: ignore[misc]
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        boid.extra = 1  # type: ignore[attr-defined]


def test_flat_boid_snapshot_is_frozen() -> None:
    snapshot = FlatBoidSnapshot(
        xs=(1.0, 2.0),
        ys=(3.0, 4.0),
        vxs=(5.0, 6.0),
        vys=(7.0, 8.0),
    )
    assert isinstance(snapshot.xs, tuple)
    with pytest.raises(FrozenInstanceError):
        snapshot.xs = (9.0,)  # type: ignore[misc]


def test_game_state_is_frozen_and_replace_returns_new_instance() -> None:
    initial_boids = (Boid(x=1.0, y=2.0, vx=90.0, vy=0.0),)
    state = GameState(screen=ScreenMode.START, boids=initial_boids, mode=SimMode.SEQUENTIAL)

    assert isinstance(state.boids, tuple)
    with pytest.raises(FrozenInstanceError):
        state.frame = 1  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        state.paused = True  # type: ignore[misc]
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        state.dynamic_attr = "prohibido"  # type: ignore[attr-defined]

    next_state = replace(state, screen=ScreenMode.SIMULATION, frame=1)
    assert state.screen is ScreenMode.START
    assert state.frame == 0
    assert next_state.screen is ScreenMode.SIMULATION
    assert next_state.frame == 1


def test_sim_config_is_frozen_and_validates_two_zone_geometry() -> None:
    config = validate_config(SimConfig())
    assert config.window_width == 1280
    assert config.window_height == 720
    assert config.world_width == 960
    assert config.panel_width == 320
    assert config.world_width + config.panel_width == config.window_width

    with pytest.raises(FrozenInstanceError):
        config.entity_count = 3000  # type: ignore[misc]

    invalid_geometry = replace(config, panel_width=200)
    with pytest.raises(ValueError):
        validate_config(invalid_geometry)

    invalid_speed = replace(config, min_speed=300.0, max_speed=200.0)
    with pytest.raises(ValueError):
        validate_config(invalid_speed)


def test_input_state_is_frozen_and_mouse_precedence_rules() -> None:
    inp = InputState(
        mouse_pos=(250.0, 300.0),
        mouse_in_canvas=True,
        left_click=True,
        right_click=True,
        mouse_action=MouseAction.REPEL,
        start_action=StartAction.NONE,
    )
    with pytest.raises(FrozenInstanceError):
        inp.toggle_pause = True  # type: ignore[misc]

    assert resolve_mouse_action(True, False, True) is MouseAction.ATTRACT
    assert resolve_mouse_action(False, True, True) is MouseAction.REPEL
    assert resolve_mouse_action(True, True, True) is MouseAction.REPEL
    assert resolve_mouse_action(True, True, False) is MouseAction.NONE


def test_metrics_snapshot_is_frozen_with_tuple_history() -> None:
    metrics = MetricsSnapshot(
        instant_fps=60.0,
        average_fps=58.5,
        physics_ms=8.2,
        frame_ms=16.6,
        fps_history=(60.0, 57.0),
        cpu_count=8,
        active_workers=7,
    )
    assert isinstance(metrics.fps_history, tuple)
    with pytest.raises(FrozenInstanceError):
        metrics.physics_ms = 1.0  # type: ignore[misc]


def test_worker_count_helpers_respect_hardware_bounds() -> None:
    assert default_worker_count(1) == 1
    assert default_worker_count(8) == 7
    assert clamp_worker_count(0, cpu_count=8) == 1
    assert clamp_worker_count(12, cpu_count=8) == 8
    assert clamp_worker_count(4, cpu_count=8) == 4
