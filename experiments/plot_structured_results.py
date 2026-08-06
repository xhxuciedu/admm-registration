#!/usr/bin/env python3
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; out=ROOT/'figures';out.mkdir(exist_ok=True)

x=pd.read_csv(ROOT/'results'/'raw'/'structured_envelopes.csv')
order=['local_predictor','block_resolvent','block_gershgorin','commutator_rectangle','comparison_rectangle']
labels=['mean local\n(predictive)','block\nresolvent','block\nGershgorin','row-sum\nrectangle','comparison\nrectangle']
fig,ax=plt.subplots(figsize=(7.2,3.4))
data=[x[x.method==m].relative_radius_gap for m in order]
ax.boxplot(data,tick_labels=labels,showfliers=True);ax.axhline(.1,color='tab:red',ls='--',lw=1,label='quality gate')
ax.set_ylabel('relative spectral-radius gap');ax.legend(frameon=False);fig.tight_layout();fig.savefig(out/'structured_parameter_gaps.pdf');plt.close(fig)

x=pd.read_csv(ROOT/'results'/'raw'/'variation_regimes.csv'); methods=['pixel_curvature_predictor','block_resolvent','block_gershgorin','commutator_rectangle']
fig,ax=plt.subplots(figsize=(6.4,3.5))
data=[x[(x.method==m)&x.smooth].parameter_gap for m in methods]
ax.boxplot(data,tick_labels=['pixel\ncurvatures','block\nresolvent','block\nGershgorin','commutator\nrectangle']);ax.axhline(.1,color='tab:red',ls='--',lw=1)
ax.set_ylabel('smooth-field parameter gap');fig.tight_layout();fig.savefig(out/'smooth_parameter_gaps.pdf');plt.close(fig)

z=x[(x.method=='predict_then_certify')&x.smooth]
fig,ax=plt.subplots(figsize=(5.8,3.4));pos=range(len(z))
ax.plot(pos,z.actual_radius,'o-',label='exact radius');ax.plot(pos,z.bound,'s-',label='rigorous certificate');ax.axhline(1,color='tab:red',ls='--',lw=1,label='convergence threshold')
ax.set_xlabel('smooth synthetic case');ax.set_ylabel('convergence factor / bound');ax.legend(frameon=False,ncol=2);fig.tight_layout();fig.savefig(out/'predict_then_certify.pdf');plt.close(fig)
