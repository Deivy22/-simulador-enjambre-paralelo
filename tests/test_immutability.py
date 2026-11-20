"""Pruebas unitarias de inmutabilidad estricta de contratos base."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import pytest

from data import Boid, FlatBoidSnapshot, GameState, ScreenMode, SimMode


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
