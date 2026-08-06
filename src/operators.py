"""Finite-difference and registration Hessian operators."""
from __future__ import annotations

import numpy as np
from scipy import sparse


def periodic_difference(n: int, spacing: float = 1.0):
    d = sparse.diags([-np.ones(n), np.ones(n)], [0, 1], shape=(n, n), format="lil")
    d[-1, 0] = 1.0
    return d.tocsr() / spacing


def periodic_laplacian(shape, beta=1.0, gamma=0.0, spacing=1.0):
    mats = []
    for axis, n in enumerate(shape):
        d = periodic_difference(n, spacing)
        factors = [sparse.eye(m) for m in shape]
        factors[axis] = d
        op = factors[0]
        for f in factors[1:]:
            op = sparse.kron(op, f, format="csr")
        mats.append(op)
    n_total = int(np.prod(shape))
    return gamma * sparse.eye(n_total) + beta * sum((d.T @ d for d in mats), sparse.csr_matrix((n_total, n_total)))


def regularizer_symbol(shape, beta=1.0, gamma=0.0, spacing=1.0, order=1):
    grids = np.meshgrid(*[2 * np.pi * np.arange(n) / n for n in shape], indexing="ij")
    base = sum(4 * np.sin(x / 2) ** 2 / spacing**2 for x in grids)
    return gamma + beta * base**order


def data_hessian(gradients, mu=1.0, damping=0.0):
    q = np.asarray(gradients, dtype=float).reshape(-1, np.asarray(gradients).shape[-1])
    blocks = mu * np.einsum("ni,nj->nij", q, q)
    blocks += damping * np.eye(q.shape[1])[None]
    return sparse.block_diag(blocks, format="csr")

