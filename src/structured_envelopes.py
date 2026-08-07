"""Structure-aware rigorous spectral enclosures for registration ADMM."""
from __future__ import annotations

import numpy as np
from scipy.linalg import solve
from scipy import sparse
from scipy.sparse.linalg import eigsh

from .local_envelope import local_envelope
from .spectral_tools import cayley


def cayley_blocks(blocks: np.ndarray, rho: float) -> np.ndarray:
    """Exact Cayley transforms of the pixelwise 2x2 or 3x3 Hessians."""
    blocks = np.asarray(blocks, dtype=float)
    eye = np.eye(blocks.shape[-1])
    return np.stack([(b-rho*eye) @ solve(b+rho*eye, eye, assume_a="sym") for b in blocks])


def block_resolvent_error(blocks, surrogate_blocks, rho: float) -> float:
    """Exact max-block ||C_H-C_Htilde||_2, not a delta/rho estimate."""
    cb = cayley_blocks(blocks, rho)
    cs = cayley_blocks(surrogate_blocks, rho)
    return float(max(np.linalg.norm(a-b, 2) for a, b in zip(cb, cs)))


def block_resolvent_envelope(corners, blocks, surrogate_blocks, rho, alpha=1.0):
    """Certificate with exact G and exact blockwise Cayley mismatch."""
    eps = block_resolvent_error(blocks, surrogate_blocks, rho)
    return local_envelope(corners, rho, alpha) + alpha * eps / 2.0


def block_gershgorin_disks(blocks, g0, rho: float):
    """Return real centers and radii enclosing sigma(C_H (C_G0 kron I))."""
    cblocks = cayley_blocks(blocks, rho)
    k = cayley(np.asarray(g0, dtype=float), rho)
    row_off = np.sum(np.abs(k), axis=1) - np.abs(np.diag(k))
    centers, radii = [], []
    for i, ci in enumerate(cblocks):
        eig = np.linalg.eigvalsh(ci)
        centers.extend(k[i, i] * eig)
        # Exact row sum of off-diagonal block norms: |k_ij| ||C_i||_2.
        radii.extend([np.linalg.norm(ci, 2) * row_off[i]] * len(eig))
    return np.asarray(centers), np.asarray(radii)


def block_gershgorin_envelope(blocks, g0, rho, alpha=1.0):
    centers, radii = block_gershgorin_disks(blocks, g0, rho)
    mapped = 1.0 - alpha / 2.0 + alpha * centers / 2.0
    return float(np.max(np.abs(mapped) + alpha * radii / 2.0))


def disk_alpha_candidates(centers, radii, interval=(1e-6, 2.0)):
    """All vertices of max_i |1+a(z_i-1)/2| + a r_i/2."""
    lo, hi = interval
    centers, radii = np.asarray(centers), np.asarray(radii)
    # Each absolute value is the maximum of two affine functions.
    slopes = np.r_[(centers-1+radii)/2, (1-centers+radii)/2]
    intercepts = np.r_[np.ones_like(centers), -np.ones_like(centers)]
    cand = [float(lo), float(hi)]
    for i in range(len(slopes)):
        for j in range(i+1, len(slopes)):
            den = slopes[i]-slopes[j]
            if abs(den) > 1e-14:
                a = (intercepts[j]-intercepts[i])/den
                if lo < a < hi:
                    cand.append(float(a))
    return np.asarray(sorted(set(round(a, 13) for a in cand)))


def select_disk_alpha(blocks, g0, rho, interval=(1e-6, 2.0)):
    centers, radii = block_gershgorin_disks(blocks, g0, rho)
    cand = disk_alpha_candidates(centers, radii, interval)
    vals = [block_gershgorin_envelope(blocks, g0, rho, a) for a in cand]
    i = int(np.argmin(vals))
    return float(cand[i]), float(vals[i]), cand


def local_rectangle_bounds(blocks, g0, rho: float):
    """Block-local bounds for symmetric/skew parts of C_H C_G.

    Returns m <= lambda_min(S), M >= lambda_max(S), eta >= ||K||_2.
    Off-diagonal skew blocks are k_ij(C_i-C_j)/2, so eta responds to
    neighboring Cayley-block variation and is exactly zero for constant H.
    """
    c = cayley_blocks(blocks, rho); k = cayley(np.asarray(g0), rho)
    pair_sum=(c[:,None]+c[None,:])/2; pair_diff=(c[:,None]-c[None,:])/2
    sum_norm=np.max(np.abs(np.linalg.eigvalsh(pair_sum)),axis=-1)
    diff_norm=np.max(np.abs(np.linalg.eigvalsh(pair_diff)),axis=-1)
    weights=np.abs(k).copy(); np.fill_diagonal(weights,0.0)
    sym_radius=np.sum(weights*sum_norm,axis=1); skew_rows=np.sum(weights*diff_norm,axis=1)
    diag_eigs=np.linalg.eigvalsh(np.diag(k)[:,None,None]*c)
    return (float(np.min(diag_eigs[:,0]-sym_radius)),
            float(np.max(diag_eigs[:,-1]+sym_radius)),float(np.max(skew_rows)))


def comparison_rectangle_bounds(blocks, g0, rho: float):
    """Sharper scalar-comparison-matrix bounds for the same rectangle.

    Unlike row-sum Gershgorin, this retains global spatial coupling through
    three n-by-n symmetric comparison eigenproblems (independent of d).
    """
    c=cayley_blocks(blocks,rho); k=cayley(np.asarray(g0),rho)
    pair_sum=(c[:,None]+c[None,:])/2; pair_diff=(c[:,None]-c[None,:])/2
    sum_norm=np.max(np.abs(np.linalg.eigvalsh(pair_sum)),axis=-1)
    diff_norm=np.max(np.abs(np.linalg.eigvalsh(pair_diff)),axis=-1)
    off=np.abs(k).copy(); np.fill_diagonal(off,0.0)
    bs=off*sum_norm; bq=off*diff_norm
    diag_eigs=np.linalg.eigvalsh(np.diag(k)[:,None,None]*c)
    lower_matrix=np.diag(diag_eigs[:,0])-bs
    upper_matrix=np.diag(diag_eigs[:,-1])+bs
    m=float(np.linalg.eigvalsh(lower_matrix)[0])
    big_m=float(np.linalg.eigvalsh(upper_matrix)[-1])
    eta=float(np.max(np.abs(np.linalg.eigvalsh(bq))))
    return m,big_m,eta


def rectangle_envelope(blocks, g0, rho, alpha=1.0):
    m, big_m, eta = local_rectangle_bounds(blocks, g0, rho)
    real = 1-alpha/2 + alpha*np.asarray([m,big_m])/2
    return float(np.max(np.sqrt(real**2+(alpha*eta/2)**2)))


def comparison_rectangle_envelope(blocks,g0,rho,alpha=1.0):
    m,big_m,eta=comparison_rectangle_bounds(blocks,g0,rho)
    real=1-alpha/2+alpha*np.asarray([m,big_m])/2
    return float(np.max(np.sqrt(real**2+(alpha*eta/2)**2)))


def angular_numerical_radius_bound(blocks,g0,rho,alpha=1.0,n_angles=64):
    """Rigorous comparison bound on the numerical radius of the reduced map.

    A fixed angular sampling is made rigorous by a global Lipschitz remainder.
    Only n-by-n real symmetric comparison matrices and d-by-d block norms are
    used; the dn-by-dn iteration matrix is never formed.
    """
    if n_angles<4: raise ValueError('n_angles must be at least 4')
    c=cayley_blocks(blocks,rho);k=cayley(np.asarray(g0),rho);n,d=len(c),c.shape[-1]
    scale=alpha/2; shift=1-alpha/2; eye=np.eye(d)
    sii=shift*eye[None]+scale*np.diag(k)[:,None,None]*c
    s=scale*k[:,:,None,None]*(c[:,None]+c[None,:])/2
    q=scale*k[:,:,None,None]*(c[:,None]-c[None,:])/2
    idx=np.arange(n);s[idx,idx]=0;q[idx,idx]=0
    # Lipschitz comparison matrix for theta -> lambda_max(comparison(theta)).
    lip=np.max(np.abs(np.linalg.eigvalsh(sii)),axis=-1)
    lipmat=np.zeros((n,n));np.fill_diagonal(lipmat,lip)
    for i in range(n):
      for j in range(i+1,n):
        v=np.linalg.norm(s[i,j],2)+np.linalg.norm(q[i,j],2)
        lipmat[i,j]=lipmat[j,i]=v
    L=float(np.linalg.norm(lipmat,2)); sampled=-np.inf
    for theta_ang in 2*np.pi*np.arange(n_angles)/n_angles:
        ct,st=np.cos(theta_ang),np.sin(theta_ang)
        diagmax=np.linalg.eigvalsh(ct*sii)[:,-1]
        comp=np.diag(diagmax)
        for i in range(n):
          for j in range(i+1,n):
            v=np.linalg.norm(ct*s[i,j]-1j*st*q[i,j],2)
            comp[i,j]=comp[j,i]=v
        sampled=max(sampled,float(np.linalg.eigvalsh(comp)[-1]))
    return sampled+L*np.pi/n_angles


def truncated_kernel_comparison_envelope(blocks,symbol,rho,alpha=1.0,radius=3):
    """Scalable periodic comparison certificate with a rigorous l1 tail.

    The kept Cayley convolution offsets form sparse comparison matrices. The
    omitted convolution has 2-norm bounded by its kernel l1 norm.
    """
    symbol=np.asarray(symbol,float);shape=symbol.shape;n=int(np.prod(shape));c=cayley_blocks(blocks,rho)
    if len(shape)!=2 or len(c)!=n:raise ValueError('2D symbol/block shape mismatch')
    kernel=np.fft.ifftn((symbol-rho)/(symbol+rho)).real
    offsets=[];tail=0.
    for iy in range(shape[0]):
      dy=iy if iy<=shape[0]//2 else iy-shape[0]
      for ix in range(shape[1]):
        dx=ix if ix<=shape[1]//2 else ix-shape[1];value=float(kernel[iy,ix])
        if max(abs(dy),abs(dx))<=radius:offsets.append((dy,dx,value))
        else:tail+=abs(value)
    rows=[];cols=[];bsdata=[];bqdata=[]
    for y in range(shape[0]):
      for x in range(shape[1]):
        i=y*shape[1]+x
        for dy,dx,value in offsets:
          if dy==0 and dx==0:continue
          j=((y+dy)%shape[0])*shape[1]+((x+dx)%shape[1])
          rows.append(i);cols.append(j);bsdata.append(abs(value)*np.linalg.norm((c[i]+c[j])/2,2));bqdata.append(abs(value)*np.linalg.norm((c[i]-c[j])/2,2))
    bs=sparse.csr_matrix((bsdata,(rows,cols)),shape=(n,n));bq=sparse.csr_matrix((bqdata,(rows,cols)),shape=(n,n))
    kii=float(kernel[0,0]);de=np.linalg.eigvalsh(kii*c);lower=sparse.diags(de[:,0])-bs;upper=sparse.diags(de[:,-1])+bs
    if n<=4:
        m=float(np.linalg.eigvalsh(lower.toarray())[0]);big_m=float(np.linalg.eigvalsh(upper.toarray())[-1]);eta=float(np.max(np.abs(np.linalg.eigvalsh(bq.toarray()))))
    else:
        m=float(eigsh(lower,k=1,which='SA',return_eigenvectors=False,tol=1e-8)[0]);big_m=float(eigsh(upper,k=1,which='LA',return_eigenvectors=False,tol=1e-8)[0])
        if bq.nnz == 0 or np.max(np.abs(bq.data),initial=0.) == 0.:
            eta=0.
        else:
            eta=max(abs(float(eigsh(bq,k=1,which='LA',return_eigenvectors=False,tol=1e-8)[0])),abs(float(eigsh(bq,k=1,which='SA',return_eigenvectors=False,tol=1e-8)[0])))
    real=1-alpha/2+alpha*np.asarray([m,big_m])/2;base=float(np.max(np.sqrt(real**2+(alpha*eta/2)**2)))
    correction=alpha/2*float(max(np.linalg.norm(ci,2) for ci in c))*tail
    return base+correction,{'tail_l1':tail,'nnz':int(bs.nnz),'radius':radius,'base':base,'correction':correction}


def _rectangle_candidates_from_bounds(m,big_m,eta,interval):
    lo,hi=interval; cand=[lo,hi]
    for x in (m,big_m):
        a=(x-1)/2; b=eta/2
        if a<0:
            root=-a/(a*a+b*b)
            if lo<root<hi:cand.append(root)
    den=2-m-big_m
    if abs(den)>1e-14:
        cross=4/den
        if lo<cross<hi:cand.append(cross)
    return np.asarray(sorted(set(round(float(a),13) for a in cand)))


def rectangle_alpha_candidates(blocks, g0, rho, interval=(1e-6, 2.0)):
    """Finite exact minimizer candidates for the fixed-rho rectangle."""
    return _rectangle_candidates_from_bounds(*local_rectangle_bounds(blocks,g0,rho),interval)


def select_rectangle_alpha(blocks,g0,rho,interval=(1e-6,2.0)):
    bounds=local_rectangle_bounds(blocks,g0,rho);cand=_rectangle_candidates_from_bounds(*bounds,interval)
    m,big_m,eta=bounds
    vals=[float(np.max(np.sqrt((1-a/2+a*np.asarray([m,big_m])/2)**2+(a*eta/2)**2))) for a in cand]; i=int(np.argmin(vals))
    return float(cand[i]),float(vals[i]),cand


def select_comparison_alpha(blocks,g0,rho,interval=(1e-6,2.0)):
    bounds=comparison_rectangle_bounds(blocks,g0,rho);cand=_rectangle_candidates_from_bounds(*bounds,interval)
    m,big_m,eta=bounds
    vals=[float(np.max(np.sqrt((1-a/2+a*np.asarray([m,big_m])/2)**2+(a*eta/2)**2))) for a in cand];i=int(np.argmin(vals))
    return float(cand[i]),float(vals[i]),cand


def exact_rectangle(blocks, g0, rho: float):
    """Diagnostic full-matrix rectangle; not a practical selector primitive."""
    c=cayley_blocks(blocks,rho); k=cayley(np.asarray(g0),rho); d=c.shape[-1]
    ch=np.zeros((len(c)*d,len(c)*d))
    for i,b in enumerate(c): ch[d*i:d*i+d,d*i:d*i+d]=b
    a=ch @ np.kron(k,np.eye(d)); s=(a+a.T)/2; skew=(a-a.T)/2
    eig=np.linalg.eigvalsh(s)
    return float(eig[0]),float(eig[-1]),float(np.linalg.norm(skew,2))


def commutator_cayley_bound(h, g, rho: float):
    """Resolvent bound ||[C_H,C_G]|| <= explicit factor ||[H,G]||."""
    h=np.asarray(h); g=np.asarray(g)
    hmin=float(np.linalg.eigvalsh(h)[0]); gmin=float(np.linalg.eigvalsh(g)[0])
    factor=4*rho**2/((hmin+rho)**2*(gmin+rho)**2)
    return factor*np.linalg.norm(h@g-g@h,2)


def gradient_variation_measures(gradients, edges):
    """Neighbor magnitude-squared and unoriented-angle variation statistics."""
    q=np.asarray(gradients,float).reshape(-1,np.asarray(gradients).shape[-1]); mags=np.linalg.norm(q,axis=1)
    mag_var=0.0; angle_var=0.0
    for i,j in edges:
        mag_var=max(mag_var,abs(mags[i]**2-mags[j]**2))
        if mags[i]>0 and mags[j]>0:
            # q q^T is invariant to sign, hence use the acute unoriented angle.
            cosine=np.clip(abs(q[i]@q[j])/(mags[i]*mags[j]),-1,1)
            angle_var=max(angle_var,np.sqrt((1-cosine)/2))
    return float(mag_var),float(angle_var)
