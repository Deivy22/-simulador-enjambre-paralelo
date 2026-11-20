"""Utilidades matemáticas puras para vectores 2D."""

from __future__ import annotations

import math
from typing import Final

from data.types import Vec2

ZERO_VEC: Final[Vec2] = (0.0, 0.0)
NORM_EPSILON_SQ: Final[float] = 1e-8


def vec_add(a: Vec2, b: Vec2) -> Vec2:
    """Retorna la suma pura de dos vectores 2D."""
    return (a[0] + b[0], a[1] + b[1])


def vec_sub(a: Vec2, b: Vec2) -> Vec2:
    """Retorna la resta pura a - b de dos vectores 2D."""
    return (a[0] - b[0], a[1] - b[1])


def vec_scale(v: Vec2, scalar: float) -> Vec2:
    """Escala un vector 2D por un escalar real."""
    return (v[0] * scalar, v[1] * scalar)


def vec_div(v: Vec2, scalar: float) -> Vec2:
    """Divide un vector 2D por un escalar no nulo."""
    if abs(scalar) < 1e-12:
        raise ValueError("No se puede dividir un vector por cero.")
    inv = 1.0 / scalar
    return (v[0] * inv, v[1] * inv)


def vec_dot(a: Vec2, b: Vec2) -> float:
    """Retorna el producto punto entre dos vectores 2D."""
    return a[0] * b[0] + a[1] * b[1]


def vec_mag_sq(v: Vec2) -> float:
    """Retorna la magnitud al cuadrado de un vector 2D (sin sqrt)."""
    return v[0] * v[0] + v[1] * v[1]


def vec_mag(v: Vec2) -> float:
    """Retorna la magnitud euclidiana de un vector 2D."""
    return math.sqrt(v[0] * v[0] + v[1] * v[1])


def dist_sq(a: Vec2, b: Vec2) -> float:
    """Retorna la distancia euclidiana al cuadrado entre dos puntos 2D."""
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return dx * dx + dy * dy


def dist(a: Vec2, b: Vec2) -> float:
    """Retorna la distancia euclidiana entre dos puntos 2D."""
    return math.sqrt(dist_sq(a, b))


def clamp_scalar(value: float, min_value: float, max_value: float) -> float:
    """Acota un escalar al intervalo cerrado [min_value, max_value]."""
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def vec_normalize(v: Vec2) -> Vec2:
    """Normaliza un vector 2D; retorna (0.0, 0.0) si su norma es casi cero."""
    mag_sq = v[0] * v[0] + v[1] * v[1]
    if mag_sq < NORM_EPSILON_SQ:
        return ZERO_VEC
    inv_mag = 1.0 / math.sqrt(mag_sq)
    return (v[0] * inv_mag, v[1] * inv_mag)


def vec_unit_or_default(v: Vec2, default_dir: Vec2 = (1.0, 0.0)) -> Vec2:
    """Retorna vector unitario de v, o la dirección unitaria de respaldo si ||v||≈0."""
    unit = vec_normalize(v)
    if unit != ZERO_VEC:
        return unit
    fallback = vec_normalize(default_dir)
    return fallback if fallback != ZERO_VEC else (1.0, 0.0)


def vec_limit(v: Vec2, max_mag: float) -> Vec2:
    """Limita la magnitud de un vector 2D a max_mag sin alterar su dirección."""
    if max_mag <= 0.0:
        return ZERO_VEC
    mag_sq = v[0] * v[0] + v[1] * v[1]
    max_sq = max_mag * max_mag
    if mag_sq <= max_sq:
        return v
    scale = max_mag / math.sqrt(mag_sq)
    return (v[0] * scale, v[1] * scale)


def clamp_speed(
    velocity: Vec2,
    min_speed: float,
    max_speed: float,
    fallback_dir: Vec2 = (1.0, 0.0),
) -> Vec2:
    """Acota la velocidad al rango [min_speed, max_speed] protegiendo norma cero."""
    speed_sq = velocity[0] * velocity[0] + velocity[1] * velocity[1]
    if speed_sq < NORM_EPSILON_SQ:
        unit_dir = vec_unit_or_default(fallback_dir)
        return (unit_dir[0] * min_speed, unit_dir[1] * min_speed)

    min_sq = min_speed * min_speed
    if speed_sq < min_sq:
        scale = min_speed / math.sqrt(speed_sq)
        return (velocity[0] * scale, velocity[1] * scale)

    max_sq = max_speed * max_speed
    if speed_sq > max_sq:
        scale = max_speed / math.sqrt(speed_sq)
        return (velocity[0] * scale, velocity[1] * scale)

    return velocity
