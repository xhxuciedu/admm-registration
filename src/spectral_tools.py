"""Iteration matrices and spectral diagnostics for quadratic ADMM."""
from __future__ import annotations

import numpy as np
from scipy.linalg import solve


def resolvent(a: np.ndarray, rho: float) -> np.ndarray:
    """Return rho (A + rho I)^-1 without forming an inverse."""
    n = a.shape[0]
    return solve(a + rho * np.eye(n), rho * np.eye(n), assume_a="sym")


def cayley(a: np.ndarray, rho: float) -> np.ndarray:
    p = resolvent(a, rho)
    return np.eye(a.shape[0]) - 2.0 * p


def reduced_matrix(h: np.ndarray, g: np.ndarray, rho: float, alpha: float = 1.0) -> np.ndarray:
    n = h.shape[0]
    return (1.0 - alpha / 2.0) * np.eye(n) + alpha / 2.0 * cayley(h, rho) @ cayley(g, rho)


def full_state_matrix(h: np.ndarray, g: np.ndarray, rho: float, alpha: float = 1.0) -> np.ndarray:
    """Homogeneous [w,u] map for Boyd-style scaled over-relaxation."""
    ph, pg = resolvent(h, rho), resolvent(g, rho)
    n = h.shape[0]
    eye = np.eye(n)
    z_w = alpha * ph + (1.0 - alpha) * eye
    z_u = eye - alpha * ph
    w_w, w_u = pg @ z_w, pg @ z_u
    return np.block([[w_w, w_u], [z_w - w_w, z_u - w_u]])


def spectral_radius(a: np.ndarray) -> float:
    return float(np.max(np.abs(np.linalg.eigvals(a))))


def nonzero_spectrum(a: np.ndarray, tol: float = 1e-10) -> np.ndarray:
    vals = np.linalg.eigvals(a)
    return vals[np.abs(vals) > tol]

