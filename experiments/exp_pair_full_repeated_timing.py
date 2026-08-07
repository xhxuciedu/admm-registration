#!/usr/bin/env python3
"""Five-repeat paired timing of the validation-selected and one-shot policies."""
from pathlib import Path
import time
import numpy as np
import pandas as pd
from experiments.exp_public_sample_registration import make_pair
from src.registration2d import register

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'/'real2d_v1'

def main():
    images={p.stem:np.load(p) for p in (ROOT/'data'/'processed'/'public_samples').glob('*.npy')};rows=[]
    methods={'manual_global':dict(method='fixed',rho_fixed=.1,alpha_fixed=1.),'predict_pair_full':dict(method='predictor',reuse='pair_full')}
    for repetition in range(5):
      for image_name,fixed in images.items():
       for case in (3,4,5):
        moving,_=make_pair(fixed,case)
        # Alternate method order to reduce drift bias.
        names=list(methods) if (repetition+case)%2==0 else list(methods)[::-1]
        for name in names:
          result=register(fixed,moving,factors=(4,2,1),outer_iterations=6,beta=.2,gamma=.05,atol=1e-6,rtol=1e-5,max_iter=300,**methods[name])
          rows.append(dict(repetition=repetition,category=image_name,case=case,method=name,total_seconds=result.total_seconds,tuning_seconds=result.tuning_seconds,total_inner_iterations=sum(r['inner_iterations'] for r in result.records),mse_after=float(np.mean((result.warped-fixed)**2))))
          print(repetition,image_name,case,name,rows[-1]['total_seconds'],flush=True)
    pd.DataFrame(rows).to_csv(OUT/'pair_full_repeated_timing.csv',index=False)

if __name__=='__main__':main()
