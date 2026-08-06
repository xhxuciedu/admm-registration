#!/usr/bin/env python3
from pathlib import Path
import csv, json, time, yaml
import numpy as np
from scipy.optimize import differential_evolution
from src.candidate_roots import select_alpha, select_rho
from src.local_envelope import certified_envelope, local_envelope
from src.operators import data_hessian, periodic_laplacian, regularizer_symbol
from src.spectral_tools import reduced_matrix, spectral_radius

ROOT=Path(__file__).resolve().parents[1]
def main():
    cfg=yaml.safe_load((ROOT/'configs'/'controlled.yaml').read_text()); rng=np.random.default_rng(cfg['seed']); rows=[]
    for n in cfg['grid_sizes']:
      yy,xx=np.meshgrid(np.arange(n),np.arange(n),indexing='ij')
      for contrast in cfg['contrasts']:
       for freq in cfg['rotation_frequencies']:
        for trial in range(cfg['trials_per_setting']):
          mag=.4*(1+(contrast-1)*(xx/(n-1)))
          angle=2*np.pi*freq*yy/n + rng.normal(scale=.03,size=(n,n))
          q=np.stack([mag*np.cos(angle),mag*np.sin(angle)],-1)
          h=data_hessian(q,damping=.05).toarray(); hr=np.mean(h.reshape(-1,2,2),axis=0); ht=np.kron(np.eye(n*n),hr)
          g0=periodic_laplacian((n,n),beta=cfg['regularization_beta'],gamma=cfg['regularization_gamma']).toarray(); g=np.kron(g0,np.eye(2))
          symbol=regularizer_symbol((n,n),beta=cfg['regularization_beta'],gamma=cfg['regularization_gamma'])
          hs=np.linalg.eigvalsh(hr); corners=np.array([[x,y] for x in hs for y in (symbol.min(),symbol.max())]); delta=np.linalg.norm(h-ht,2)
          start=time.perf_counter(); rho,_,_=select_rho(corners,cfg['rho_interval'],delta); alpha,cert,_=select_alpha(corners,rho,cfg['alpha_interval'],delta); select_time=time.perf_counter()-start
          actual=spectral_radius(reduced_matrix(h,g,rho,alpha))
          exact=differential_evolution(lambda z:spectral_radius(reduced_matrix(h,g,np.exp(z[0]),z[1])),[(np.log(cfg['rho_interval'][0]),np.log(cfg['rho_interval'][1])),tuple(cfg['alpha_interval'])],seed=cfg['seed']+trial,popsize=5,maxiter=8,tol=1e-6,polish=True,workers=1)
          exact_rho=float(np.exp(exact.x[0])); exact_alpha=float(exact.x[1]); exact_radius=float(exact.fun)
          rows.append(dict(n=n,contrast=contrast,frequency=freq,trial=trial,rho=rho,alpha=alpha,delta_h=delta,local_envelope=local_envelope(corners,rho,alpha),certified_envelope=cert,actual_radius=actual,exact_joint_rho=exact_rho,exact_joint_alpha=exact_alpha,exact_joint_radius=exact_radius,relative_radius_gap=(actual-exact_radius)/exact_radius,selection_seconds=select_time,certificate_valid=actual<=cert+1e-10))
    out=ROOT/'results'/'raw'; out.mkdir(parents=True,exist_ok=True)
    with (out/'variable_coeff.csv').open('w',newline='') as f:
      w=csv.DictWriter(f,fieldnames=rows[0]); w.writeheader(); w.writerows(rows)
    vals=np.array([r['relative_radius_gap'] for r in rows]); summary={'n_cases':len(rows),'median_relative_radius_gap':float(np.median(vals)),'mean_relative_radius_gap':float(np.mean(vals)),'max_relative_radius_gap':float(np.max(vals)),'certificate_failures':sum(not r['certificate_valid'] for r in rows),'gate_threshold':cfg['gate_2_median_relative_gap'],'gate_2_passed':bool(np.median(vals)<cfg['gate_2_median_relative_gap'])}
    (ROOT/'results'/'summary.json').write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
