"""Deformation diagnostics."""
from __future__ import annotations
import numpy as np


def jacobian_determinant_2d(displacement, spacing=(1.0, 1.0)):
    u = np.asarray(displacement)
    duy, dux = np.gradient(u[..., 0], *spacing, edge_order=2)
    dvy, dvx = np.gradient(u[..., 1], *spacing, edge_order=2)
    return (1 + dux) * (1 + dvy) - duy * dvx


def compose_displacements(first, second):
    """First-order same-grid composition; exact for constant translations."""
    from scipy.ndimage import map_coordinates
    shape = first.shape[:-1]
    coords = np.meshgrid(*[np.arange(n) for n in shape], indexing="ij")
    sample = [coords[a] + first[..., a] for a in range(len(shape))]
    warped = np.stack([map_coordinates(second[..., a], sample, order=1, mode="nearest") for a in range(len(shape))], axis=-1)
    return first + warped

