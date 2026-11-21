"""Subpaquete de grilla espacial inmutable y motor secuencial."""

from core.engine.sequential import step_boids_sequential, update_sequential
from core.engine.spatial_grid import (
    SpatialGridIndex,
    build_spatial_grid,
    cell_coords,
    grid_dimensions,
    query_neighbor_indices,
    query_neighbors,
)

__all__: tuple[str, ...] = (
    "SpatialGridIndex",
    "build_spatial_grid",
    "cell_coords",
    "grid_dimensions",
    "query_neighbor_indices",
    "query_neighbors",
    "step_boids_sequential",
    "update_sequential",
)
