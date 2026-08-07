#!/usr/bin/env python3
"""Five paired CIMA timing repetitions with common image-only initialization."""
from pathlib import Path
import itertools,time
import numpy as np
import pandas as pd
from src.metrics import jacobian_determinant_2d
from src.registration2d import register,robust_translation_initialization

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/processed/cima_lung_lesion_3';OUT=ROOT/'results/real2d_v1'
METHODS={'manual_external':dict(method='fixed',rho_fixed=.1,alpha_fixed=1.),'predict_pair_full':dict(method='predictor',reuse='pair_full')}

def main():
    names=sorted(p.stem for p in DATA.glob('*.npy'));rows=[]
    for repetition in range(5):
      for pair_index,(fixed_name,moving_name) in enumerate(itertools.combinations(names,2)):
        fixed=np.load(DATA/f'{fixed_name}.npy');moving=np.load(DATA/f'{moving_name}.npy');start=time.perf_counter();initial=robust_translation_initialization(fixed,moving);initial_seconds=time.perf_counter()-start
        order=list(METHODS) if (repetition+pair_index)%2==0 else list(METHODS)[::-1]
        for method in order:
          result=register(fixed,moving,factors=(4,2,1),outer_iterations=8,beta=.2,gamma=.05,atol=1e-6,rtol=1e-5,max_iter=400,initial_displacement=initial,**METHODS[method]);jac=jacobian_determinant_2d(result.displacement)
          rows.append({'repetition':repetition,'pair_index':pair_index,'method':method,'initialization_seconds':initial_seconds,'solver_seconds':result.total_seconds,'total_seconds':initial_seconds+result.total_seconds,'tuning_seconds':result.tuning_seconds,'inner_iterations':sum(r['inner_iterations'] for r in result.records),'min_jacobian':float(jac.min()),'min_interior_jacobian':float(jac[2:-2,2:-2].min()),'nonpositive_fraction':float(np.mean(jac<=0))})
          print(repetition,pair_index,method,rows[-1]['total_seconds'],flush=True)
    pd.DataFrame(rows).to_csv(OUT/'cima_repeated_timing.csv',index=False)

if __name__=='__main__':main()
