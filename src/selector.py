"""Hierarchical search-free selector with an explicit certification status."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

from .candidate_roots import rho_candidates, select_alpha, select_rho
from .structured_envelopes import comparison_rectangle_envelope, select_comparison_alpha, select_disk_alpha, select_rectangle_alpha


@dataclass(frozen=True)
class Selection:
    rho: float
    alpha: float
    envelope: float
    predictor: float
    method: str
    status: str


def predict_then_certify(blocks,g0,pixel_corners,rho_interval=(.01,100.),alpha_interval=(1e-6,2.)):
    """Finite pixel-curvature prediction followed by one rigorous certificate."""
    rho,_,_=select_rho(pixel_corners,rho_interval,0)
    alpha,predictor,_=select_alpha(pixel_corners,rho,alpha_interval,0)
    envelope=comparison_rectangle_envelope(blocks,g0,rho,alpha)
    collapsed=alpha<.01 or rho>=.999*rho_interval[1]
    if envelope<1 and not collapsed:status='CERTIFIED_USEFUL'
    elif envelope<1:status='CERTIFIED_CONSERVATIVE'
    else:status='UNCERTIFIABLE'
    return Selection(rho,alpha,envelope,predictor,'predict_then_certify',status)


def select_hierarchy(blocks, g0, corners, rho_interval=(.01,100.), alpha_interval=(1e-6,2.)):
    """Choose the tightest rigorous signed bound on finite local rho candidates."""
    prho,_,_=select_rho(corners,rho_interval,0); palpha,pred,_=select_alpha(corners,prho,alpha_interval,0)
    best=None
    for rho in rho_candidates(corners,rho_interval,0):
        for name,fn in (('block_gershgorin',select_disk_alpha),('commutator_rectangle',select_rectangle_alpha),('comparison_rectangle',select_comparison_alpha)):
            alpha,value,_=fn(blocks,g0,rho,alpha_interval)
            if best is None or value<best[0]:best=(value,float(rho),alpha,name)
    value,rho,alpha,name=best
    # Predictor is used only to flag conservatism; the returned envelope is rigorous.
    if value < 1 and value <= 1.25*pred: status='CERTIFIED_TIGHT'
    elif value < 1: status='CERTIFIED_CONSERVATIVE'
    else: status='UNCERTIFIABLE'
    return Selection(rho,alpha,value,pred,name,status)
