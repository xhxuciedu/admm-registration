#!/usr/bin/env python3
"""Runtime/tightness of the rigorous truncated Cayley-kernel certificate."""
from pathlib import Path
import argparse,csv,time
import numpy as np
from src.candidate_roots import select_four_corner
from src.operators import regularizer_symbol
from src.oracle import arnoldi_radius
from src.structured_envelopes import truncated_kernel_comparison_envelope

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'/'real2d_v1'

def smooth_blocks(side):
    y,x=np.meshgrid(np.arange(side),np.arange(side),indexing='ij')
    angle=.55*np.sin(2*np.pi*x/side)*np.sin(2*np.pi*y/side)
    magnitude=.3*(1+.35*np.cos(2*np.pi*x/side))
    q=magnitude[...,None]*np.stack([np.cos(angle),np.sin(angle)],axis=-1)
    return .05*np.eye(2)[None]+np.einsum('...i,...j->...ij',q,q).reshape(-1,2,2)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sides',type=int,nargs='+',default=[8,16,32,64,128]);args=parser.parse_args()
    rows=[]
    for side in args.sides:
        blocks=smooth_blocks(side);symbol=regularizer_symbol((side,side),.2,.05)
        h=np.linalg.eigvalsh(blocks);rho,alpha,_=select_four_corner(h,[symbol.min(),symbol.max()],(1e-4,1e3))[:3]
        tol,maxiter,k=(1e-4,400,1) if side>=128 else (3e-7,1000,2)
        start=time.perf_counter();actual,_=arnoldi_radius(blocks,symbol,rho,alpha,tol=tol,maxiter=maxiter,k=k);arnoldi_seconds=time.perf_counter()-start
        for radius in (0,1,2,4,8):
            start=time.perf_counter();bound,meta=truncated_kernel_comparison_envelope(blocks,symbol,rho,alpha,radius);seconds=time.perf_counter()-start
            rows.append(dict(side=side,pixels=side*side,rho=rho,alpha=alpha,actual_radius=actual,bound=bound,valid=actual<=bound+1e-8,relative_gap=(bound-actual)/actual,certificate_seconds=seconds,arnoldi_seconds=arnoldi_seconds,**meta))
        print('side',side,'actual',actual,'rows',len(rows),flush=True)
        with (OUT/f'certificate_scaling_{side}.csv').open('w',newline='') as handle:
            local=[row for row in rows if row['side']==side]
            writer=csv.DictWriter(handle,fieldnames=local[0]);writer.writeheader();writer.writerows(local)
        with (OUT/'certificate_scaling.partial.csv').open('w',newline='') as handle:
            writer=csv.DictWriter(handle,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    with (OUT/'certificate_scaling.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    print('cases',len(rows),'violations',sum(not r['valid'] for r in rows),'max_pixels',max(r['pixels'] for r in rows))

if __name__=='__main__':main()
