"""Instantánea inmutable de entradas del usuario para ambas pantallas."""

from __future__ import annotations

from dataclasses import dataclass

from data.types import MouseAction, StartAction, Vec2


@dataclass(frozen=True, slots=True)
class InputState:
    """Captura congelada de teclado, mouse y acciones discretas en un frame."""

    mouse_pos: Vec2 = (0.0, 0.0)
    mouse_in_canvas: bool = False
    left_click: bool = False
    right_click: bool = False
    mouse_action: MouseAction = MouseAction.NONE
    requested_entity_count: int | None = None
    toggle_mode: bool = False
    worker_delta: int = 0
    reset_requested: bool = False
    toggle_pause: bool = False
    return_to_menu: bool = False
    quit_requested: bool = False
    start_action: StartAction = StartAction.NONE
