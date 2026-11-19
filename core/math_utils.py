"""Utilidades matemáticas puras para vectores 2D."""

from __future__ import annotations

import math

from data.types import Vec2


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
