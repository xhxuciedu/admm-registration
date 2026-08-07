"""Finite algebraic candidate enumeration for certified envelopes."""
from __future__ import annotations

import numpy as np
from numpy.polynomial import Polynomial as P

from .local_envelope import certified_envelope, global_four_corners, theta


def _positive_real_roots(poly: P, lo: float, hi: float, tol: float = 1e-8):
    poly=poly.trim(tol=1e-15)
    if poly.degree()<1:return []
    out = []
    for z in poly.roots():
        if abs(z.imag) <= tol * max(1.0, abs(z.real)) and lo < z.real < hi:
            x = float(z.real)
            # A few Newton steps polish ill-conditioned companion roots without
            # turning candidate generation into continuous optimization.
            derivative=poly.deriv()
            for _ in range(4):
                slope=derivative(x)
                if abs(slope)<=1e-18:break
                candidate=x-poly(x)/slope
                if not lo<candidate<hi:break
                x=float(candidate)
            scale=max(1.,sum(abs(a)*abs(x)**i for i,a in enumerate(poly.coef)))
            if abs(poly(x)) <= 1e-8 * scale:
                out.append(x)
    return out


def _merge_candidates(values,rtol=2e-10):
    values=sorted(float(x) for x in values if np.isfinite(x));out=[]
    for value in values:
        if not out or abs(value-out[-1])>rtol*max(1.,abs(value),abs(out[-1])):out.append(value)
    return np.asarray(out)


def _polynomial_key(poly):
    coef=np.asarray(poly.trim(tol=1e-15).coef,float);scale=np.max(np.abs(coef),initial=0.)
    if scale==0:return (0.,)
    coef=coef/scale
    first=coef[np.flatnonzero(np.abs(coef)>1e-14)[0]]
    if first<0:coef=-coef
    return tuple(np.round(coef,13))


def _num_den(h: float, g: float):
    p, s = h * g, h + g
    return P([p, 0.0, 1.0]), P([p, s, 1.0])


def rho_candidates(corners, interval, delta=0.0):
    """All endpoints, branch intersections, and branch stationary roots."""
    lo, hi = map(float, interval)
    corners = np.unique(np.asarray(corners, dtype=float), axis=0)
    candidates = [lo, hi];seen=set()
    def add(poly):
        key=_polynomial_key(poly)
        if key not in seen:seen.add(key);candidates.extend(_positive_real_roots(poly,lo,hi))
    nd = [_num_den(*c) for c in corners]
    for i, (ni, di) in enumerate(nd):
        h, g = corners[i]
        s, p = h + g, h * g
        # d theta / d rho = s (rho^2-p) / D(rho)^2.
        derivative_num = P([-s * p, 0.0, s])
        stationary = P([0, 0, 1]) * derivative_num - delta * di * di
        add(stationary)
        for nj, dj in nd[i + 1 :]:
            add(ni*dj-nj*di)
    return _merge_candidates(candidates)


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
    return _merge_candidates(cand)


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
    nd=[_num_den(*c) for c in corners]; cand=list(rho_candidates(corners,interval,0));seen=set()
    def add(poly):
        key=_polynomial_key(poly)
        if key not in seen:seen.add(key);cand.extend(_positive_real_roots(poly,lo,hi))
    # Swapping (a,b) negates the first reduced numerator but leaves all
    # stationary roots unchanged; the transition a+b=1 is also symmetric.
    for i,(na,da) in enumerate(nd):
      for nb,db in nd[i:]:
        num=nb*da-na*db; den=2*da*db-na*db-nb*da
        deriv=num.deriv()*den-num*den.deriv()
        add(deriv)
        transition=na*db+nb*da-da*db
        add(transition)
    return _merge_candidates(cand)


def select_joint_constant(corners, rho_interval, alpha_interval=(1e-6,2.0)):
    rhos=joint_constant_candidates(corners,rho_interval); best=None
    for rho in rhos:
        alpha,value,_=select_alpha(corners,rho,alpha_interval,0)
        if best is None or value < best[0]: best=(value,float(rho),alpha)
    return best[1],best[2],best[0],rhos


def select_four_corner(h_values,g_values,rho_interval,alpha_interval=(1e-6,2.0)):
    """Exact joint constant-model selector using the global four-corner theorem."""
    return select_joint_constant(global_four_corners(h_values,g_values),rho_interval,alpha_interval)
