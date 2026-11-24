"""Pruebas unitarias de utilidades matemáticas, física pura, grilla espacial y motor secuencial."""

from __future__ import annotations

import math
import pytest

from core.engine import (
    build_spatial_grid,
    query_neighbor_indices,
    step_boids_sequential,
    update_sequential,
)
from core.math_utils import (
    ZERO_VEC,
    clamp_scalar,
    clamp_speed,
    dist,
    dist_sq,
    vec_add,
    vec_div,
    vec_dot,
    vec_limit,
    vec_mag,
    vec_mag_sq,
    vec_normalize,
    vec_scale,
    vec_sub,
    vec_unit_or_default,
)
from core.physics import (
    clamp_position_and_velocity,
    compute_alignment,
    compute_boundary_force,
    compute_cohesion,
    compute_flocking_forces,
    compute_mouse_force,
    compute_separation,
)
from core.state import create_initial_state, spawn_boids
from data import Boid, InputState, MouseAction, ScreenMode, SimConfig, SimMode


def test_vector_arithmetic_is_pure() -> None:
    a = (3.0, -4.0)
    b = (1.5, 2.5)
    assert vec_add(a, b) == (4.5, -1.5)
    assert vec_sub(a, b) == (1.5, -6.5)
    assert vec_scale(a, 2.0) == (6.0, -8.0)
    assert vec_div((6.0, -8.0), 2.0) == (3.0, -4.0)
    assert vec_dot((2.0, 3.0), (4.0, -1.0)) == 5.0
    with pytest.raises(ValueError):
        vec_div(a, 0.0)


def test_magnitudes_and_distances() -> None:
    assert vec_mag_sq((3.0, 4.0)) == 25.0
    assert vec_mag((3.0, 4.0)) == pytest.approx(5.0)
    assert dist_sq((1.0, 2.0), (4.0, 6.0)) == 25.0
    assert dist((1.0, 2.0), (4.0, 6.0)) == pytest.approx(5.0)


def test_normalize_limit_and_clamp_scalar() -> None:
    ux, uy = vec_normalize((3.0, 4.0))
    assert ux == pytest.approx(0.6)
    assert uy == pytest.approx(0.8)
    assert vec_normalize((0.0, 0.0)) == ZERO_VEC

    assert vec_unit_or_default((0.0, 0.0), (0.0, 5.0)) == pytest.approx((0.0, 1.0))
    assert vec_unit_or_default((0.0, 0.0), (0.0, 0.0)) == (1.0, 0.0)

    limited = vec_limit((30.0, 40.0), 10.0)
    assert math.hypot(*limited) == pytest.approx(10.0)
    assert vec_limit((3.0, 4.0), 10.0) == (3.0, 4.0)

    assert clamp_scalar(-5.0, 0.0, 10.0) == 0.0
    assert clamp_scalar(5.0, 0.0, 10.0) == 5.0
    assert clamp_scalar(15.0, 0.0, 10.0) == 10.0


def test_clamp_speed_enforces_bounds_and_protects_zero_norm() -> None:
    slow = clamp_speed((3.0, 4.0), min_speed=90.0, max_speed=220.0)
    assert math.hypot(*slow) == pytest.approx(90.0)
    assert slow[0] == pytest.approx(54.0)
    assert slow[1] == pytest.approx(72.0)

    fast = clamp_speed((300.0, 400.0), min_speed=90.0, max_speed=220.0)
    assert math.hypot(*fast) == pytest.approx(220.0)

    mid = clamp_speed((100.0, 100.0), min_speed=90.0, max_speed=220.0)
    assert mid == (100.0, 100.0)

    zero_protected = clamp_speed(
        (0.0, 0.0),
        min_speed=90.0,
        max_speed=220.0,
        fallback_dir=(0.0, -3.0),
    )
    assert zero_protected == pytest.approx((0.0, -90.0))


def test_separation_repels_close_neighbors_and_protects_overlap() -> None:
    cfg = SimConfig()
    center = Boid(x=100.0, y=100.0, vx=100.0, vy=0.0)
    close_right = Boid(x=110.0, y=100.0, vx=100.0, vy=0.0)
    far = Boid(x=200.0, y=100.0, vx=100.0, vy=0.0)

    fx, fy = compute_separation(center, (close_right, far), cfg)
    assert fx < 0.0
    assert fy == pytest.approx(0.0)
    expected_fx = (-10.0) * (cfg.separation_radius ** 2 / 100.0)
    assert fx == pytest.approx(expected_fx)

    overlapping = Boid(x=100.0, y=100.0, vx=-50.0, vy=50.0)
    ox, oy = compute_separation(center, (overlapping,), cfg)
    assert math.isfinite(ox) and math.isfinite(oy)
    assert (ox, oy) == ZERO_VEC


def test_alignment_cohesion_and_combined_flocking_match() -> None:
    cfg = SimConfig()
    b = Boid(x=200.0, y=200.0, vx=100.0, vy=0.0)
    n1 = Boid(x=210.0, y=200.0, vx=140.0, vy=20.0)
    n2 = Boid(x=220.0, y=220.0, vx=120.0, vy=40.0)
    outside = Boid(x=400.0, y=400.0, vx=-200.0, vy=-200.0)
    neighbors = (n1, n2, outside)

    ali = compute_alignment(b, neighbors, cfg)
    coh = compute_cohesion(b, neighbors, cfg)
    sep = compute_separation(b, neighbors, cfg)

    assert ali == pytest.approx((30.0, 30.0))
    assert coh == pytest.approx((15.0, 10.0))

    c_sep, c_ali, c_coh = compute_flocking_forces(b, neighbors, cfg)
    assert c_sep == pytest.approx(sep)
    assert c_ali == pytest.approx(ali)
    assert c_coh == pytest.approx(coh)


def test_soft_boundaries_and_hard_clamp() -> None:
    cfg = SimConfig()
    near_left_top = Boid(x=30.0, y=15.0, vx=-100.0, vy=-100.0)
    fx, fy = compute_boundary_force(near_left_top, cfg)
    assert fx == pytest.approx(cfg.turn_factor * 0.5)
    assert fy == pytest.approx(cfg.turn_factor * 0.75)

    near_right_bottom = Boid(x=930.0, y=705.0, vx=100.0, vy=100.0)
    fx2, fy2 = compute_boundary_force(near_right_bottom, cfg)
    assert fx2 == pytest.approx(-cfg.turn_factor * 0.5)
    assert fy2 == pytest.approx(-cfg.turn_factor * 0.75)

    center = Boid(x=480.0, y=360.0, vx=100.0, vy=0.0)
    assert compute_boundary_force(center, cfg) == ZERO_VEC

    pos, vel = clamp_position_and_velocity((-5.0, 750.0), (-120.0, 80.0), cfg)
    assert pos == (0.0, float(cfg.world_height))
    assert vel == (120.0, -80.0)


def test_mouse_force_attraction_repulsion_precedence_and_canvas_clip() -> None:
    cfg = SimConfig()
    b = Boid(x=200.0, y=200.0, vx=100.0, vy=0.0)

    attract_inp = InputState(
        mouse_pos=(275.0, 200.0),
        mouse_in_canvas=True,
        left_click=True,
        mouse_action=MouseAction.ATTRACT,
    )
    afx, afy = compute_mouse_force(b, attract_inp, cfg)
    assert afx == pytest.approx(0.5 * cfg.mouse_strength)
    assert afy == pytest.approx(0.0)

    repel_inp = InputState(
        mouse_pos=(275.0, 200.0),
        mouse_in_canvas=True,
        left_click=True,
        right_click=True,
        mouse_action=MouseAction.NONE,
    )
    rfx, rfy = compute_mouse_force(b, repel_inp, cfg)
    assert rfx == pytest.approx(-0.5 * cfg.mouse_strength)
    assert rfy == pytest.approx(0.0)

    outside_canvas = InputState(
        mouse_pos=(1100.0, 200.0),
        mouse_in_canvas=False,
        left_click=True,
        mouse_action=MouseAction.ATTRACT,
    )
    assert compute_mouse_force(b, outside_canvas, cfg) == ZERO_VEC


def test_spatial_grid_matches_exact_bruteforce_neighborhood() -> None:
    cfg = SimConfig(entity_count=120)
    boids = spawn_boids(cfg.entity_count, cfg, seed=123)
    grid = build_spatial_grid(boids, cfg.world_width, cfg.world_height, cfg.perception_radius)
    perc_r_sq = cfg.perception_radius ** 2

    for idx, b in enumerate(boids):
        brute = {
            j
            for j, other in enumerate(boids)
            if j != idx and dist_sq((b.x, b.y), (other.x, other.y)) < perc_r_sq
        }
        grid_candidates = query_neighbor_indices(grid, b.x, b.y, exclude_index=idx)
        grid_filtered = {
            j
            for j in grid_candidates
            if dist_sq((b.x, b.y), (boids[j].x, boids[j].y)) < perc_r_sq
        }
        assert grid_filtered == brute


def test_update_sequential_moves_boids_preserves_invariants_and_is_deterministic() -> None:
    cfg = SimConfig(entity_count=80)
    state_a = create_initial_state(
        config=cfg,
        seed=99,
        screen=ScreenMode.SIMULATION,
        mode=SimMode.SEQUENTIAL,
    )
    state_b = create_initial_state(
        config=cfg,
        seed=99,
        screen=ScreenMode.SIMULATION,
        mode=SimMode.SEQUENTIAL,
    )
    snapshot_before = state_a.boids
    idle_input = InputState()

    next_a = update_sequential(state_a, idle_input, dt=cfg.fixed_dt)
    next_b = update_sequential(state_b, idle_input, dt=cfg.fixed_dt)

    assert state_a.frame == 0
    assert state_a.boids == snapshot_before
    assert next_a.frame == 1
    assert next_a.boids == next_b.boids
    assert next_a.boids != snapshot_before

    for boid in next_a.boids:
        speed = math.hypot(boid.vx, boid.vy)
        assert cfg.min_speed - 1e-6 <= speed <= cfg.max_speed + 1e-6
        assert 0.0 <= boid.x <= cfg.world_width
        assert 0.0 <= boid.y <= cfg.world_height

    direct_boids = step_boids_sequential(state_a.boids, idle_input, cfg, cfg.fixed_dt)
    assert direct_boids == next_a.boids
