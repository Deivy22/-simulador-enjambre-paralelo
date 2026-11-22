"""Integrador puro de fuerzas ponderadas hacia un nuevo Boid congelado."""

from __future__ import annotations

from collections.abc import Sequence
import math

from core.math_utils import NORM_EPSILON_SQ, clamp_speed
from core.physics.environment import (
    clamp_position_and_velocity,
    compute_boundary_force,
    compute_mouse_force,
)
from core.physics.flocking import compute_flocking_forces
from data.config import SimConfig
from data.entities import Boid
from data.input_state import InputState, resolve_mouse_action
from data.types import FlatBoidTuple, MouseAction, SpatialGrid


def integrate_boid(
    boid: Boid,
    neighbors: tuple[Boid, ...],
    input_state: InputState,
    config: SimConfig,
    dt: float,
) -> Boid:
    """Calcula la nueva posición y velocidad de un Boid sin mutar el original."""
    sep, ali, coh = compute_flocking_forces(boid, neighbors, config)
    mouse_f = compute_mouse_force(boid, input_state, config)
    border_f = compute_boundary_force(boid, config)

    total_fx = (
        sep[0] * config.weight_separation
        + ali[0] * config.weight_alignment
        + coh[0] * config.weight_cohesion
        + mouse_f[0] * config.weight_mouse
        + border_f[0]
    )
    total_fy = (
        sep[1] * config.weight_separation
        + ali[1] * config.weight_alignment
        + coh[1] * config.weight_cohesion
        + mouse_f[1] * config.weight_mouse
        + border_f[1]
    )

    raw_vel = (boid.vx + total_fx * dt, boid.vy + total_fy * dt)
    clamped_vel = clamp_speed(
        velocity=raw_vel,
        min_speed=config.min_speed,
        max_speed=config.max_speed,
        fallback_dir=(boid.vx, boid.vy),
    )

    raw_pos = (boid.x + clamped_vel[0] * dt, boid.y + clamped_vel[1] * dt)
    final_pos, final_vel = clamp_position_and_velocity(raw_pos, clamped_vel, config)

    return Boid(
        x=final_pos[0],
        y=final_pos[1],
        vx=final_vel[0],
        vy=final_vel[1],
    )


def integrate_boid_from_flat(
    idx: int,
    xs: Sequence[float] | memoryview,
    ys: Sequence[float] | memoryview,
    vxs: Sequence[float] | memoryview,
    vys: Sequence[float] | memoryview,
    cells: SpatialGrid,
    cols: int,
    rows: int,
    inv_cell_size: float,
    input_state: InputState,
    config: SimConfig,
    dt: float,
) -> FlatBoidTuple:
    """Evaluador puro de una sola pasada sobre vistas planas de solo lectura (equivalente exacto).

    Elimina instanciaciones temporales de Boid y tuplas intermedias dentro del bucle 3×3,
    compartiendo exactamente la misma lógica matemática entre los modos Secuencial y Paralelo.
    """
    bx = xs[idx]
    by = ys[idx]
    bvx = vxs[idx]
    bvy = vys[idx]

    # Coordenadas de celda en la Grilla Espacial Inmutable
    cx = int(bx * inv_cell_size)
    cy = int(by * inv_cell_size)
    if cx < 0:
        cx = 0
    elif cx >= cols:
        cx = cols - 1
    if cy < 0:
        cy = 0
    elif cy >= rows:
        cy = rows - 1

    min_cx = 0 if cx == 0 else cx - 1
    max_cx = cols - 1 if cx >= cols - 1 else cx + 1
    min_cy = 0 if cy == 0 else cy - 1
    max_cy = rows - 1 if cy >= rows - 1 else cy + 1

    perc_r = config.perception_radius
    perc_r_sq = perc_r * perc_r
    sep_r = config.separation_radius
    sep_r_sq = sep_r * sep_r
    eps_sq = config.separation_epsilon * config.separation_epsilon

    sep_x = 0.0
    sep_y = 0.0
    sum_vx = 0.0
    sum_vy = 0.0
    sum_x = 0.0
    sum_y = 0.0
    perc_count = 0

    for gy in range(min_cy, max_cy + 1):
        row_offset = gy * cols
        for gx in range(min_cx, max_cx + 1):
            for j in cells[row_offset + gx]:
                if j == idx:
                    continue
                dx = bx - xs[j]
                dy = by - ys[j]
                d_sq = dx * dx + dy * dy
                if d_sq < perc_r_sq:
                    perc_count += 1
                    sum_vx += vxs[j]
                    sum_vy += vys[j]
                    sum_x += xs[j]
                    sum_y += ys[j]
                    if d_sq < sep_r_sq:
                        denom = d_sq if d_sq > eps_sq else eps_sq
                        factor = sep_r_sq / denom
                        sep_x += dx * factor
                        sep_y += dy * factor

    if perc_count > 0:
        inv_count = 1.0 / perc_count
        ali_x = sum_vx * inv_count - bvx
        ali_y = sum_vy * inv_count - bvy
        coh_x = sum_x * inv_count - bx
        coh_y = sum_y * inv_count - by
    else:
        ali_x = 0.0
        ali_y = 0.0
        coh_x = 0.0
        coh_y = 0.0

    # Interacción progresiva con el cursor (solo dentro del Canvas)
    mouse_fx = 0.0
    mouse_fy = 0.0
    if input_state.mouse_in_canvas:
        action = (
            input_state.mouse_action
            if input_state.mouse_action is not MouseAction.NONE
            else resolve_mouse_action(
                input_state.left_click,
                input_state.right_click,
                input_state.mouse_in_canvas,
            )
        )
        if action is not MouseAction.NONE:
            mdx = input_state.mouse_pos[0] - bx
            mdy = input_state.mouse_pos[1] - by
            md_sq = mdx * mdx + mdy * mdy
            mouse_r = config.mouse_radius
            if eps_sq < md_sq < mouse_r * mouse_r:
                mdist = math.sqrt(md_sq)
                sign = 1.0 if action is MouseAction.ATTRACT else -1.0
                mag = sign * (1.0 - (mdist / mouse_r)) * config.mouse_strength / mdist
                mouse_fx = mdx * mag
                mouse_fy = mdy * mag

    # Límites suaves (soft boundaries)
    border_fx = 0.0
    border_fy = 0.0
    margin = config.margin
    if margin > 0.0:
        turn = config.turn_factor
        inv_margin = 1.0 / margin
        right_limit = float(config.world_width) - margin
        bottom_limit = float(config.world_height) - margin
        if bx < margin:
            border_fx = turn * ((margin - bx) * inv_margin)
        elif bx > right_limit:
            border_fx = -turn * ((bx - right_limit) * inv_margin)
        if by < margin:
            border_fy = turn * ((margin - by) * inv_margin)
        elif by > bottom_limit:
            border_fy = -turn * ((by - bottom_limit) * inv_margin)

    total_fx = (
        sep_x * config.weight_separation
        + ali_x * config.weight_alignment
        + coh_x * config.weight_cohesion
        + mouse_fx * config.weight_mouse
        + border_fx
    )
    total_fy = (
        sep_y * config.weight_separation
        + ali_y * config.weight_alignment
        + coh_y * config.weight_cohesion
        + mouse_fy * config.weight_mouse
        + border_fy
    )

    nvx = bvx + total_fx * dt
    nvy = bvy + total_fy * dt

    # Acotado de velocidad con protección de norma cero
    min_speed = config.min_speed
    max_speed = config.max_speed
    speed_sq = nvx * nvx + nvy * nvy
    if speed_sq < NORM_EPSILON_SQ:
        fb_sq = bvx * bvx + bvy * bvy
        if fb_sq >= NORM_EPSILON_SQ:
            fb_scale = min_speed / math.sqrt(fb_sq)
            nvx = bvx * fb_scale
            nvy = bvy * fb_scale
        else:
            nvx = min_speed
            nvy = 0.0
    elif speed_sq < min_speed * min_speed:
        scale = min_speed / math.sqrt(speed_sq)
        nvx *= scale
        nvy *= scale
    elif speed_sq > max_speed * max_speed:
        scale = max_speed / math.sqrt(speed_sq)
        nvx *= scale
        nvy *= scale

    # Integración de posición + respaldo hard clamp
    nx = bx + nvx * dt
    ny = by + nvy * dt
    max_x = float(config.world_width)
    max_y = float(config.world_height)
    if nx < 0.0:
        nx = 0.0
        nvx = abs(nvx)
    elif nx > max_x:
        nx = max_x
        nvx = -abs(nvx)
    if ny < 0.0:
        ny = 0.0
        nvy = abs(nvy)
    elif ny > max_y:
        ny = max_y
        nvy = -abs(nvy)

    return (nx, ny, nvx, nvy)
