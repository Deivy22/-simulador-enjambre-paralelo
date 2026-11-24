"""Bucle principal de presentación y máquina de estados de dos pantallas."""

from __future__ import annotations

import time

import pygame

from core.state import apply_input_transitions, clamp_interactive_dt, create_initial_state
from data.config import SimConfig
from data.game_state import GameState
from data.types import ScreenMode, SimMode
from ui.canvas_renderer import render_canvas
from ui.hud_panel import render_hud_panel
from ui.input_handler import collect_pygame_input
from ui.layout import build_simulation_layout, build_start_layout
from ui.start_screen import render_start_screen
from ui.theme import load_ui_fonts


def run_simulator(
    config: SimConfig | None = None,
    seed: int = 42,
    target_fps: int = 60,
) -> None:
    """Inicia el bucle Pygame de la Pantalla de Inicio y la Simulación."""
    state: GameState = create_initial_state(
        config=config,
        seed=seed,
        screen=ScreenMode.START,
        mode=SimMode.PARALLEL,
    )
    cfg = state.config
    start_layout = build_start_layout(cfg)
    sim_layout = build_simulation_layout(cfg)

    pygame.init()
    pygame.display.set_caption("Simulador de Enjambre 2D — Boids Paralelo")
    surface = pygame.display.set_mode((cfg.window_width, cfg.window_height))
    fonts = load_ui_fonts()
    clock = pygame.time.Clock()
    previous_time = time.perf_counter()
    running = True

    while running:
        now = time.perf_counter()
        dt = clamp_interactive_dt(now - previous_time, state.config)
        previous_time = now

        input_state = collect_pygame_input(
            screen=state.screen,
            config=state.config,
            start_layout=start_layout,
            sim_layout=sim_layout,
        )
        if input_state.quit_requested:
            running = False
            continue

        state = apply_input_transitions(state, input_state)
        if state.screen is ScreenMode.START:
            render_start_screen(surface, state, start_layout, fonts)
        else:
            render_canvas(surface, state, sim_layout, fonts)
            render_hud_panel(surface, state, sim_layout, fonts)

        pygame.display.flip()
        clock.tick(target_fps)

    pygame.quit()
