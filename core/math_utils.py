"""Utilidades matemáticas puras para vectores 2D."""

from __future__ import annotations

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
