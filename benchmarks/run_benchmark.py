"""Suite formal de benchmarking headless (1,000, 3,000 y 5,000 entidades) con salida Markdown."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_ENTITY_LOADS: tuple[int, ...] = (1000, 3000, 5000)


@dataclass(frozen=True, slots=True)
class HardwareInfo:
    """Metadatos inmutables del hardware y entorno de ejecución detectados dinámicamente."""

    processor: str
    os_name: str
    python_version: str
    logical_cores: int
    active_workers: int


@dataclass(frozen=True, slots=True)
class BenchmarkRow:
    """Resultado congelado de una carga (Secuencial vs. Paralelo) con dt = 1/60 fijo."""

    entity_count: int
    frames: int
    seq_ms: float
    seq_fps: float
    par_ms: float
    par_fps: float
    speedup: float
    ipc_pickle_ms: float
    ipc_share_pct: float
    payload_kb: float


@dataclass(frozen=True, slots=True)
class BenchmarkReport:
    """Reporte completo inmutable listo para exportar a tabla Markdown."""

    hardware: HardwareInfo
    partition_strategy: str
    seed: int
    fixed_dt: float
    rows: tuple[BenchmarkRow, ...]

