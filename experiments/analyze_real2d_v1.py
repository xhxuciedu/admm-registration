#!/usr/bin/env python3
"""Predeclared paired analysis and publication figures for real2d_v1."""
from pathlib import Path
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'/'real2d_v1';FIG=ROOT/'figures'
SEED=20260806

def paired_ci(values,repetitions=10000):
    x=np.asarray(values,float);rng=np.random.default_rng(SEED)
    draws=rng.choice(x,(repetitions,len(x)),replace=True)
    return np.quantile(np.median(draws,axis=1),[.025,.975]).tolist()

def main():
    df=pd.read_csv(OUT/'public_sample_registration.csv');keys=['category','case']
    med=df.groupby('method').median(numeric_only=True)
    practical=[m for m in med.index if not m.startswith('predict')]
    best_accuracy=float(med.loc[practical,'mse_after'].min())
    matched=[m for m in practical if med.loc[m,'mse_after']<=1.01*best_accuracy]
    baseline=min(matched,key=lambda m:med.loc[m,'total_seconds'])
    decision={'n_pairs':int(df[keys].drop_duplicates().shape[0]),'strongest_matched_practical_baseline':baseline,'policies':{}}
    right=df[df.method==baseline].set_index(keys)
    for proposed in ('predict_every_outer','predict_per_level','predict_per_pair','predict_pair_full'):
      left=df[df.method==proposed].set_index(keys);pair=left.join(right,lsuffix='_p',rsuffix='_b')
      runtime_reduction=1-pair.total_seconds_p/pair.total_seconds_b;iteration_reduction=1-pair.total_inner_iterations_p/pair.total_inner_iterations_b;accuracy_change=(pair.mse_after_p-pair.mse_after_b)/(pair.mse_after_b+1e-15)
      item={'median_runtime_reduction':float(np.median(runtime_reduction)),'runtime_reduction_ci95':paired_ci(runtime_reduction),'median_iteration_reduction':float(np.median(iteration_reduction)),'iteration_reduction_ci95':paired_ci(iteration_reduction),'median_relative_mse_change':float(np.median(accuracy_change)),'relative_mse_change_ci95':paired_ci(accuracy_change),'predictor_overhead_fraction':float(left.tuning_seconds.sum()/left.total_seconds.sum()),'nonpositive_jacobian_cases':int((left.nonpositive_jacobian_fraction>0).sum())}
      item['predeclared_gates']={'iterations_15pct':item['median_iteration_reduction']>=.15,'runtime_10pct':item['median_runtime_reduction']>=.10,'accuracy_within_1pct':item['median_relative_mse_change']<=.01,'overhead_below_2pct':item['predictor_overhead_fraction']<=.02,'no_foldings':item['nonpositive_jacobian_cases']==0};decision['policies'][proposed]=item
    repeated_path=OUT/'pair_full_repeated_timing.csv'
    if repeated_path.exists():
      repeated=pd.read_csv(repeated_path);index=['repetition','category','case'];p=repeated[repeated.method=='predict_pair_full'].set_index(index);b=repeated[repeated.method=='manual_global'].set_index(index)
      runtime=1-p.total_seconds/b.total_seconds;iterations=1-p.total_inner_iterations/b.total_inner_iterations;mse=(p.mse_after-b.mse_after)/(b.mse_after+1e-15)
      decision['repeated_timing']={'n_paired_runs':len(p),'repetitions':int(repeated.repetition.nunique()),'median_runtime_reduction':float(np.median(runtime)),'runtime_reduction_ci95':paired_ci(runtime),'median_iteration_reduction':float(np.median(iterations)),'iteration_reduction_ci95':paired_ci(iterations),'median_relative_mse_change':float(np.median(mse)),'mse_change_ci95':paired_ci(mse),'aggregate_tuning_fraction':float(p.tuning_seconds.sum()/p.total_seconds.sum())}
    (OUT/'held_out_decision.json').write_text(json.dumps(decision,indent=2)+'\n')
    order=med.sort_values('total_seconds').index;fig,axes=plt.subplots(1,2,figsize=(9,3.6))
    axes[0].barh(order,med.loc[order,'total_seconds']);axes[0].set_xlabel('Median total time (s)')
    axes[1].barh(order,med.loc[order,'total_inner_iterations']);axes[1].set_xlabel('Median inner iterations')
    fig.tight_layout();fig.savefig(FIG/'real2d_runtime_iterations.pdf');plt.close(fig)
    print(json.dumps(decision,indent=2))

if __name__=='__main__':main()
