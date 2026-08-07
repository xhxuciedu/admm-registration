"""Diagnostic dense and matrix-free spectral oracles (never used by predictor)."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.sparse.linalg import LinearOperator,eigs

from .spectral_tools import cayley,reduced_matrix,spectral_radius
from .structured_envelopes import cayley_blocks


def exact_conditional_alpha(product_eigenvalues,interval=(1e-6,2.0)):
    """Globally minimize max |1+alpha(lambda-1)/2| over a finite set."""
    lam=np.asarray(product_eigenvalues,complex);lo,hi=interval
    a=np.real(lam-1);b=np.abs(lam-1)**2/4
    cand=[float(lo),float(hi)]
    # Stationary points of individual squared moduli.
    for ai,bi in zip(a,b):
        if bi>0:
            x=-ai/(2*bi)
            if lo<x<hi:cand.append(float(x))
    # Pairwise intersections of squared moduli; constant terms cancel.
    for i in range(len(lam)):
      for j in range(i+1,len(lam)):
        den=b[i]-b[j]
        if abs(den)>1e-15:
            x=-(a[i]-a[j])/den
            if lo<x<hi:cand.append(float(x))
    cand=np.asarray(sorted(set(round(x,14) for x in cand)))
    vals=np.max(np.abs(1+cand[:,None]*(lam[None]-1)/2),axis=1);idx=int(np.argmin(vals))
    return float(cand[idx]),float(vals[idx]),cand


@dataclass(frozen=True)
class OracleResult:
    rho: float
    alpha: float
    radius: float
    rho_evaluations: int


def dense_oracle(h,g,rho_interval=(1e-4,1e3),alpha_interval=(1e-6,2.),grid_points=121):
    """Dense log grid plus bounded refinement around every detected minimum."""
    lo,hi=np.log(rho_interval);cache={}
    def objective(z):
        key=float(z)
        if key not in cache:
            rho=np.exp(key);p=cayley(h,rho)@cayley(g,rho);alpha,value,_=exact_conditional_alpha(np.linalg.eigvals(p),alpha_interval)
            cache[key]=(value,alpha)
        return cache[key][0]
    grid=np.linspace(lo,hi,grid_points);vals=np.array([objective(z) for z in grid]);brackets=[]
    for i in range(1,len(grid)-1):
        if vals[i]<=vals[i-1] and vals[i]<=vals[i+1]:brackets.append((grid[i-1],grid[i+1]))
    candidates=[(vals[i],grid[i]) for i in (0,len(grid)-1)]
    for bracket in brackets:
        opt=minimize_scalar(objective,bounds=bracket,method='bounded',options={'xatol':1e-11,'maxiter':200});candidates.append((float(opt.fun),float(opt.x)))
    _,z=min(candidates);objective(z);value,alpha=cache[z]
    return OracleResult(float(np.exp(z)),float(alpha),float(value),len(cache))


def periodic_reduced_operator(blocks,symbol,rho,alpha):
    """Matrix-free reduced E using FFT for exact periodic C_G."""
    blocks=np.asarray(blocks);shape=np.asarray(symbol).shape;n=np.prod(shape);d=blocks.shape[-1];cb=cayley_blocks(blocks,rho);mult=(np.asarray(symbol)-rho)/(np.asarray(symbol)+rho)
    def matvec(x):
        field=np.asarray(x).reshape(*shape,d);cg=np.empty_like(field,dtype=np.result_type(x,complex))
        for j in range(d):cg[...,j]=np.fft.ifftn(np.fft.fftn(field[...,j])*mult)
        product=np.einsum('nij,nj->ni',cb,cg.reshape(int(n),d)).reshape(-1)
        return (1-alpha/2)*np.asarray(x)+alpha*product/2
    return LinearOperator((int(n*d),int(n*d)),matvec=matvec,dtype=np.complex128)


def arnoldi_radius(blocks,symbol,rho,alpha,tol=1e-9,maxiter=None,k=6):
    op=periodic_reduced_operator(blocks,symbol,rho,alpha);vals=eigs(op,k=min(k,op.shape[0]-2),which='LM',tol=tol,maxiter=maxiter,return_eigenvectors=False)
    return float(np.max(np.abs(vals))),vals
