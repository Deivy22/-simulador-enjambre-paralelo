"""Geometría pura e inmutable para Pantalla de Inicio y Simulación en 2 Zonas."""

from __future__ import annotations

from dataclasses import dataclass

from data.config import SimConfig
from data.types import Vec2


@dataclass(frozen=True, slots=True)
class RectBox:
    """Rectángulo 2D inmutable independiente de Pygame."""

    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class StartScreenLayout:
    """Distribución congelada de la tarjeta central y controles en Pantalla de Inicio."""

    card: RectBox
    btn_1000: RectBox
    btn_3000: RectBox
    btn_5000: RectBox
    btn_sequential: RectBox
    btn_parallel: RectBox
    btn_start: RectBox
    status_bar: RectBox


@dataclass(frozen=True, slots=True)
class SimulationLayout:
    """Distribución congelada de las 2 zonas sin solapamiento (Canvas + Panel Lateral)."""

    canvas: RectBox
    panel: RectBox
    divider_x: int
    btn_menu: RectBox


def point_in_rect(point: Vec2, rect: RectBox) -> bool:
    """Retorna True si el punto (x, y) cae dentro del rectángulo rect."""
    px, py = point
    return (
        rect.x <= px < rect.x + rect.width
        and rect.y <= py < rect.y + rect.height
    )


def build_start_layout(config: SimConfig) -> StartScreenLayout:
    """Calcula puramente los rectángulos centrados de la Pantalla de Inicio."""
    card_w = 500
    card_h = 460
    card_x = (config.window_width - card_w) // 2
    card_y = (config.window_height - card_h - 32) // 2
    pad_x = 34
    inner_w = card_w - pad_x * 2

    gap_3 = 12
    load_btn_w = (inner_w - gap_3 * 2) // 3
    load_y = card_y + 168
    load_h = 44

    gap_2 = 12
    mode_btn_w = (inner_w - gap_2) // 2
    mode_y = card_y + 252
    mode_h = 44

    start_y = card_y + 324
    start_h = 50

    return StartScreenLayout(
        card=RectBox(card_x, card_y, card_w, card_h),
        btn_1000=RectBox(card_x + pad_x, load_y, load_btn_w, load_h),
        btn_3000=RectBox(card_x + pad_x + load_btn_w + gap_3, load_y, load_btn_w, load_h),
        btn_5000=RectBox(
            card_x + pad_x + (load_btn_w + gap_3) * 2,
            load_y,
            inner_w - (load_btn_w + gap_3) * 2,
            load_h,
        ),
        btn_sequential=RectBox(card_x + pad_x, mode_y, mode_btn_w, mode_h),
        btn_parallel=RectBox(
            card_x + pad_x + mode_btn_w + gap_2,
            mode_y,
            inner_w - mode_btn_w - gap_2,
            mode_h,
        ),
        btn_start=RectBox(card_x + pad_x, start_y, inner_w, start_h),
        status_bar=RectBox(0, config.window_height - 32, config.window_width, 32),
    )


def build_simulation_layout(config: SimConfig) -> SimulationLayout:
    """Calcula puramente las 2 zonas: Canvas (960×720) y Panel Lateral (320×720)."""
    panel_x = config.world_width
    panel_w = config.panel_width
    btn_margin = 20
    btn_h = 36
    btn_y = config.window_height - btn_h - 18

    return SimulationLayout(
        canvas=RectBox(0, 0, config.world_width, config.world_height),
        panel=RectBox(panel_x, 0, panel_w, config.window_height),
        divider_x=panel_x,
        btn_menu=RectBox(panel_x + btn_margin, btn_y, panel_w - btn_margin * 2, btn_h),
    )
