"""Orquestador imperativo (Game Loop, máquina de 2 pantallas y ciclo de vida del Pool)."""

from __future__ import annotations

from dataclasses import replace
import time

import pygame

from core.engine import step_boids_sequential
from core.parallel import (
    PoolHandle,
    close_pool_handle,
    ensure_pool_workers,
    step_boids_parallel,
)
from core.state import (
    apply_input_transitions,
    clamp_interactive_dt,
    create_initial_state,
    measure_execution_ms,
    update_metrics_snapshot,
)
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
    """Inicia Pygame, ejecuta el Game Loop en 2 pantallas y garantiza cierre limpio del Pool."""
    state: GameState = create_initial_state(
        config=config,
        seed=seed,
        screen=ScreenMode.START,
        mode=SimMode.PARALLEL,
    )
    cfg = state.config
    start_layout = build_start_layout(cfg)
    sim_layout = build_simulation_layout(cfg)
    pool_handle = PoolHandle(pool=None, workers=state.workers)

    pygame.init()
    try:
        pygame.display.set_caption("Simulador de Enjambre 2D — Boids Paralelo")
        surface = pygame.display.set_mode((cfg.window_width, cfg.window_height))
        fonts = load_ui_fonts()
        clock = pygame.time.Clock()
        prev_frame_time = time.perf_counter()

        running = True
        while running:
            now = time.perf_counter()
            raw_dt = now - prev_frame_time
            prev_frame_time = now
            dt = clamp_interactive_dt(raw_dt, state.config)

            # 1. Captura de entradas inmutable
            input_state = collect_pygame_input(
                screen=state.screen,
                config=state.config,
                start_layout=start_layout,
                sim_layout=sim_layout,
            )
            if input_state.quit_requested:
                running = False
                break

            # 2. Transiciones puras de estado (Inicio <-> Simulación, 1/3/5, M, +/-, R, Espacio)
            state = apply_input_transitions(state, input_state)

            # 3. Sincronización del Pool persistente (solo activo en Simulación + Modo Paralelo)
            need_pool = (
                state.screen is ScreenMode.SIMULATION
                and state.mode is SimMode.PARALLEL
            )
            pool_handle = ensure_pool_workers(
                pool_handle,
                desired_workers=state.workers,
                active=need_pool,
                cpu_count=state.metrics.cpu_count,
            )

            # 4. Avance del motor físico (puro) midiendo tiempo exclusivo physics_ms
            physics_ms = 0.0
            if state.screen is ScreenMode.SIMULATION and not state.paused:
                if state.mode is SimMode.PARALLEL and pool_handle.pool is not None:
                    next_boids, physics_ms = measure_execution_ms(
                        step_boids_parallel,
                        state.boids,
                        input_state,
                        state.config,
                        dt,
                        pool_handle.pool,
                        state.workers,
                    )
                else:
                    next_boids, physics_ms = measure_execution_ms(
                        step_boids_sequential,
                        state.boids,
                        input_state,
                        state.config,
                        dt,
                    )
                state = replace(
                    state,
                    boids=next_boids,
                    frame=state.frame + 1,
                )

            # 5. Actualización pura de telemetría (ventana móvil de 60 frames)
            if state.screen is ScreenMode.SIMULATION:
                frame_ms = raw_dt * 1000.0
                next_metrics = update_metrics_snapshot(
                    prev=state.metrics,
                    physics_ms=physics_ms,
                    frame_ms=frame_ms,
                    window_size=state.config.fps_window_size,
                    active_workers=state.workers,
                )
                state = replace(state, metrics=next_metrics)

            # 6. Renderizado solo-lectura de la pantalla activa
            if state.screen is ScreenMode.START:
                render_start_screen(surface, state, start_layout, fonts)
            else:
                render_canvas(surface, state, sim_layout, fonts)
                render_hud_panel(surface, state, sim_layout, fonts)

            pygame.display.flip()
            clock.tick(target_fps)
    finally:
        # Cierre limpio garantizado ante ESC, cierre de ventana o excepción
        close_pool_handle(pool_handle)
        pygame.quit()
