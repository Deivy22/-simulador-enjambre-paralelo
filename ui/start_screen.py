"""Renderizado solo-lectura de la Pantalla de Inicio (Launcher pastel 1280×720)."""

from __future__ import annotations

import sys

import pygame

from data.game_state import GameState
from data.types import SimMode
from ui.layout import RectBox, StartScreenLayout, point_in_rect
from ui.theme import THEME, ColorRGB, UiFonts


def _to_pygame_rect(box: RectBox) -> pygame.Rect:
    """Convierte un RectBox inmutable en pygame.Rect para dibujado."""
    return pygame.Rect(box.x, box.y, box.width, box.height)


def _draw_dot_grid_background(surface: pygame.Surface, width: int, height: int) -> None:
    """Dibuja un patrón discreto de puntos sobre el fondo oscuro sin penalizar rendimiento."""
    surface.fill(THEME.canvas_bg)
    dot_color = THEME.dot_grid
    for y in range(20, height - 32, 32):
        for x in range(20, width, 32):
            surface.fill(dot_color, (x, y, 2, 2))


def _draw_option_button(
    surface: pygame.Surface,
    box: RectBox,
    label: str,
    selected: bool,
    hovered: bool,
    accent: ColorRGB,
    fonts: UiFonts,
    dot_color: ColorRGB | None = None,
) -> None:
    """Dibuja un botón selector limpio con borde resaltado cuando está activo."""
    rect = _to_pygame_rect(box)
    fill = THEME.button_hover if (selected or hovered) else THEME.button_bg
    border = accent if selected else THEME.border
    border_width = 2 if selected else 1

    pygame.draw.rect(surface, fill, rect, border_radius=6)
    pygame.draw.rect(surface, border, rect, width=border_width, border_radius=6)

    text_color = accent if selected else THEME.text_primary
    text_surf = fonts.body_bold.render(label, True, text_color)
    total_w = text_surf.get_width() + (14 if dot_color is not None else 0)
    start_x = rect.centerx - total_w // 2
    text_y = rect.centery - text_surf.get_height() // 2

    if dot_color is not None:
        pygame.draw.rect(surface, dot_color, (start_x, rect.centery - 3, 6, 6), border_radius=2)
        surface.blit(text_surf, (start_x + 14, text_y))
    else:
        surface.blit(text_surf, (start_x, text_y))


def render_start_screen(
    surface: pygame.Surface,
    state: GameState,
    layout: StartScreenLayout,
    fonts: UiFonts,
) -> None:
    """Dibuja la Pantalla de Inicio limpia (sin barra macOS ni textos falsos)."""
    cfg = state.config
    mouse_pos = state.input_state.mouse_pos
    _draw_dot_grid_background(surface, cfg.window_width, cfg.window_height)

    card_rect = _to_pygame_rect(layout.card)
    pygame.draw.rect(surface, THEME.card_bg, card_rect, border_radius=10)
    pygame.draw.rect(surface, THEME.border, card_rect, width=1, border_radius=10)

    inner_x = card_rect.x + 34
    inner_right = card_rect.right - 34

    # Encabezado de la tarjeta
    pygame.draw.rect(surface, THEME.accent_cyan, (inner_x, card_rect.y + 34, 7, 7), border_radius=2)
    tag_surf = fonts.mono.render("PYGAME PARALLEL ENGINE", True, THEME.accent_cyan)
    surface.blit(tag_surf, (inner_x + 14, card_rect.y + 30))

    title_surf = fonts.title.render("Simulador de Enjambre 2D", True, THEME.text_primary)
    surface.blit(title_surf, (inner_x, card_rect.y + 56))

    sub_surf = fonts.body.render(
        "Multiprocessing & Programación Funcional",
        True,
        THEME.text_secondary,
    )
    surface.blit(sub_surf, (inner_x, card_rect.y + 92))

    pygame.draw.line(
        surface,
        THEME.border,
        (inner_x, card_rect.y + 126),
        (inner_right, card_rect.y + 126),
        1,
    )

    # Selector de Carga Inicial
    load_lbl = fonts.mono.render("CARGA INICIAL (BOIDS)", True, THEME.text_secondary)
    surface.blit(load_lbl, (inner_x, card_rect.y + 144))

    _draw_option_button(
        surface,
        layout.btn_1000,
        "1,000",
        selected=cfg.entity_count == 1000,
        hovered=point_in_rect(mouse_pos, layout.btn_1000),
        accent=THEME.accent_cyan,
        fonts=fonts,
    )
    _draw_option_button(
        surface,
        layout.btn_3000,
        "3,000",
        selected=cfg.entity_count == 3000,
        hovered=point_in_rect(mouse_pos, layout.btn_3000),
        accent=THEME.accent_cyan,
        fonts=fonts,
    )
    _draw_option_button(
        surface,
        layout.btn_5000,
        "5,000",
        selected=cfg.entity_count == 5000,
        hovered=point_in_rect(mouse_pos, layout.btn_5000),
        accent=THEME.accent_cyan,
        fonts=fonts,
    )

    # Selector de Modo Inicial
    mode_lbl = fonts.mono.render("MODO INICIAL", True, THEME.text_secondary)
    surface.blit(mode_lbl, (inner_x, card_rect.y + 228))

    _draw_option_button(
        surface,
        layout.btn_sequential,
        "Secuencial",
        selected=state.mode is SimMode.SEQUENTIAL,
        hovered=point_in_rect(mouse_pos, layout.btn_sequential),
        accent=THEME.accent_sequential,
        fonts=fonts,
        dot_color=THEME.accent_sequential,
    )
    _draw_option_button(
        surface,
        layout.btn_parallel,
        "Paralelo",
        selected=state.mode is SimMode.PARALLEL,
        hovered=point_in_rect(mouse_pos, layout.btn_parallel),
        accent=THEME.accent_parallel,
        fonts=fonts,
        dot_color=THEME.accent_parallel,
    )

    # Botón Principal CTA
    start_rect = _to_pygame_rect(layout.btn_start)
    start_hovered = point_in_rect(mouse_pos, layout.btn_start)
    cta_color = (182, 238, 178) if start_hovered else THEME.accent_parallel
    pygame.draw.rect(surface, cta_color, start_rect, border_radius=7)
    cta_text = fonts.heading.render("INICIAR SIMULACIÓN  >", True, THEME.text_dark)
    surface.blit(
        cta_text,
        (start_rect.centerx - cta_text.get_width() // 2, start_rect.centery - cta_text.get_height() // 2),
    )

    # Pie informativo real dentro de la tarjeta
    footer_y = card_rect.y + 394
    pygame.draw.line(surface, THEME.border, (inner_x, footer_y), (inner_right, footer_y), 1)

    cores_lbl = fonts.mono.render("Núcleos lógicos detectados:", True, THEME.text_secondary)
    surface.blit(cores_lbl, (inner_x, footer_y + 20))

    badge_x = inner_x + cores_lbl.get_width() + 10
    badge_text = fonts.mono.render(str(state.metrics.cpu_count), True, THEME.text_primary)
    badge_rect = pygame.Rect(badge_x, footer_y + 16, max(28, badge_text.get_width() + 14), 24)
    pygame.draw.rect(surface, THEME.button_bg, badge_rect, border_radius=4)
    pygame.draw.rect(surface, THEME.border, badge_rect, width=1, border_radius=4)
    surface.blit(
        badge_text,
        (badge_rect.centerx - badge_text.get_width() // 2, badge_rect.centery - badge_text.get_height() // 2),
    )

    ready_text = fonts.mono.render(
        f"• Listo ({state.workers} workers)",
        True,
        THEME.accent_parallel,
    )
    surface.blit(ready_text, (inner_right - ready_text.get_width(), footer_y + 20))

    # Barra de estado inferior con datos reales del entorno Python
    bar_rect = _to_pygame_rect(layout.status_bar)
    pygame.draw.rect(surface, THEME.panel_bg, bar_rect)
    pygame.draw.line(
        surface,
        THEME.border,
        (0, bar_rect.y),
        (cfg.window_width, bar_rect.y),
        1,
    )
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    left_status = fonts.mono.render(
        f"ESTADO: LISTO  |  LIENZO {cfg.world_width}x{cfg.world_height} + PANEL {cfg.panel_width}px",
        True,
        THEME.text_secondary,
    )
    right_status = fonts.mono.render(
        f"RUNTIME: PYTHON {py_ver} + MULTIPROCESSING",
        True,
        THEME.text_secondary,
    )
    surface.blit(left_status, (16, bar_rect.y + 8))
    surface.blit(right_status, (cfg.window_width - right_status.get_width() - 16, bar_rect.y + 8))
