"""Pruebas de particionamiento, IPC, ciclo de vida del Pool y equivalencia paralela."""

from __future__ import annotations

import pytest

from core.parallel.partition import (
    compute_chunk_ranges,
    detect_cpu_cores,
    recommended_worker_count,
    verify_chunk_partition,
)
from core.parallel.ipc_codec import (
    pack_boids_to_flat_tuples,
    pack_boids_to_snapshot,
    unpack_flat_tuples_to_boids,
    unpack_snapshot_to_boids,
)
from core.state import spawn_boids
from data import SimConfig


def test_partition_covers_all_indices_balanced_without_gaps_or_overlaps() -> None:
    assert compute_chunk_ranges(0, workers=4) == ()
    assert verify_chunk_partition((), 0) is True

    exact = compute_chunk_ranges(1000, workers=4)
    assert exact == ((0, 250), (250, 500), (500, 750), (750, 1000))
    assert verify_chunk_partition(exact, 1000) is True

    uneven = compute_chunk_ranges(10, workers=4)
    assert uneven == ((0, 3), (3, 6), (6, 8), (8, 10))
    assert verify_chunk_partition(uneven, 10) is True

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
