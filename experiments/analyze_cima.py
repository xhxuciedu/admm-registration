#!/usr/bin/env python3
from pathlib import Path
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'/'real2d_v1';FIG=ROOT/'figures';SEED=20260806

def ci(values,repetitions=10000):
    x=np.asarray(values,float);rng=np.random.default_rng(SEED);draw=rng.choice(x,(repetitions,len(x)),replace=True)
    return np.quantile(np.median(draw,axis=1),[.025,.975]).tolist()

def main():
    data=pd.read_csv(OUT/'cima_landmarks_part_00.csv');summary={}
    for method,z in data.groupby('method'):
        summary[method]={'pairs':len(z),'median_tre_px':float(z.median_tre.median()),'median_rtre':float(z.median_rtre.median()),'median_landmark_improvement':float(z.landmark_improvement.median()),'median_total_seconds':float(z.total_seconds.median()),'median_solver_seconds':float(z.solver_seconds.median()),'median_iterations':float(z.inner_iterations.median()),'tuning_fraction':float(z.tuning_seconds.sum()/z.total_seconds.sum()),'global_folding_cases':int((z.min_jacobian<=0).sum())}
    timing_path=OUT/'cima_repeated_timing.csv'
    if timing_path.exists():
        timing=pd.read_csv(timing_path);keys=['repetition','pair_index'];p=timing[timing.method=='predict_pair_full'].set_index(keys);b=timing[timing.method=='manual_external'].set_index(keys)
        runtime=1-p.total_seconds/b.total_seconds;solver=1-p.solver_seconds/b.solver_seconds;iterations=1-p.inner_iterations/b.inner_iterations
        summary['_paired_repeated']={'paired_runs':len(p),'repetitions':int(timing.repetition.nunique()),'median_total_reduction':float(np.median(runtime)),'total_reduction_ci95':ci(runtime),'median_solver_reduction':float(np.median(solver)),'solver_reduction_ci95':ci(solver),'median_iteration_reduction':float(np.median(iterations)),'iteration_reduction_ci95':ci(iterations),'tuning_fraction':float(p.tuning_seconds.sum()/p.total_seconds.sum()),'global_folding_cases':int((p.min_jacobian<=0).sum()),'interior_folding_cases':int((p.min_interior_jacobian<=0).sum())}
    spectral_path=OUT/'cima_numerical_spectral_8.csv'
    if spectral_path.exists():
        spectral=pd.read_csv(spectral_path);summary['_numerical_spectral_8']={'pairs':len(spectral),'median_rho_evaluations':float(spectral.rho_evaluations.median()),'median_tuning_seconds':float(spectral.tuning_seconds.median()),'median_total_seconds':float(spectral.total_seconds.median()),'median_iterations':float(spectral.inner_iterations.median()),'median_tre_px':float(spectral.median_tre.median())}
    (OUT/'cima_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    pivot=data.pivot(index='pair_index',columns='method',values='median_tre');fig,axes=plt.subplots(1,2,figsize=(9,3.6));axes[0].plot(pivot.index,pivot.predict_pair_full,'o-',label='registered');axes[0].plot(data[data.method=='predict_pair_full'].pair_index,data[data.method=='predict_pair_full'].initial_tre,'o--',label='initial');axes[0].set(xlabel='CIMA pair',ylabel='Median TRE (px)');axes[0].legend();med=data.groupby('method').total_seconds.median().sort_values();axes[1].barh(med.index,med);axes[1].set_xlabel('Median total time (s)');fig.tight_layout();fig.savefig(FIG/'cima_landmarks_runtime.pdf');plt.close(fig);print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
