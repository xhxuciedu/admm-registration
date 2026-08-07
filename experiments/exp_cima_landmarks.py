#!/usr/bin/env python3
"""CIMA lung-lesion sample: real differently stained landmark registration."""
from pathlib import Path
import argparse,itertools,json,time
import numpy as np
import pandas as pd
from scipy.ndimage import map_coordinates
from src.metrics import jacobian_determinant_2d
from src.registration2d import register,robust_translation_initialization

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/processed/cima_lung_lesion_3';OUT=ROOT/'results/real2d_v1'
METHODS={
 'fixed_1_1':dict(method='fixed',rho_fixed=1.,alpha_fixed=1.),
 'fixed_1_18':dict(method='fixed',rho_fixed=1.,alpha_fixed=1.8),
 'manual_external':dict(method='fixed',rho_fixed=.1,alpha_fixed=1.),
 'residual_balance':dict(method='residual_balance',rho_fixed=1.,alpha_fixed=1.),
 'adaptive_bb_proxy':dict(method='adaptive_bb',rho_fixed=1.,alpha_fixed=1.),
 'predict_per_level':dict(method='predictor',reuse='level'),
 'predict_pair_full':dict(method='predictor',reuse='pair_full'),
}

def landmarks(name):return pd.read_csv(DATA/f'{name}.csv')[['X','Y']].to_numpy(float)

def landmark_metrics(displacement,fixed_points,moving_points):
    # displacement components are (dy,dx), while landmark files are (x,y).
    coords=np.vstack([fixed_points[:,1],fixed_points[:,0]])
    dy=map_coordinates(displacement[...,0],coords,order=1,mode='nearest');dx=map_coordinates(displacement[...,1],coords,order=1,mode='nearest')
    predicted=fixed_points+np.stack([dx,dy],axis=1);errors=np.linalg.norm(predicted-moving_points,axis=1)
    initial=np.linalg.norm(fixed_points-moving_points,axis=1);diagonal=np.sqrt(2)*256
    return {'initial_tre':float(np.median(initial)),'median_tre':float(np.median(errors)),'mean_tre':float(np.mean(errors)),'p95_tre':float(np.quantile(errors,.95)),'median_rtre':float(np.median(errors)/diagonal),'landmark_improvement':float(1-np.median(errors)/np.median(initial))}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--start',type=int,default=0);parser.add_argument('--count',type=int,default=10);args=parser.parse_args()
    names=sorted(p.stem for p in DATA.glob('*.npy'));pairs=list(itertools.combinations(names,2))[args.start:args.start+args.count];rows=[]
    for pair_index,(fixed_name,moving_name) in enumerate(pairs,start=args.start):
      fixed=np.load(DATA/f'{fixed_name}.npy');moving=np.load(DATA/f'{moving_name}.npy');fixed_points=landmarks(fixed_name);moving_points=landmarks(moving_name)
      assert len(fixed_points)==len(moving_points)
      init_start=time.perf_counter();initial=robust_translation_initialization(fixed,moving);initial_seconds=time.perf_counter()-init_start
      for method,kwargs in METHODS.items():
        result=register(fixed,moving,factors=(4,2,1),outer_iterations=8,beta=.2,gamma=.05,atol=1e-6,rtol=1e-5,max_iter=400,initial_displacement=initial,**kwargs)
        jac=jacobian_determinant_2d(result.displacement);metrics=landmark_metrics(result.displacement,fixed_points,moving_points)
        rows.append({'pair_index':pair_index,'fixed':fixed_name,'moving':moving_name,'method':method,'initialization_seconds':initial_seconds,'solver_seconds':result.total_seconds,'total_seconds':initial_seconds+result.total_seconds,'tuning_seconds':result.tuning_seconds,'inner_iterations':sum(r['inner_iterations'] for r in result.records),'failed_subproblems':sum(not r['inner_converged'] for r in result.records),'accepted_steps':sum(r['accepted'] for r in result.records),'subproblems':len(result.records),'min_jacobian':float(jac.min()),'nonpositive_jacobian_fraction':float(np.mean(jac<=0)),**metrics})
        print(pair_index,method,'TRE',metrics['median_tre'],'time',result.total_seconds,flush=True)
    path=OUT/f'cima_landmarks_part_{args.start:02d}.csv';pd.DataFrame(rows).to_csv(path,index=False)
    print(json.dumps({'pairs':len(pairs),'rows':len(rows),'path':str(path)},indent=2))

if __name__=='__main__':main()
