"""Capa 1 (data): contratos de datos inmutables y tipos de dominio."""

from data.config import (
    VALID_ENTITY_COUNTS,
    SimConfig,
    clamp_worker_count,
    default_worker_count,
    detected_cpu_count,
    validate_config,
)
from data.entities import Boid, FlatBoidSnapshot
from data.game_state import GameState
from data.input_state import InputState, resolve_mouse_action
from data.metrics import MetricsSnapshot
from data.types import (
    ChunkRange,
    FlatBoidTuple,
    MouseAction,
    ScreenMode,
    SimMode,
    SpatialGrid,
    StartAction,
    Vec2,
)

__all__: tuple[str, ...] = (
    "Boid",
    "ChunkRange",
    "FlatBoidSnapshot",
    "FlatBoidTuple",
    "GameState",
    "InputState",
    "MetricsSnapshot",
    "MouseAction",
    "ScreenMode",
    "SimConfig",
    "SimMode",
    "SpatialGrid",
    "StartAction",
    "VALID_ENTITY_COUNTS",
    "Vec2",
    "clamp_worker_count",
    "default_worker_count",
    "detected_cpu_count",
    "resolve_mouse_action",
    "validate_config",
)
