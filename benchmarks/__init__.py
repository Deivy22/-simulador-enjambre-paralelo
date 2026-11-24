"""Suite de benchmarks reproducibles headless (1k, 3k y 5k entidades)."""

from benchmarks.run_benchmark import (
    BenchmarkReport,
    BenchmarkRow,
    HardwareInfo,
    format_markdown_report,
    run_full_benchmark,
)

__all__: tuple[str, ...] = (
    "BenchmarkReport",
    "BenchmarkRow",
    "HardwareInfo",
    "format_markdown_report",
    "run_full_benchmark",
)
