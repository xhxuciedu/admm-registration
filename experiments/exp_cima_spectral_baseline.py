#!/usr/bin/env python3
"""Song-style numerical spectral optimization on an 8x8 CIMA surrogate."""
from pathlib import Path
import itertools,time
import numpy as np
import pandas as pd
from scipy.ndimage import zoom
from src.metrics import jacobian_determinant_2d
from src.operators import data_hessian,periodic_laplacian
from src.oracle import dense_oracle
from src.registration2d import register,robust_translation_initialization
from experiments.exp_cima_landmarks import landmark_metrics,landmarks

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/processed/cima_lung_lesion_3';OUT=ROOT/'results/real2d_v1'

def main():
    names=sorted(p.stem for p in DATA.glob('*.npy'));rows=[]
    for pair_index,(fixed_name,moving_name) in enumerate(itertools.combinations(names,2)):
        fixed=np.load(DATA/f'{fixed_name}.npy');moving=np.load(DATA/f'{moving_name}.npy');start=time.perf_counter();initial=robust_translation_initialization(fixed,moving);initial_seconds=time.perf_counter()-start
        small=zoom(moving,np.asarray((8,8))/np.asarray(moving.shape),order=1);gy,gx=np.gradient(small);q=np.stack([gy,gx],axis=-1)
        h=data_hessian(q).toarray();g=np.kron(periodic_laplacian((8,8),.2,.05).toarray(),np.eye(2))
        tune_start=time.perf_counter();oracle=dense_oracle(h,g,(1e-4,1e3),(1e-6,2),grid_points=61);tuning=time.perf_counter()-tune_start
        result=register(fixed,moving,method='fixed',rho_fixed=oracle.rho,alpha_fixed=oracle.alpha,factors=(4,2,1),outer_iterations=8,beta=.2,gamma=.05,atol=1e-6,rtol=1e-5,max_iter=400,initial_displacement=initial)
        jac=jacobian_determinant_2d(result.displacement);metrics=landmark_metrics(result.displacement,landmarks(fixed_name),landmarks(moving_name))
        rows.append({'pair_index':pair_index,'fixed':fixed_name,'moving':moving_name,'method':'numerical_spectral_8','rho':oracle.rho,'alpha':oracle.alpha,'spectral_radius_8':oracle.radius,'rho_evaluations':oracle.rho_evaluations,'initialization_seconds':initial_seconds,'tuning_seconds':tuning,'solver_seconds':result.total_seconds,'total_seconds':initial_seconds+tuning+result.total_seconds,'inner_iterations':sum(r['inner_iterations'] for r in result.records),'min_jacobian':float(jac.min()),**metrics})
        print(pair_index,oracle.rho,oracle.alpha,'tune',tuning,'total',rows[-1]['total_seconds'],flush=True)
    pd.DataFrame(rows).to_csv(OUT/'cima_numerical_spectral_8.csv',index=False)

if __name__=='__main__':main()
