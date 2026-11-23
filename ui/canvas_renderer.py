"""Renderizado 2D eficiente del Canvas leyendo exclusivamente el GameState congelado."""

from __future__ import annotations

import math

import pygame

from data.entities import Boid
from data.game_state import GameState
from data.types import MouseAction
from ui.layout import SimulationLayout
from ui.theme import THEME, UiFonts


def compute_boid_chevron_points(
    boid: Boid,
    length: float = 7.5,
    half_width: float = 3.2,
) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    """Calcula los 3 vértices del boid orientado usando (vx, vy) sin cos()/sin()."""
    vx = boid.vx
    vy = boid.vy
    speed_sq = vx * vx + vy * vy
    if speed_sq > 1e-8:
        inv_speed = 1.0 / math.sqrt(speed_sq)
        ux = vx * inv_speed
        uy = vy * inv_speed
    else:
        ux = 1.0
        uy = 0.0

    # Vector perpendicular (-uy, ux)
    px = -uy * half_width
    py = ux * half_width

    bx = boid.x
    by = boid.y
    tip_x = bx + ux * length
    tip_y = by + uy * length
    tail_x = bx - ux * (length * 0.55)
    tail_y = by - uy * (length * 0.55)

    return (
        (tip_x, tip_y),
        (tail_x + px, tail_y + py),
        (tail_x - px, tail_y - py),
    )


def _render_cursor_indicator(
    surface: pygame.Surface,
    state: GameState,
) -> None:
    """Dibuja el anillo fino del cursor cuando hay atracción o repulsión activa en el Canvas."""
    inp = state.input_state
    if not inp.mouse_in_canvas or inp.mouse_action is MouseAction.NONE:
        return

    color = (
        THEME.cursor_attract
        if inp.mouse_action is MouseAction.ATTRACT
        else THEME.cursor_repel
    )
    center = (int(inp.mouse_pos[0]), int(inp.mouse_pos[1]))
    radius = int(state.config.mouse_radius)
    pygame.draw.circle(surface, color, center, radius, 1)
    pygame.draw.circle(surface, color, center, 4, 0)


def _render_paused_badge(
    surface: pygame.Surface,
    layout: SimulationLayout,
    fonts: UiFonts,
) -> None:
    """Muestra una etiqueta discreta cuando la simulación está pausada."""
    label = fonts.mono.render("PAUSADO  [ESPACIO]", True, THEME.badge_paused)
    pad_x = 12
    pad_y = 6
    box_w = label.get_width() + pad_x * 2
    box_h = label.get_height() + pad_y * 2
    box_rect = pygame.Rect(
        layout.canvas.x + layout.canvas.width - box_w - 16,
        layout.canvas.y + 14,
        box_w,
        box_h,
    )
    pygame.draw.rect(surface, THEME.panel_bg, box_rect, border_radius=5)
    pygame.draw.rect(surface, THEME.badge_paused, box_rect, width=1, border_radius=5)
    surface.blit(label, (box_rect.x + pad_x, box_rect.y + pad_y))


def render_canvas(
    surface: pygame.Surface,
    state: GameState,
    layout: SimulationLayout,
    fonts: UiFonts,
) -> None:
    """Renderiza el lienzo izquierdo (960×720) en modo estricto de solo lectura."""
    canvas_rect = pygame.Rect(
        layout.canvas.x,
        layout.canvas.y,
        layout.canvas.width,
        layout.canvas.height,
    )
    surface.fill(THEME.canvas_bg, canvas_rect)

    # Recorte estricto al Canvas para garantizar cero solapamiento con el Panel Lateral
    previous_clip = surface.get_clip()
    surface.set_clip(canvas_rect)
    try:
        draw_polygon = pygame.draw.polygon
        cyan = THEME.boid_cyan
        mint = THEME.boid_mint
        speed_mid_sq = ((state.config.min_speed + state.config.max_speed) * 0.5) ** 2

        for boid in state.boids:
            vx = boid.vx
            vy = boid.vy
            speed_sq = vx * vx + vy * vy
            color = mint if speed_sq >= speed_mid_sq else cyan
            if speed_sq > 1e-8:
                inv_speed = 1.0 / math.sqrt(speed_sq)
                ux = vx * inv_speed
                uy = vy * inv_speed
            else:
                ux = 1.0
                uy = 0.0

            bx = boid.x
            by = boid.y
            px = -uy * 3.0
            py = ux * 3.0
            tail_x = bx - ux * 4.0
            tail_y = by - uy * 4.0

            draw_polygon(
                surface,
                color,
                (
                    (bx + ux * 7.2, by + uy * 7.2),
                    (tail_x + px, tail_y + py),
                    (tail_x - px, tail_y - py),
                ),
            )

        _render_cursor_indicator(surface, state)
        if state.paused:
            _render_paused_badge(surface, layout, fonts)
    finally:
        surface.set_clip(previous_clip)
