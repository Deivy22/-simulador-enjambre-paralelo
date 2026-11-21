"""Contrato inmutable de tareas para workers paralelos picklables."""

from __future__ import annotations

from dataclasses import dataclass

from core.engine.spatial_grid import SpatialGridIndex
from data.config import SimConfig
from data.entities import FlatBoidSnapshot
from data.input_state import InputState
from data.types import ChunkRange


@dataclass(frozen=True, slots=True)
class WorkerTask:
    """Carga inmutable enviada a un worker para procesar un segmento [start, end)."""

    chunk_range: ChunkRange
    snapshot: FlatBoidSnapshot
    grid: SpatialGridIndex
    input_state: InputState
    config: SimConfig
    dt: float
