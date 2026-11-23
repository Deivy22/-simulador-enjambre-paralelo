"""Paleta pastel oscura inmutable y carga controlada de fuentes para Pygame."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, TypeAlias

import pygame

ColorRGB: TypeAlias = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class ThemePalette:
    """Paleta de colores pastel de alto contraste (tema oscuro limpio)."""

    canvas_bg: ColorRGB = (30, 30, 46)          # #1E1E2E
    panel_bg: ColorRGB = (24, 24, 37)           # #181825
    card_bg: ColorRGB = (24, 24, 37)            # #181825
    button_bg: ColorRGB = (30, 32, 48)          # #1E2030
    button_hover: ColorRGB = (42, 45, 66)       # #2A2D42
    border: ColorRGB = (49, 50, 68)             # #313244
    dot_grid: ColorRGB = (42, 44, 62)           # #2A2C3E
    text_primary: ColorRGB = (205, 214, 244)    # #CDD6F4
    text_secondary: ColorRGB = (166, 173, 200)  # #A6ADC8
    text_dark: ColorRGB = (17, 17, 27)          # #11111B
    boid_cyan: ColorRGB = (137, 220, 235)       # #89DCEB
    boid_mint: ColorRGB = (166, 227, 161)       # #A6E3A1
    accent_parallel: ColorRGB = (166, 227, 161) # #A6E3A1
    accent_sequential: ColorRGB = (250, 179, 135)  # #FAB387
    accent_cyan: ColorRGB = (137, 220, 235)     # #89DCEB
    cursor_attract: ColorRGB = (250, 179, 135)  # #FAB387
    cursor_repel: ColorRGB = (243, 139, 168)    # #F38BA8
    badge_paused: ColorRGB = (249, 226, 175)    # #F9E2AF


THEME: Final[ThemePalette] = ThemePalette()


@dataclass(frozen=True, slots=True)
class UiFonts:
    """Conjunto inmutable de fuentes pre-cargadas una sola vez al iniciar Pygame."""

    title: pygame.font.Font
    heading: pygame.font.Font
    body: pygame.font.Font
    body_bold: pygame.font.Font
    small: pygame.font.Font
    mono: pygame.font.Font
    mono_large: pygame.font.Font


def load_ui_fonts() -> UiFonts:
    """Inicializa y retorna el paquete congelado de fuentes limpias del sistema."""
    sans_candidates = "segoeui,inter,arial,dejavusans"
    mono_candidates = "consolas,cascadiamono,couriernew,dejavusansmono"
    return UiFonts(
        title=pygame.font.SysFont(sans_candidates, 28, bold=True),
        heading=pygame.font.SysFont(sans_candidates, 16, bold=True),
        body=pygame.font.SysFont(sans_candidates, 15, bold=False),
        body_bold=pygame.font.SysFont(sans_candidates, 15, bold=True),
        small=pygame.font.SysFont(sans_candidates, 12, bold=False),
        mono=pygame.font.SysFont(mono_candidates, 13, bold=False),
        mono_large=pygame.font.SysFont(mono_candidates, 18, bold=True),
    )
