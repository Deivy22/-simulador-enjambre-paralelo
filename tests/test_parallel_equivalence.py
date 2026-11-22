"""Pruebas de particionamiento, ciclo de vida del Pool y equivalencia Secuencial == Paralelo."""

from __future__ import annotations

import pytest

from core.engine import build_spatial_grid, query_neighbors, update_sequential
from core.parallel import (
    PoolHandle,
    buffer_as_readonly_views,
    close_pool_handle,
    compute_chunk_ranges,
    detect_cpu_cores,
    ensure_pool_workers,
    managed_worker_pool,
    pack_boids_to_buffer,
    pack_boids_to_flat_tuples,
    pack_boids_to_snapshot,
    recommended_worker_count,
    unpack_buffer_to_boids,
    unpack_flat_tuples_to_boids,
    unpack_snapshot_to_boids,
    update_parallel,
    verify_chunk_partition,
)
from core.physics import integrate_boid, integrate_boid_from_flat
from core.state import create_initial_state, spawn_boids
from data import InputState, MouseAction, ScreenMode, SimConfig, SimMode


def test_partition_covers_all_indices_balanced_without_gaps_or_overlaps() -> None:
    assert compute_chunk_ranges(0, workers=4) == ()
    assert verify_chunk_partition((), 0) is True

    # División exacta
    exact = compute_chunk_ranges(1000, workers=4)
    assert exact == ((0, 250), (250, 500), (500, 750), (750, 1000))
    assert verify_chunk_partition(exact, 1000) is True

    # División con residuo distribuido (+1 en primeros chunks)
    uneven = compute_chunk_ranges(10, workers=4)
    assert uneven == ((0, 3), (3, 6), (6, 8), (8, 10))
    assert verify_chunk_partition(uneven, 10) is True

    # Más workers que entidades: nunca crea chunks vacíos
    small = compute_chunk_ranges(2, workers=8)
    assert small == ((0, 1), (1, 2))
    assert verify_chunk_partition(small, 2) is True

    assert detect_cpu_cores() >= 1
    assert recommended_worker_count(1) == 1
    assert recommended_worker_count(12) == 11

    with pytest.raises(ValueError):
        compute_chunk_ranges(-1, workers=2)
    with pytest.raises(ValueError):
        compute_chunk_ranges(10, workers=0)


def test_ipc_codec_roundtrip_preserves_exact_boids_immutably() -> None:
    cfg = SimConfig(entity_count=40)
    boids = spawn_boids(cfg.entity_count, cfg, seed=11)

    flat = pack_boids_to_flat_tuples(boids)
    assert isinstance(flat, tuple)
    assert unpack_flat_tuples_to_boids(flat) == boids

    snapshot = pack_boids_to_snapshot(boids)
    assert unpack_snapshot_to_boids(snapshot) == boids

    buf = pack_boids_to_buffer(boids)
    assert unpack_buffer_to_boids(buf) == boids
    xs_v, ys_v, vxs_v, vys_v = buffer_as_readonly_views(buf)
    assert xs_v.readonly and ys_v.readonly and vxs_v.readonly and vys_v.readonly
    with pytest.raises(TypeError):
        xs_v[0] = 999.0  # type: ignore[index]


def test_optimized_flat_integrator_matches_reference_integrate_boid() -> None:
    cfg = SimConfig(entity_count=60)
    boids = spawn_boids(cfg.entity_count, cfg, seed=77)
    grid = build_spatial_grid(boids, cfg.world_width, cfg.world_height, cfg.perception_radius)
    buf = pack_boids_to_buffer(boids)
    xs, ys, vxs, vys = buffer_as_readonly_views(buf)
    inp = InputState(
        mouse_pos=(350.0, 280.0),
        mouse_in_canvas=True,
        left_click=True,
        mouse_action=MouseAction.ATTRACT,
    )
    inv_cell = 1.0 / grid.cell_size

    for idx, boid in enumerate(boids):
        ref = integrate_boid(boid, query_neighbors(boids, grid, idx), inp, cfg, cfg.fixed_dt)
        opt = integrate_boid_from_flat(
            idx=idx,
            xs=xs,
            ys=ys,
            vxs=vxs,
            vys=vys,
            cells=grid.cells,
            cols=grid.cols,
            rows=grid.rows,
            inv_cell_size=inv_cell,
            input_state=inp,
            config=cfg,
            dt=cfg.fixed_dt,
        )
        assert opt[0] == pytest.approx(ref.x, abs=1e-9)
        assert opt[1] == pytest.approx(ref.y, abs=1e-9)
        assert opt[2] == pytest.approx(ref.vx, abs=1e-9)
        assert opt[3] == pytest.approx(ref.vy, abs=1e-9)


def test_pool_lifecycle_reuse_resize_and_clean_close() -> None:
    handle = PoolHandle(pool=None, workers=1)

    # Desactivado no crea procesos
    inactive = ensure_pool_workers(handle, desired_workers=2, active=False, cpu_count=4)
    assert inactive.pool is None

    # Activar crea pool persistente y lo reutiliza si workers no cambia
    active_2 = ensure_pool_workers(inactive, desired_workers=2, active=True, cpu_count=4)
    try:
        assert active_2.pool is not None
        assert active_2.workers == 2

        reused = ensure_pool_workers(active_2, desired_workers=2, active=True, cpu_count=4)
        assert reused.pool is active_2.pool

        # Cambiar workers cierra el anterior y levanta uno nuevo
        resized = ensure_pool_workers(reused, desired_workers=3, active=True, cpu_count=4)
        active_2 = resized
        assert resized.pool is not None
        assert resized.workers == 3

        # Desactivar cierra limpiamente y retorna pool=None
        closed = ensure_pool_workers(resized, desired_workers=3, active=False, cpu_count=4)
        active_2 = closed
        assert closed.pool is None
        # Cierre idempotente
        assert close_pool_handle(closed).pool is None
    finally:
        close_pool_handle(active_2)


def test_parallel_matches_sequential_within_float_tolerance_across_frames() -> None:
    cfg = SimConfig(entity_count=120)
    dt = cfg.fixed_dt
    seq_state = create_initial_state(
        config=cfg,
        seed=2026,
        screen=ScreenMode.SIMULATION,
        mode=SimMode.SEQUENTIAL,
        workers=1,
    )
    par_state = create_initial_state(
        config=cfg,
        seed=2026,
        screen=ScreenMode.SIMULATION,
        mode=SimMode.PARALLEL,
        workers=2,
        cpu_count=4,
    )

    inputs = (
        InputState(),
        InputState(
            mouse_pos=(420.0, 310.0),
            mouse_in_canvas=True,
            left_click=True,
            mouse_action=MouseAction.ATTRACT,
        ),
        InputState(
            mouse_pos=(480.0, 360.0),
            mouse_in_canvas=True,
            right_click=True,
            mouse_action=MouseAction.REPEL,
        ),
    )

    initial_snapshot = par_state.boids
    with managed_worker_pool(workers=2, cpu_count=4) as handle:
        assert handle.pool is not None
        for step_input in inputs:
            seq_state = update_sequential(seq_state, step_input, dt=dt)
            par_state = update_parallel(par_state, step_input, dt=dt, pool=handle.pool)

    # Inmutabilidad del estado inicial y conteo de frames
    assert len(par_state.boids) == len(seq_state.boids) == 120
    assert par_state.boids != initial_snapshot
    assert par_state.frame == seq_state.frame == len(inputs)

    # Equivalencia matemática estricta (tolerancia 1e-9)
    for b_seq, b_par in zip(seq_state.boids, par_state.boids):
        assert b_par.x == pytest.approx(b_seq.x, abs=1e-9)
        assert b_par.y == pytest.approx(b_seq.y, abs=1e-9)
        assert b_par.vx == pytest.approx(b_seq.vx, abs=1e-9)
        assert b_par.vy == pytest.approx(b_seq.vy, abs=1e-9)
