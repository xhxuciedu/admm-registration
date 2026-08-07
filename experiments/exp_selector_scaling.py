#!/usr/bin/env python3
"""Measure four-corner selector cost versus pixels and legacy branch count."""
from pathlib import Path
import csv,time
import numpy as np
from src.candidate_roots import select_four_corner,select_joint_constant

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'/'real2d_v1'

def median_time(fn,repetitions=9):
    values=[]
    for _ in range(repetitions):
        start=time.perf_counter_ns();fn();values.append((time.perf_counter_ns()-start)/1e6)
    return float(np.median(values))

def main():
    rng=np.random.default_rng(20260806);rows=[];g=(.05,1.65)
    for side in (8,16,32,64,128,256,512,1024):
        h=np.r_[.05,.05+rng.lognormal(-2,1,size=side*side)]
        elapsed=median_time(lambda:select_four_corner(h,g,(1e-4,1e3)))
        rows.append(dict(study='image_scaling',side=side,pixels=side*side,unique_curvatures=len(np.unique(h)),milliseconds=elapsed))
    # Legacy complexity is governed by distinct curvature branches, not pixels.
    for count in (2,4,8,16):
        h=np.geomspace(.01,10,count);corners=np.array([[a,b] for a in h for b in g])
        elapsed=median_time(lambda:select_joint_constant(corners,(1e-4,1e3)),3)
        rows.append(dict(study='legacy_branch_scaling',side='',pixels='',unique_curvatures=count,milliseconds=elapsed))
    with (OUT/'selector_scaling.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    for row in rows:print(row,flush=True)

if __name__=='__main__':main()
