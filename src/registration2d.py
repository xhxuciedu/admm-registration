"""CPU reference implementation of multiresolution 2D diffeomorphic registration."""
from __future__ import annotations
from dataclasses import dataclass,field
import time
import numpy as np
from scipy.ndimage import gaussian_filter,map_coordinates,zoom
from skimage.registration import phase_cross_correlation
from skimage.feature import SIFT,match_descriptors

from .candidate_roots import select_four_corner
from .metrics import compose_displacements,jacobian_determinant_2d
from .operators import regularizer_symbol


def warp_image(image, displacement):
    shape=image.shape;coords=np.meshgrid(*[np.arange(n) for n in shape],indexing='ij')
    sample=[coords[0]+displacement[...,0],coords[1]+displacement[...,1]]
    return map_coordinates(image,sample,order=1,mode='nearest')


def invert_displacement(displacement, iterations=40, tolerance=1e-7):
    """Invert ``x -> x + displacement(x)`` by fixed-point iteration."""
    inverse=-np.asarray(displacement,float).copy()
    for _ in range(iterations):
        updated=np.empty_like(inverse)
        for component in range(displacement.shape[-1]):
            updated[...,component]=-warp_image(displacement[...,component],inverse)
        error=float(np.max(np.abs(updated-inverse)));inverse=updated
        if error<tolerance:break
    return inverse


def phase_translation_initialization(fixed,moving,upsample_factor=10):
    """Image-only translation mapping fixed-grid points into the moving image."""
    shift,_,_=phase_cross_correlation(fixed,moving,upsample_factor=upsample_factor)
    displacement=np.empty((*fixed.shape,2),float)
    displacement[...,0]=-shift[0];displacement[...,1]=-shift[1]
    return displacement


def robust_translation_initialization(fixed,moving,max_phase_shift=50.,cluster_radius=5.,max_size=128):
    """Select a translation from phase, centroid, and SIFT proposals by NCC."""
    if max_size is not None and max(fixed.shape)>max_size:
        scale=max_size/max(fixed.shape);small_shape=tuple(max(8,int(round(n*scale))) for n in fixed.shape)
        factors=np.asarray(small_shape)/np.asarray(fixed.shape)
        fixed_small=zoom(fixed,factors,order=1);moving_small=zoom(moving,factors,order=1)
        small=robust_translation_initialization(fixed_small,moving_small,max_phase_shift*scale,cluster_radius*scale,None)
        displacement=np.empty((*fixed.shape,2),float);displacement[...,0]=small[0,0,0]/factors[0];displacement[...,1]=small[0,0,1]/factors[1]
        return displacement
    candidates=[np.zeros(2)]  # proposals use (x,y)
    phase=phase_translation_initialization(fixed,moving)[0,0][::-1]
    if np.linalg.norm(phase)<=max_phase_shift:candidates.append(phase)
    yy,xx=np.mgrid[:fixed.shape[0],:fixed.shape[1]]
    def centroid(image):
        mass=np.maximum(image,0);den=mass.sum()+1e-15
        return np.array([(xx*mass).sum()/den,(yy*mass).sum()/den])
    candidates.append(centroid(moving)-centroid(fixed))
    try:
        left,right=SIFT(n_octaves=6),SIFT(n_octaves=6);left.detect_and_extract(fixed);right.detect_and_extract(moving)
        matches=match_descriptors(left.descriptors,right.descriptors,cross_check=True,max_ratio=.9)
        differences=right.keypoints[matches[:,1]][:,::-1]-left.keypoints[matches[:,0]][:,::-1]
        counts=np.asarray([(np.linalg.norm(differences-value,axis=1)<cluster_radius).sum() for value in differences])
        if len(counts) and counts.max()>=4:
            center=differences[int(np.argmax(counts))];candidates.append(np.median(differences[np.linalg.norm(differences-center,axis=1)<cluster_radius],axis=0))
    except RuntimeError:
        pass
    def score(value):
        displacement=np.empty((*fixed.shape,2));displacement[...,0]=value[1];displacement[...,1]=value[0]
        warped=warp_image(moving,displacement);a=fixed-fixed.mean();b=warped-warped.mean()
        return float(np.sum(a*b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-15))
    selected=max(candidates,key=score);displacement=np.empty((*fixed.shape,2),float);displacement[...,0]=selected[1];displacement[...,1]=selected[0]
    return displacement


def image_pyramid(image,factors=(4,2,1),sigma=.8):
    return [zoom(gaussian_filter(image,sigma),1/f,order=1) if f>1 else image.copy() for f in factors]


def safeguard_displacement(displacement,jacobian_floor=.05,max_steps=20):
    """Damp non-translational deformation until the discrete map is regular."""
    result=np.asarray(displacement,float).copy();translation=np.mean(result,axis=(0,1),keepdims=True)
    for _ in range(max_steps):
        if jacobian_determinant_2d(result).min()>jacobian_floor:return result
        result=translation+.5*(result-translation)
    return result


def _block_solve(q,rhs,rho,mu,nu):
    """Sherman--Morrison solve of ((rho+nu)I+mu q q^T)x=rhs."""
    a=rho+nu;dot=np.sum(q*rhs,axis=-1);den=a+mu*np.sum(q*q,axis=-1)
    return rhs/a-(mu/a)*(dot/den)[...,None]*q


@dataclass
class InnerResult:
    velocity: np.ndarray
    iterations: int
    converged: bool
    history: np.ndarray
    solve_seconds: float
    rho_final: float


def solve_linearized_admm(q,residual,beta,gamma,rho,alpha=1.,order=1,mu=1.,nu=0.,
                          atol=1e-6,rtol=1e-5,max_iter=500,adaptive=None):
    shape=residual.shape;d=2;symbol=regularizer_symbol(shape,beta,gamma,order=order)
    b=mu*q*residual[...,None];w=np.zeros((*shape,d));u=np.zeros_like(w);history=[];start=time.perf_counter()
    old_v=np.zeros_like(w);old_grad=np.zeros_like(w)
    for k in range(1,max_iter+1):
        v=_block_solve(q,-b+rho*(w-u),rho,mu,nu)
        z=alpha*v+(1-alpha)*w;old_w=w.copy()
        for j in range(d):w[...,j]=np.fft.ifftn(np.fft.fftn(z[...,j]+u[...,j])*(rho/(symbol+rho))).real
        u+=z-w
        primal=np.linalg.norm(v-w);dual=rho*np.linalg.norm(w-old_w)
        data=.5*mu*np.sum((np.sum(q*v,axis=-1)+residual)**2)+.5*nu*np.sum(v*v)
        reg=.5*sum(np.sum(symbol*np.abs(np.fft.fftn(w[...,j]))**2)/np.prod(shape) for j in range(d))
        history.append((primal,dual,data+reg,rho))
        eps_p=np.sqrt(d*np.prod(shape))*atol+rtol*max(np.linalg.norm(v),np.linalg.norm(w))
        eps_d=np.sqrt(d*np.prod(shape))*atol+rtol*np.linalg.norm(rho*u)
        if primal<=eps_p and dual<=eps_d:break
        if adaptive=='residual_balance' and k%10==0:
            old=rho
            if primal>10*dual:rho*=2
            elif dual>10*primal:rho/=2
            if rho!=old:u*=old/rho
        elif adaptive=='bb' and k%5==0:
            # Safeguarded BB estimate on the data-gradient secant.
            grad=mu*q*(np.sum(q*v,axis=-1)+residual)[...,None]+nu*v
            s=(v-old_v).ravel();y=(grad-old_grad).ravel();sy=float(s@y);ss=float(s@s);yy=float(y@y)
            if sy>1e-12*np.sqrt(max(ss*yy,0)) and yy>0:
                estimate=np.sqrt(max(sy/ss,1e-12)*max(yy/sy,1e-12));old=rho;rho=float(np.clip(estimate,1e-6,1e6));u*=old/rho
            old_v=v.copy();old_grad=grad.copy()
    return InnerResult(w,k,k<max_iter,np.asarray(history),time.perf_counter()-start,rho)


def predictor_parameters(q,shape,beta,gamma,order=1,mu=1.,nu=0.,rho_interval=(1e-4,1e3)):
    h=[nu,nu+mu*float(np.max(np.sum(q*q,axis=-1)))];symbol=regularizer_symbol(shape,beta,gamma,order=order)
    return select_four_corner(h,[float(symbol.min()),float(symbol.max())],rho_interval)[:3]


@dataclass
class RegistrationResult:
    displacement: np.ndarray
    warped: np.ndarray
    records: list=field(default_factory=list)
    total_seconds: float=0.
    tuning_seconds: float=0.


def register(fixed,moving,method='predictor',factors=(4,2,1),outer_iterations=8,beta=.2,gamma=.05,
             order=1,alpha_fixed=1.,rho_fixed=1.,reuse='outer',seed=20260806,
             initial_displacement=None,initialization=None,**inner_kwargs):
    del seed
    start=time.perf_counter()
    if initial_displacement is not None and initialization is not None:raise ValueError('choose explicit or named initialization')
    if initialization=='phase':initial_displacement=phase_translation_initialization(fixed,moving)
    elif initialization=='robust_translation':initial_displacement=robust_translation_initialization(fixed,moving)
    elif initialization is not None:raise ValueError(f'unknown initialization {initialization}')
    fp=image_pyramid(fixed,factors);mp=image_pyramid(moving,factors);disp=None if initial_displacement is None else np.asarray(initial_displacement,float).copy();records=[];tune_total=0.;cached={}
    if method.startswith('predictor') and reuse=='pair_full':
        tune_start=time.perf_counter();gy,gx=np.gradient(moving);initial_q=np.stack([gy,gx],axis=-1)
        cached[0]=predictor_parameters(initial_q,fixed.shape,beta,gamma,order);tune_total+=time.perf_counter()-tune_start
    for level,(fimg,mimg,factor) in enumerate(zip(fp,mp,factors)):
        if disp is None:disp=np.zeros((*fimg.shape,2))
        else:
            scale=np.array(fimg.shape)/np.array(disp.shape[:2]);disp=zoom(disp,(*scale,1),order=1);disp[...,0]*=scale[0];disp[...,1]*=scale[1]
        disp=safeguard_displacement(disp)
        for outer in range(outer_iterations):
            warped=warp_image(mimg,disp);gy,gx=np.gradient(warped);q=np.stack([gy,gx],axis=-1);residual=warped-fimg
            key=0 if reuse in ('pair','pair_full') else (level if reuse=='level' else (level,outer))
            tune_start=time.perf_counter()
            if method.startswith('predictor'):
                if key not in cached:cached[key]=predictor_parameters(q,fimg.shape,beta,gamma,order)
                rho,alpha,_=cached[key]
            else:rho,alpha=rho_fixed,alpha_fixed
            tune=time.perf_counter()-tune_start
            if not (reuse=='pair_full' and key==0):tune_total+=tune
            adaptive='residual_balance' if method=='residual_balance' else ('bb' if method=='adaptive_bb' else None)
            inner=solve_linearized_admm(q,residual,beta,gamma,rho,alpha,order=order,adaptive=adaptive,**inner_kwargs)
            step=1.;accepted=False;base=.5*np.mean(residual**2)
            while step>=1/64:
                candidate=compose_displacements(disp,step*inner.velocity);jac=jacobian_determinant_2d(candidate);new=warp_image(mimg,candidate);obj=.5*np.mean((new-fimg)**2)
                if jac.min()>0.05 and obj<=base:accepted=True;break
                step/=2
            if accepted:disp=candidate
            records.append(dict(level=level,factor=factor,outer=outer,rho=rho,alpha=alpha,inner_iterations=inner.iterations,inner_converged=inner.converged,inner_seconds=inner.solve_seconds,tuning_seconds=tune,step=step if accepted else 0,objective_before=base,objective_after=obj if accepted else base,min_jacobian=float(jac.min()),accepted=accepted))
            if not accepted or np.linalg.norm(step*inner.velocity)/np.sqrt(inner.velocity.size)<1e-3:break
    warped=warp_image(mp[-1],disp)
    return RegistrationResult(disp,warped,records,time.perf_counter()-start,tune_total)
