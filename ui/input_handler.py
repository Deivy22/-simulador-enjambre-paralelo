"""Resolución pura de clics de la Pantalla de Inicio."""

from __future__ import annotations

from collections.abc import Sequence

import pygame

from data.config import SimConfig
from data.input_state import InputState, resolve_mouse_action
from data.types import ScreenMode, StartAction, Vec2
from ui.layout import SimulationLayout, StartScreenLayout, point_in_rect


def _resolve_start_click(
    click_pos: Vec2,
    start_layout: StartScreenLayout,
) -> StartAction:
    """Mapea clics de los selectores y el botón principal a acciones inmutables."""
    if point_in_rect(click_pos, start_layout.btn_1000):
        return StartAction.SELECT_1000
    if point_in_rect(click_pos, start_layout.btn_3000):
        return StartAction.SELECT_3000
    if point_in_rect(click_pos, start_layout.btn_5000):
        return StartAction.SELECT_5000
    if point_in_rect(click_pos, start_layout.btn_sequential):
        return StartAction.SELECT_SEQUENTIAL
    if point_in_rect(click_pos, start_layout.btn_parallel):
        return StartAction.SELECT_PARALLEL
    if point_in_rect(click_pos, start_layout.btn_start):
        return StartAction.START_SIMULATION
    return StartAction.NONE


def translate_events_to_input(
    events: Sequence[pygame.event.Event],
    mouse_pos: Vec2,
    mouse_buttons: tuple[bool, bool, bool],
    screen: ScreenMode,
    config: SimConfig,
    start_layout: StartScreenLayout,
    sim_layout: SimulationLayout,
) -> InputState:
    """Traduce eventos discretos a un único InputState congelado."""
    left_click = bool(mouse_buttons[0])
    right_click = bool(mouse_buttons[2])
    mouse_in_canvas = (
        screen is ScreenMode.SIMULATION
        and point_in_rect(mouse_pos, sim_layout.canvas)
    )
    mouse_action = resolve_mouse_action(left_click, right_click, mouse_in_canvas)

    quit_requested = False
    toggle_mode = False
    toggle_pause = False
    reset_requested = False
    return_to_menu = False
    worker_delta = 0
    requested_entity_count: int | None = None
    start_action = StartAction.NONE

    for event in events:
        if event.type == pygame.QUIT:
            quit_requested = True
        elif event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_ESCAPE:
                quit_requested = True
            elif screen is ScreenMode.START:
                if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    start_action = StartAction.START_SIMULATION
                elif key in (pygame.K_1, pygame.K_KP1):
                    start_action = StartAction.SELECT_1000
                elif key in (pygame.K_3, pygame.K_KP3):
                    start_action = StartAction.SELECT_3000
                elif key in (pygame.K_5, pygame.K_KP5):
                    start_action = StartAction.SELECT_5000
                elif key == pygame.K_s:
                    start_action = StartAction.SELECT_SEQUENTIAL
                elif key == pygame.K_p:
                    start_action = StartAction.SELECT_PARALLEL
            else:
                if key in (pygame.K_1, pygame.K_KP1):
                    requested_entity_count = 1000
                elif key in (pygame.K_3, pygame.K_KP3):
                    requested_entity_count = 3000
                elif key in (pygame.K_5, pygame.K_KP5):
                    requested_entity_count = 5000
                elif key == pygame.K_m:
                    toggle_mode = True
                elif key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                    worker_delta += 1
                elif key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    worker_delta -= 1
                elif key == pygame.K_r:
                    reset_requested = True
                elif key == pygame.K_SPACE:
                    toggle_pause = True
                elif key == pygame.K_BACKSPACE:
                    return_to_menu = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click_pos: Vec2 = (float(event.pos[0]), float(event.pos[1]))
            if screen is ScreenMode.START:
                resolved = _resolve_start_click(click_pos, start_layout)
                if resolved is not StartAction.NONE:
                    start_action = resolved
            elif point_in_rect(click_pos, sim_layout.btn_menu):
                return_to_menu = True

    return InputState(
        mouse_pos=mouse_pos,
        mouse_in_canvas=mouse_in_canvas,
        left_click=left_click,
        right_click=right_click,
        mouse_action=mouse_action,
        requested_entity_count=requested_entity_count,
        toggle_mode=toggle_mode,
        worker_delta=worker_delta,
        reset_requested=reset_requested,
        toggle_pause=toggle_pause,
        return_to_menu=return_to_menu,
        quit_requested=quit_requested,
        start_action=start_action,
    )
