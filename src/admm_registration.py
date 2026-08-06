"""Reference quadratic ADMM solver using the manuscript convention."""
from __future__ import annotations

import numpy as np
from scipy.linalg import solve


def solve_quadratic(h, g, b, rho, alpha=1.0, atol=1e-8, rtol=1e-6, max_iter=10000):
    n = len(b)
    w = np.zeros(n); u = np.zeros(n)
    history = []
    for k in range(1, max_iter + 1):
        v = solve(h + rho*np.eye(n), -b + rho*(w-u), assume_a="sym")
        z = alpha*v + (1-alpha)*w
        old_w = w.copy()
        w = solve(g + rho*np.eye(n), rho*(z+u), assume_a="sym")
        u += z-w
        primal = np.linalg.norm(v-w)
        dual = rho*np.linalg.norm(w-old_w)
        eps_p = np.sqrt(n)*atol + rtol*max(np.linalg.norm(v), np.linalg.norm(w))
        eps_d = np.sqrt(n)*atol + rtol*np.linalg.norm(rho*u)
        obj = .5*v@h@v + b@v + .5*w@g@w
        history.append((primal, dual, obj))
        if primal <= eps_p and dual <= eps_d:
            break
    return {"v": v, "w": w, "u": u, "iterations": k, "history": np.asarray(history), "converged": k < max_iter}

