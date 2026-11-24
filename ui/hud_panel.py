"""Renderizado solo-lectura del Panel Lateral HUD (Zona Derecha 320×720)."""

from __future__ import annotations

import pygame

from data.game_state import GameState
from data.types import SimMode
from ui.layout import SimulationLayout, point_in_rect
from ui.theme import THEME, ColorRGB, UiFonts

SHORTCUTS: tuple[tuple[str, str], ...] = (
    ("1 / 3 / 5", "Carga 1k / 3k / 5k"),
    ("M", "Secuencial / Paralelo"),
    ("+ / -", "Ajustar workers"),
    ("Clic Izq", "Atractor en lienzo"),
    ("Clic Der", "Repulsor en lienzo"),
    ("R", "Reiniciar semilla"),
    ("Espacio", "Pausar / Reanudar"),
    ("Backspace", "Volver al Menú"),
    ("ESC", "Salir limpio"),
)


def _draw_metric_row(
    surface: pygame.Surface,
    x: int,
    right_x: int,
    y: int,
    label: str,
    value: str,
    value_color: ColorRGB,
    fonts: UiFonts,
) -> None:
    """Dibuja una fila alineada de telemetría (etiqueta izquierda, valor derecha)."""
    lbl_surf = fonts.body.render(label, True, THEME.text_secondary)
    val_surf = fonts.mono_large.render(value, True, value_color)
    surface.blit(lbl_surf, (x, y + 2))
    surface.blit(val_surf, (right_x - val_surf.get_width(), y))


def render_hud_panel(
    surface: pygame.Surface,
    state: GameState,
    layout: SimulationLayout,
    fonts: UiFonts,
) -> None:
    """Dibuja el Panel Lateral fijo derecho en 3 bloques limpios + botón discreto Menú."""
    panel = layout.panel
    panel_rect = pygame.Rect(panel.x, panel.y, panel.width, panel.height)
    surface.fill(THEME.panel_bg, panel_rect)

    # Línea separadora de 1px entre Canvas y Panel Lateral
    pygame.draw.line(
        surface,
        THEME.border,
        (layout.divider_x, 0),
        (layout.divider_x, panel.height),
        1,
    )

    x = panel.x + 20
    right_x = panel.x + panel.width - 20
    inner_w = right_x - x

    # ================= BLOQUE 1: MODO Y ENTIDADES =================
    y = 20
    sec1_lbl = fonts.mono.render("MODO DE EJECUCIÓN", True, THEME.text_secondary)
    surface.blit(sec1_lbl, (x, y))
    y += 24

    is_parallel = state.mode is SimMode.PARALLEL
    mode_accent = THEME.accent_parallel if is_parallel else THEME.accent_sequential
    mode_text = (
        f"PARALELO ({state.workers} workers)"
        if is_parallel
        else "SECUENCIAL (1 núcleo)"
    )

    badge_rect = pygame.Rect(x, y, inner_w, 36)
    pygame.draw.rect(surface, THEME.button_bg, badge_rect, border_radius=6)
    pygame.draw.rect(surface, mode_accent, badge_rect, width=1, border_radius=6)
    pygame.draw.circle(surface, mode_accent, (x + 14, badge_rect.centery), 4)
    mode_surf = fonts.body_bold.render(mode_text, True, mode_accent)
    surface.blit(mode_surf, (x + 26, badge_rect.centery - mode_surf.get_height() // 2))
    y += 50

    _draw_metric_row(
        surface,
        x,
        right_x,
        y,
        "Entidades activas",
        f"{len(state.boids):,}",
        THEME.accent_cyan,
        fonts,
    )
    y += 32

    status_val = "PAUSADO" if state.paused else "ACTIVO"
    status_color = THEME.badge_paused if state.paused else THEME.accent_parallel
    _draw_metric_row(surface, x, right_x, y, "Estado", status_val, status_color, fonts)
    y += 38

    pygame.draw.line(surface, THEME.border, (x, y), (right_x, y), 1)
    y += 18

    # ================= BLOQUE 2: TELEMETRÍA EN VIVO =================
    sec2_lbl = fonts.mono.render("TELEMETRÍA EN VIVO", True, THEME.text_secondary)
    surface.blit(sec2_lbl, (x, y))
    y += 26

    m = state.metrics
    _draw_metric_row(
        surface,
        x,
        right_x,
        y,
        "FPS instantáneos",
        f"{m.instant_fps:5.1f}",
        THEME.text_primary,
        fonts,
    )
    y += 30

    _draw_metric_row(
        surface,
        x,
        right_x,
        y,
        "FPS promedio (60f)",
        f"{m.average_fps:5.1f}",
        THEME.accent_parallel if m.average_fps >= 30.0 else THEME.accent_sequential,
        fonts,
    )
    y += 30

    _draw_metric_row(
        surface,
        x,
        right_x,
        y,
        "Física exclusiva",
        f"{m.physics_ms:5.2f} ms",
        THEME.accent_cyan,
        fonts,
    )
    y += 30

    _draw_metric_row(
        surface,
        x,
        right_x,
        y,
        "Frame total",
        f"{m.frame_ms:5.2f} ms",
        THEME.text_secondary,
        fonts,
    )
    y += 32

    effective_workers = state.workers if is_parallel else 1
    _draw_metric_row(
        surface,
        x,
        right_x,
        y,
        "Workers / Núcleos",
        f"{effective_workers} / {m.cpu_count}",
        mode_accent,
        fonts,
    )
    y += 30

    # Barra de utilización de núcleos
    bar_rect = pygame.Rect(x, y, inner_w, 8)
    pygame.draw.rect(surface, THEME.button_bg, bar_rect, border_radius=4)
    ratio = min(1.0, effective_workers / max(1, m.cpu_count))
    fill_w = max(4, int(inner_w * ratio))
    pygame.draw.rect(surface, mode_accent, pygame.Rect(x, y, fill_w, 8), border_radius=4)
    y += 24

    pygame.draw.line(surface, THEME.border, (x, y), (right_x, y), 1)
    y += 16

    # ================= BLOQUE 3: ATAJOS =================
    sec3_lbl = fonts.mono.render("ATAJOS", True, THEME.text_secondary)
    surface.blit(sec3_lbl, (x, y))
    y += 22

    for key_label, desc in SHORTCUTS:
        key_surf = fonts.mono.render(key_label, True, THEME.text_primary)
        key_box = pygame.Rect(x, y, 82, 20)
        pygame.draw.rect(surface, THEME.button_bg, key_box, border_radius=4)
        pygame.draw.rect(surface, THEME.border, key_box, width=1, border_radius=4)
        surface.blit(
            key_surf,
            (key_box.centerx - key_surf.get_width() // 2, key_box.centery - key_surf.get_height() // 2),
        )
        desc_surf = fonts.small.render(desc, True, THEME.text_secondary)
        surface.blit(desc_surf, (x + 92, y + 3))
        y += 24

    # ================= BOTÓN DISCRETO MENÚ =================
    menu_box = layout.btn_menu
    menu_rect = pygame.Rect(menu_box.x, menu_box.y, menu_box.width, menu_box.height)
    hovered = point_in_rect(state.input_state.mouse_pos, menu_box)
    pygame.draw.rect(
        surface,
        THEME.button_hover if hovered else THEME.button_bg,
        menu_rect,
        border_radius=6,
    )
    pygame.draw.rect(
        surface,
        THEME.accent_cyan if hovered else THEME.border,
        menu_rect,
        width=1,
        border_radius=6,
    )
    menu_text = fonts.body_bold.render("<  Menú  (Backspace)", True, THEME.text_primary)
    surface.blit(
        menu_text,
        (menu_rect.centerx - menu_text.get_width() // 2, menu_rect.centery - menu_text.get_height() // 2),
    )
