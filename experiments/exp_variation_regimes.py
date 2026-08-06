#!/usr/bin/env python3
"""Magnitude, orientation, discontinuity, and smoothed-field study."""
from pathlib import Path
import csv,json,yaml
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
from scipy.optimize import minimize

from experiments.exp_structured_envelopes import select_block_disks,select_block_resolvent,select_rectangle,select_comparison
from src.candidate_roots import select_alpha,select_rho
from src.operators import data_hessian,periodic_laplacian
from src.spectral_tools import reduced_matrix,spectral_radius
from src.structured_envelopes import angular_numerical_radius_bound, comparison_rectangle_envelope

ROOT=Path(__file__).resolve().parents[1]

def fields(cfg):
 n=cfg['grid_size']; y,x=np.meshgrid(np.arange(n),np.arange(n),indexing='ij'); phase=2*np.pi*x/n
 for a in cfg['magnitude_amplitudes']:
  m=.4*(1+a*np.sin(phase)); yield 'magnitude',a,np.stack([m,np.zeros_like(m)],-1),True
 for a in cfg['orientation_amplitudes']:
  angle=a*np.sin(phase); yield 'orientation',a,.4*np.stack([np.cos(angle),np.sin(angle)],-1),True
 angle=np.where(x<n//2,0,np.pi/2); yield 'discontinuous',1.,.4*np.stack([np.cos(angle),np.sin(angle)],-1),False
 rng=np.random.default_rng(cfg['seed']); image=rng.normal(size=(n,n))
 for sigma in cfg['smoothing_sigmas']:
  smooth=gaussian_filter(image,sigma=sigma,mode='wrap'); gy,gx=np.gradient(smooth); q=np.stack([gx,gy],-1)
  scale=.4/(np.sqrt(np.mean(np.sum(q*q,axis=-1)))+1e-12); yield 'smoothed',sigma,q*scale,True

def main():
 cfg=yaml.safe_load((ROOT/'configs'/'regime_study.yaml').read_text()); n=cfg['grid_size']; rows=[]
 g0=periodic_laplacian((n,n),cfg['regularization_beta'],cfg['regularization_gamma']).toarray(); g=np.kron(g0,np.eye(2)); ge=np.linalg.eigvalsh(g0)
 for regime,level,q,smooth in fields(cfg):
  blocks=np.einsum('...i,...j->...ij',q,q).reshape(-1,2,2)+.05*np.eye(2)[None]; mb=blocks.mean(0); surrogate=np.repeat(mb[None],len(blocks),axis=0)
  h=data_hessian(q,damping=.05).toarray(); corners=np.array([[a,b] for a in np.linalg.eigvalsh(mb) for b in (ge.min(),ge.max())])
  pixel_corners=np.array([[a,b] for a in np.unique(np.round(np.linalg.eigvalsh(blocks),14)) for b in (ge.min(),ge.max())])
  prho,_,_=select_rho(pixel_corners,cfg['rho_interval'],0);palpha,_,_=select_alpha(pixel_corners,prho,cfg['alpha_interval'],0)
  objective=lambda z:spectral_radius(reduced_matrix(h,g,np.exp(z[0]),z[1]))
  optima=[]
  for start in ((np.log(prho),palpha),(np.log(.1),1.8),(0.,1.)):
   optima.append(minimize(objective,start,method='Nelder-Mead',options={'maxiter':180,'xatol':1e-9,'fatol':1e-10}))
  feasible=[o for o in optima if np.log(.01)<=o.x[0]<=np.log(100) and cfg['alpha_interval'][0]<=o.x[1]<=cfg['alpha_interval'][1]]
  ora=min([objective((np.log(prho),palpha))]+[float(o.fun) for o in feasible])
  def local():
   rho,_,_=select_rho(corners,cfg['rho_interval'],0);alpha,value,_=select_alpha(corners,rho,cfg['alpha_interval'],0);return value,rho,alpha
  def pixel_local():
   rho,_,_=select_rho(pixel_corners,cfg['rho_interval'],0);alpha,value,_=select_alpha(pixel_corners,rho,cfg['alpha_interval'],0);return value,rho,alpha
  def predict_certify():
   _,rho,alpha=pixel_local();return comparison_rectangle_envelope(blocks,g0,rho,alpha),rho,alpha
  def predict_angular():
   _,rho,alpha=pixel_local();return angular_numerical_radius_bound(blocks,g0,rho,alpha,64),rho,alpha
  selectors={'local_predictor':local,'pixel_curvature_predictor':pixel_local,'predict_then_certify':predict_certify,'predict_angular_certify':predict_angular,'block_resolvent':lambda:select_block_resolvent(corners,blocks,surrogate,cfg['rho_interval'],cfg['alpha_interval']),'block_gershgorin':lambda:select_block_disks(corners,blocks,g0,cfg['rho_interval'],cfg['alpha_interval']),'commutator_rectangle':lambda:select_rectangle(corners,blocks,g0,cfg['rho_interval'],cfg['alpha_interval']),'comparison_rectangle':lambda:select_comparison(corners,blocks,g0,cfg['rho_interval'],cfg['alpha_interval'])}
  for method,fn in selectors.items():
   bound,rho,alpha=fn(); actual=spectral_radius(reduced_matrix(h,g,rho,alpha))
   certified=method not in ('local_predictor','pixel_curvature_predictor')
   rows.append(dict(regime=regime,level=level,smooth=smooth,method=method,rho=rho,alpha=alpha,bound=bound,actual_radius=actual,oracle_radius=ora,envelope_gap=(bound-actual)/actual,parameter_gap=(actual-ora)/ora,certificate_valid=(actual<=bound+1e-10) if certified else False,certified=certified,collapsed=alpha<.01 or rho>=99.9))
 out=ROOT/'results'/'raw';out.mkdir(parents=True,exist_ok=True)
 with (out/'variation_regimes.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 df=pd.DataFrame(rows); summary={}
 for (scope,method),z in pd.concat([df.assign(scope='all'),df[df.smooth].assign(scope='smooth')]).groupby(['scope','method']):
  certified=method not in ('local_predictor','pixel_curvature_predictor')
  summary[f'{scope}:{method}']={'n':len(z),'certified':certified,'bounds_below_one':int((z.bound<1).sum()) if certified else None,'median_envelope_gap':float(z.envelope_gap.median()),'median_parameter_gap':float(z.parameter_gap.median()),'collapses':int(z.collapsed.sum()),'empirical_gate_2':bool(z.envelope_gap.median()<.25),'rigorous_gate_2':bool(certified and z.envelope_gap.median()<.25),'gate_3':bool(z.parameter_gap.median()<.10),'gate_4':bool(z.collapsed.sum()==0)}
 (ROOT/'results'/'regime_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
