#!/usr/bin/env python3
"""Fast-validation comparison of global, block-resolvent, and block-disk bounds."""
from pathlib import Path
import csv, json, time, yaml

import numpy as np
import pandas as pd

from src.candidate_roots import alpha_candidates, rho_candidates, select_alpha, select_rho
from src.local_envelope import certified_envelope, local_envelope
from src.operators import data_hessian, periodic_laplacian, regularizer_symbol
from src.spectral_tools import reduced_matrix, spectral_radius
from src.structured_envelopes import (
    block_gershgorin_envelope, block_resolvent_envelope,
    block_resolvent_error, select_disk_alpha, select_rectangle_alpha,
    select_comparison_alpha,
)

ROOT=Path(__file__).resolve().parents[1]


def finite_rhos(corners, interval):
    """Constant-model algebraic candidates; no rho grid or iterative search."""
    return rho_candidates(corners, interval, delta=0.0)


def select_block_resolvent(corners, blocks, surrogate, interval, alpha_interval):
    best=None
    for rho in finite_rhos(corners, interval):
        eps=block_resolvent_error(blocks,surrogate,rho)
        # alpha*eps/2 equals the legacy alpha*delta/rho form at delta=eps*rho/2.
        for alpha in alpha_candidates(corners,rho,alpha_interval,delta=eps*rho/2):
            value=block_resolvent_envelope(corners,blocks,surrogate,rho,alpha)
            if best is None or value < best[0]: best=(value,float(rho),float(alpha))
    return best


def select_block_disks(corners, blocks, g0, interval, alpha_interval):
    best=None
    for rho in finite_rhos(corners,interval):
        alpha,value,_=select_disk_alpha(blocks,g0,rho,alpha_interval)
        if best is None or value < best[0]: best=(value,float(rho),alpha)
    return best


def select_rectangle(corners,blocks,g0,interval,alpha_interval):
    best=None
    for rho in finite_rhos(corners,interval):
        alpha,value,_=select_rectangle_alpha(blocks,g0,rho,alpha_interval)
        if best is None or value < best[0]: best=(value,float(rho),alpha)
    return best


def select_comparison(corners,blocks,g0,interval,alpha_interval):
    best=None
    for rho in finite_rhos(corners,interval):
        alpha,value,_=select_comparison_alpha(blocks,g0,rho,alpha_interval)
        if best is None or value<best[0]:best=(value,float(rho),alpha)
    return best


def main():
    cfg=yaml.safe_load((ROOT/'configs'/'controlled.yaml').read_text()); rng=np.random.default_rng(cfg['seed']); rows=[]
    baseline=pd.read_csv(ROOT/'results'/'raw'/'variable_coeff.csv').set_index(['n','contrast','frequency','trial'])
    for n in cfg['grid_sizes']:
      yy,xx=np.meshgrid(np.arange(n),np.arange(n),indexing='ij')
      for contrast in cfg['contrasts']:
       for freq in cfg['rotation_frequencies']:
        for trial in range(cfg['trials_per_setting']):
          mag=.4*(1+(contrast-1)*(xx/(n-1))); angle=2*np.pi*freq*yy/n+rng.normal(scale=.03,size=(n,n))
          q=np.stack([mag*np.cos(angle),mag*np.sin(angle)],-1)
          blocks=np.einsum('...i,...j->...ij',q,q).reshape(-1,2,2)+.05*np.eye(2)[None]
          mean_block=blocks.mean(0); surrogate=np.repeat(mean_block[None],len(blocks),axis=0)
          h=data_hessian(q,damping=.05).toarray()
          g0=periodic_laplacian((n,n),beta=cfg['regularization_beta'],gamma=cfg['regularization_gamma']).toarray(); g=np.kron(g0,np.eye(2))
          symbol=regularizer_symbol((n,n),beta=cfg['regularization_beta'],gamma=cfg['regularization_gamma'])
          corners=np.array([[x,y] for x in np.linalg.eigvalsh(mean_block) for y in (symbol.min(),symbol.max())])
          oracle_radius=float(baseline.loc[(n,contrast,freq,trial),'exact_joint_radius'])
          for method,selector in (
            ('local_predictor',lambda:(lambda rv:(select_alpha(corners,rv[0],cfg['alpha_interval'],0)[1],rv[0],select_alpha(corners,rv[0],cfg['alpha_interval'],0)[0]))(select_rho(corners,cfg['rho_interval'],0))),
            ('block_resolvent',lambda:select_block_resolvent(corners,blocks,surrogate,cfg['rho_interval'],cfg['alpha_interval'])),
            ('block_gershgorin',lambda:select_block_disks(corners,blocks,g0,cfg['rho_interval'],cfg['alpha_interval'])),
            ('commutator_rectangle',lambda:select_rectangle(corners,blocks,g0,cfg['rho_interval'],cfg['alpha_interval'])),
            ('comparison_rectangle',lambda:select_comparison(corners,blocks,g0,cfg['rho_interval'],cfg['alpha_interval'])),
          ):
            start=time.perf_counter(); bound,rho,alpha=selector(); elapsed=time.perf_counter()-start
            actual=spectral_radius(reduced_matrix(h,g,rho,alpha))
            rows.append(dict(n=n,contrast=contrast,frequency=freq,trial=trial,method=method,rho=rho,alpha=alpha,bound=bound,actual_radius=actual,oracle_radius=oracle_radius,relative_radius_gap=(actual-oracle_radius)/oracle_radius,envelope_gap=(bound-actual)/actual,selection_seconds=elapsed,certificate_valid=actual<=bound+1e-10,collapsed=alpha<.01 or rho>=.999*cfg['rho_interval'][1]))
    out=ROOT/'results'/'raw'; out.mkdir(parents=True,exist_ok=True)
    with (out/'structured_envelopes.csv').open('w',newline='') as f:
      w=csv.DictWriter(f,fieldnames=rows[0]); w.writeheader(); w.writerows(rows)
    frame=pd.DataFrame(rows); summary={}
    for method,group in frame.groupby('method'):
      summary[method]={'n_cases':len(group),'median_envelope_gap':float(group.envelope_gap.median()),'median_parameter_gap':float(group.relative_radius_gap.median()),'certificate_failures':None if method=='local_predictor' else int((~group.certificate_valid).sum()),'collapses':int(group.collapsed.sum()),'gate_2_tightness_passed':bool(group.envelope_gap.median()<.25),'gate_3_quality_passed':bool(group.relative_radius_gap.median()<.10),'gate_4_robustness_passed':bool(group.collapsed.sum()==0)}
    (ROOT/'results'/'structured_summary.json').write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
