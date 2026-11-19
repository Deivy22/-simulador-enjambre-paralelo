"""Alias de tipos inmutables y enumeraciones del dominio (solo stdlib)."""

from __future__ import annotations

from enum import Enum
from typing import TypeAlias

Vec2: TypeAlias = tuple[float, float]
FlatBoidTuple: TypeAlias = tuple[float, float, float, float]
ChunkRange: TypeAlias = tuple[int, int]
SpatialGrid: TypeAlias = tuple[tuple[int, ...], ...]


class SimMode(Enum):
    """Modo de ejecución del motor físico."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


class ScreenMode(Enum):
    """Pantalla activa de la aplicación."""

    START = "start"
    SIMULATION = "simulation"


class MouseAction(Enum):
    """Tipo de interacción del cursor sobre el lienzo."""

    NONE = "none"
    ATTRACT = "attract"
    REPEL = "repel"


class StartAction(Enum):
    """Acciones discretas disparadas desde la Pantalla de Inicio."""

    NONE = "none"
    SELECT_1000 = "select_1000"
    SELECT_3000 = "select_3000"
    SELECT_5000 = "select_5000"
    SELECT_SEQUENTIAL = "select_sequential"
    SELECT_PARALLEL = "select_parallel"
    START_SIMULATION = "start_simulation"
