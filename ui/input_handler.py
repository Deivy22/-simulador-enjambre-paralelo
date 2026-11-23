"""Resolución pura de clics de la Pantalla de Inicio."""

from __future__ import annotations

from data.types import StartAction, Vec2
from ui.layout import StartScreenLayout, point_in_rect


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
