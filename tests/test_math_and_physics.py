"""Pruebas unitarias de utilidades matemáticas puras 2D en core/math_utils.py."""

from __future__ import annotations

import math
import pytest

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
