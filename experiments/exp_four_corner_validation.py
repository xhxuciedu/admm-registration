#!/usr/bin/env python3
"""10,000-configuration validation of the global four-corner reduction."""
from pathlib import Path
import argparse,csv,json,time
from multiprocessing import Pool
import numpy as np

from src.candidate_roots import select_four_corner,select_joint_constant
from src.local_envelope import global_four_corners,local_envelope

ROOT=Path(__file__).resolve().parents[1]; SEED=20260806

def one(args):
    idx,h,g=args
    # Legacy construction enumerates every observed rank-one curvature.
    legacy=np.array([[a,b] for a in h for b in (min(g),max(g))])
    old=select_joint_constant(legacy,(1e-6,1e3))[:3]
    new=select_four_corner(h,g,(1e-6,1e3))[:3]
    # Equal objectives imply equal minimizer sets; tie-break comparison is explicit.
    same=np.allclose(old,new,rtol=2e-9,atol=2e-11)
    return idx,*old,*new,same

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--start',type=int,default=0);parser.add_argument('--count',type=int,default=2500);parser.add_argument('--merge',action='store_true');args=parser.parse_args()
    out=ROOT/'results'/'real2d_v1'
    if args.merge:
        rows=[]
        for p in sorted(out.glob('four_corner_part_*.csv')):
            with p.open() as f: rows.extend(list(csv.reader(f))[1:])
        failures=sum(str(r[-1]).lower()!='true' for r in rows)
        summary={'configurations':len(rows),'exact_parameter_matches':len(rows)-failures,'failures':failures}
        (out/'four_corner_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2));return
    rng=np.random.default_rng(SEED); jobs=[]
    for i in range(10_000):
        nu=0.0 if i%17==0 else 10**rng.uniform(-8,-1)
        magnitudes=rng.lognormal(mean=-1,sigma=1.5,size=rng.integers(1,5))
        h=np.unique(np.r_[nu,nu+magnitudes**2])
        order=1 if i%2==0 else 2; beta=10**rng.uniform(-3,1);gamma=0.0 if i%19==0 else 10**rng.uniform(-8,-1)
        g=np.array([gamma,(gamma+8*beta)**order])
        if args.start<=i<args.start+args.count:jobs.append((i,h,g))
    start=time.perf_counter()
    with Pool(processes=32) as pool: rows=pool.map(one,jobs,chunksize=20)
    elapsed=time.perf_counter()-start
    with (out/f'four_corner_part_{args.start:05d}.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['id','old_rho','old_alpha','old_value','four_rho','four_alpha','four_value','same']);w.writerows(rows)
    print(json.dumps({'start':args.start,'count':len(rows),'wall_seconds':elapsed,'failures':sum(not bool(r[-1]) for r in rows)},indent=2))
if __name__=='__main__':main()
