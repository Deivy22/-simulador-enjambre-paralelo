"""Punto de entrada principal protegido para Windows (spawn) y multiplataforma."""

from __future__ import annotations

import multiprocessing

from ui.app import run_simulator


def main() -> None:
    """Lanza el Simulador de Enjambre 2D desde la Pantalla de Inicio."""
    multiprocessing.freeze_support()
    run_simulator()


if __name__ == "__main__":
    main()
