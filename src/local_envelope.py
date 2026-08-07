"""Frozen-coefficient local spectral envelopes."""
from __future__ import annotations

import numpy as np


def theta(h, g, rho):
    h, g, rho = np.asarray(h), np.asarray(g), np.asarray(rho)
    return (rho**2 + h * g) / ((rho + h) * (rho + g))


def local_eigenvalue(h, g, rho, alpha=1.0):
    return 1.0 - alpha + alpha * theta(h, g, rho)


def corner_values(corners: np.ndarray, rho: float, alpha: float = 1.0) -> np.ndarray:
    c = np.asarray(corners, dtype=float)
    return local_eigenvalue(c[:, 0], c[:, 1], rho, alpha)


def local_envelope(corners: np.ndarray, rho: float, alpha: float = 1.0) -> float:
    return float(np.max(np.abs(corner_values(corners, rho, alpha))))


def certified_envelope(corners, rho, alpha=1.0, delta_h=0.0, delta_g=0.0):
    return local_envelope(corners, rho, alpha) + alpha * (delta_h + delta_g) / rho


def global_four_corners(h_values, g_values):
    """Canonical four corners for nonnegative scalar data/regularizer spectra."""
    h=np.asarray(h_values,float);g=np.asarray(g_values,float)
    if h.size==0 or g.size==0 or np.any(h<0) or np.any(g<0):
        raise ValueError('curvatures must be nonempty and nonnegative')
    return np.array([[h.min(),g.min()],[h.min(),g.max()],
                     [h.max(),g.min()],[h.max(),g.max()]])


def refined_certificate(corners, rho, alpha, delta_h, delta_g, h_min=0.0, g_min=0.0):
    """Resolvent-denominator refinement proved by the same Cayley identity."""
    correction = alpha * (
        rho * delta_h / ((h_min + rho) ** 2)
        + rho * delta_g / ((g_min + rho) ** 2)
    )
    return local_envelope(corners, rho, alpha) + correction
