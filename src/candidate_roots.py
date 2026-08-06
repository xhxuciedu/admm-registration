"""Finite algebraic candidate enumeration for certified envelopes."""
from __future__ import annotations

import numpy as np
from numpy.polynomial import Polynomial as P

from .local_envelope import certified_envelope, theta


def _positive_real_roots(poly: P, lo: float, hi: float, tol: float = 1e-8):
    scale = max(1.0, np.max(np.abs(poly.coef)))
    out = []
    for z in poly.roots():
        if abs(z.imag) <= tol * max(1.0, abs(z.real)) and lo < z.real < hi:
            x = float(z.real)
            if abs(poly(x)) <= 1e-6 * scale:
                out.append(x)
    return out


def _num_den(h: float, g: float):
    p, s = h * g, h + g
    return P([p, 0.0, 1.0]), P([p, s, 1.0])


def rho_candidates(corners, interval, delta=0.0):
    """All endpoints, branch intersections, and branch stationary roots."""
    lo, hi = map(float, interval)
    corners = np.unique(np.asarray(corners, dtype=float), axis=0)
    candidates = [lo, hi]
    nd = [_num_den(*c) for c in corners]
    for i, (ni, di) in enumerate(nd):
        h, g = corners[i]
        s, p = h + g, h * g
        # d theta / d rho = s (rho^2-p) / D(rho)^2.
        derivative_num = P([-s * p, 0.0, s])
        stationary = P([0, 0, 1]) * derivative_num - delta * di * di
        candidates.extend(_positive_real_roots(stationary, lo, hi))
        for nj, dj in nd[i + 1 :]:
            candidates.extend(_positive_real_roots(ni * dj - nj * di, lo, hi))
    return np.array(sorted(set(round(x, 13) for x in candidates)))


def select_rho(corners, interval, delta=0.0):
    cand = rho_candidates(corners, interval, delta)
    values = np.array([certified_envelope(corners, r, 1.0, delta, 0.0) for r in cand])
    i = int(np.argmin(values))
    return float(cand[i]), float(values[i]), cand


def alpha_candidates(corners, rho, interval=(1e-6, 2.0), delta=0.0):
    """Vertices of the convex piecewise-linear certified alpha objective."""
    lo, hi = interval
    t = theta(np.asarray(corners)[:, 0], np.asarray(corners)[:, 1], rho)
    # |1 + alpha(t-1)| + alpha*delta/rho: signed affine branches.
    slopes = np.r_[t - 1.0, 1.0 - t] + delta / rho
    intercepts = np.r_[np.ones_like(t), -np.ones_like(t)]
    cand = [lo, hi]
    for i in range(len(slopes)):
        for j in range(i + 1, len(slopes)):
            d = slopes[i] - slopes[j]
            if abs(d) > 1e-14:
                a = (intercepts[j] - intercepts[i]) / d
                if lo < a < hi:
                    cand.append(float(a))
    return np.array(sorted(set(round(x, 13) for x in cand)))


def select_alpha(corners, rho, interval=(1e-6, 2.0), delta=0.0):
    cand = alpha_candidates(corners, rho, interval, delta)
    vals = np.array([certified_envelope(corners, rho, a, delta, 0.0) for a in cand])
    i = int(np.argmin(vals))
    return float(cand[i]), float(vals[i]), cand


def joint_constant_candidates(corners, interval):
    """Finite rho set containing the global constant-coefficient oADMM optimum.

    Between branch intersections, a=min(theta_c) and b=max(theta_c) are fixed
    rational branches. Eliminating the exact fixed-rho relaxation gives either
    (b-a)/(2-a-b) or 2b-1. We enumerate roots of both branchwise derivatives,
    a+b=1 transitions, branch intersections, and interval endpoints.
    """
    lo,hi=map(float,interval); corners=np.unique(np.asarray(corners,float),axis=0)
    nd=[_num_den(*c) for c in corners]; cand=list(rho_candidates(corners,interval,0))
    for na,da in nd:
      for nb,db in nd:
        num=nb*da-na*db; den=2*da*db-na*db-nb*da
        deriv=num.deriv()*den-num*den.deriv()
        cand.extend(_positive_real_roots(deriv,lo,hi))
        transition=na*db+nb*da-da*db
        cand.extend(_positive_real_roots(transition,lo,hi))
    return np.asarray(sorted(set(round(float(x),13) for x in cand)))


def select_joint_constant(corners, rho_interval, alpha_interval=(1e-6,2.0)):
    rhos=joint_constant_candidates(corners,rho_interval); best=None
    for rho in rhos:
        alpha,value,_=select_alpha(corners,rho,alpha_interval,0)
        if best is None or value < best[0]: best=(value,float(rho),alpha)
    return best[1],best[2],best[0],rhos
