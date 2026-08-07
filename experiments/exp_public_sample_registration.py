#!/usr/bin/env python3
"""Registration on public-domain retina/histology content with known warps."""
from pathlib import Path
import csv,json,time
import numpy as np
import pandas as pd
from skimage.metrics import structural_similarity

from src.metrics import jacobian_determinant_2d
from src.registration2d import invert_displacement,register,warp_image

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'/'real2d_v1';SEED=20260806

def deformation(shape,amplitude,phase):
    y,x=np.meshgrid(np.arange(shape[0]),np.arange(shape[1]),indexing='ij');yn=y/(shape[0]-1);xn=x/(shape[1]-1)
    d=np.empty((*shape,2));d[...,0]=amplitude*np.sin(2*np.pi*xn+phase)*np.sin(np.pi*yn);d[...,1]=amplitude*np.sin(2*np.pi*yn-phase)*np.sin(np.pi*xn)
    return d

def ncc(a,b):
    a=a-a.mean();b=b-b.mean();return float((a*b).sum()/(np.linalg.norm(a)*np.linalg.norm(b)+1e-15))

def bootstrap_median(values,rng,reps=2000):
    x=np.asarray(values);samples=rng.choice(x,(reps,len(x)),replace=True);return np.quantile(np.median(samples,axis=1),[.025,.975]).tolist()

def make_pair(fixed,case):
    gt=deformation(fixed.shape,2+case,phase=.37*case)
    # If phi(x)=x+gt(x), moving=fixed o phi^{-1}, so moving o phi=fixed.
    moving=warp_image(fixed,invert_displacement(gt))
    return moving,gt

def select_manual_parameters(images):
    """Select one global fixed pair using validation cases 1--2 only."""
    saved=OUT/'manual_validation_summary.csv'
    if saved.exists():
        score=pd.read_csv(saved);eligible=score[score.median_mse<=1.01*score.median_mse.min()]
        chosen=eligible.sort_values(['median_iterations','median_mse']).iloc[0]
        return float(chosen.rho),float(chosen.alpha)
    rows=[]
    candidates=[(.03,1.),(.03,1.8),(.1,1.),(.1,1.8),(.3,1.),(.3,1.8),(1.,1.),(1.,1.8),(3.,1.),(3.,1.8)]
    for rho,alpha in candidates:
      for image_name,fixed in images.items():
       for case in (1,2):
        moving,_=make_pair(fixed,case)
        result=register(fixed,moving,method='fixed',rho_fixed=rho,alpha_fixed=alpha,factors=(4,2,1),outer_iterations=4,beta=.2,gamma=.05,atol=1e-6,rtol=1e-5,max_iter=250)
        rows.append(dict(category=image_name,case=case,rho=rho,alpha=alpha,total_seconds=result.total_seconds,total_inner_iterations=sum(r['inner_iterations'] for r in result.records),mse=float(np.mean((result.warped-fixed)**2))))
    frame=pd.DataFrame(rows);score=frame.groupby(['rho','alpha']).agg(median_iterations=('total_inner_iterations','median'),median_mse=('mse','median')).reset_index()
    eligible=score[score.median_mse<=1.01*score.median_mse.min()]
    chosen=eligible.sort_values(['median_iterations','median_mse']).iloc[0]
    frame.to_csv(OUT/'manual_validation_raw.csv',index=False);score.to_csv(OUT/'manual_validation_summary.csv',index=False)
    return float(chosen.rho),float(chosen.alpha)

def main():
    images={p.stem:np.load(p) for p in (ROOT/'data'/'processed'/'public_samples').glob('*.npy')};rows=[]
    manual_rho,manual_alpha=select_manual_parameters(images)
    methods=[('fixed_1_1',dict(method='fixed',rho_fixed=1,alpha_fixed=1)),('fixed_1_18',dict(method='fixed',rho_fixed=1,alpha_fixed=1.8)),('manual_global',dict(method='fixed',rho_fixed=manual_rho,alpha_fixed=manual_alpha)),('residual_balance',dict(method='residual_balance',rho_fixed=1,alpha_fixed=1)),('adaptive_bb_proxy',dict(method='adaptive_bb',rho_fixed=1,alpha_fixed=1)),('predict_every_outer',dict(method='predictor',reuse='outer')),('predict_per_level',dict(method='predictor',reuse='level')),('predict_per_pair',dict(method='predictor',reuse='pair')),('predict_pair_full',dict(method='predictor',reuse='pair_full'))]
    # Two warm-up calls excluded from timing.
    sample=next(iter(images.values()));moving,_=make_pair(sample,1)
    for _ in range(2):register(sample,moving,method='predictor',factors=(4,2,1),outer_iterations=2,max_iter=100)
    result_path=OUT/'public_sample_registration.csv'
    if result_path.exists():rows=pd.read_csv(result_path).to_dict('records')
    completed={(r['category'],int(r['case']),r['method']) for r in rows}
    for image_name,fixed in images.items():
      for case in range(3,6):
        moving,gt=make_pair(fixed,case);before_mse=float(np.mean((moving-fixed)**2));before_ncc=ncc(fixed,moving)
        for method,kwargs in methods:
          if (image_name,case,method) in completed:continue
          result=register(fixed,moving,factors=(4,2,1),outer_iterations=6,beta=.2,gamma=.05,atol=1e-6,rtol=1e-5,max_iter=300,**kwargs)
          jac=jacobian_determinant_2d(result.displacement);disp_rmse=float(np.sqrt(np.mean((result.displacement-gt)**2)))
          rows.append(dict(category=image_name,case=case,method=method,total_seconds=result.total_seconds,tuning_seconds=result.tuning_seconds,total_inner_iterations=sum(r['inner_iterations'] for r in result.records),subproblems=len(result.records),failed_subproblems=sum(not r['inner_converged'] for r in result.records),mse_before=before_mse,mse_after=float(np.mean((result.warped-fixed)**2)),ncc_before=before_ncc,ncc_after=ncc(fixed,result.warped),ssim_after=float(structural_similarity(fixed,result.warped,data_range=1)),displacement_rmse=disp_rmse,min_jacobian=float(jac.min()),nonpositive_jacobian_fraction=float(np.mean(jac<=0)),accepted_steps=sum(r['accepted'] for r in result.records)))
    with result_path.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    df=pd.DataFrame(rows);summary={};rng=np.random.default_rng(SEED)
    for method,z in df.groupby('method'):
      summary[method]={'n':len(z),'median_total_seconds':float(z.total_seconds.median()),'iqr_total_seconds':np.quantile(z.total_seconds,[.25,.75]).tolist(),'median_total_inner_iterations':float(z.total_inner_iterations.median()),'median_mse_after':float(z.mse_after.median()),'median_ncc_after':float(z.ncc_after.median()),'median_ssim_after':float(z.ssim_after.median()),'median_displacement_rmse':float(z.displacement_rmse.median()),'min_jacobian':float(z.min_jacobian.min()),'failure_rate':float(np.mean(z.failed_subproblems>0)),'tuning_fraction':float(z.tuning_seconds.sum()/z.total_seconds.sum()),'runtime_median_ci95':bootstrap_median(z.total_seconds,rng),'iterations_median_ci95':bootstrap_median(z.total_inner_iterations,rng)}
    summary['_design']={'validation_cases':[1,2],'held_out_cases':[3,4,5],'manual_rho':manual_rho,'manual_alpha':manual_alpha,'adaptive_bb_note':'safeguarded BB proxy; not claimed as Xu et al. AADMM'}
    (OUT/'public_sample_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
