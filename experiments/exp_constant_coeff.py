#!/usr/bin/env python3
from pathlib import Path
import json, time
import numpy as np
from src.candidate_roots import select_joint_constant
from src.local_envelope import local_envelope
from src.operators import periodic_laplacian, regularizer_symbol
from src.spectral_tools import reduced_matrix, spectral_radius

ROOT=Path(__file__).resolve().parents[1]
def main():
    rows=[]
    for n in (4,6,8):
        hvals=(.2,2.3); q=np.array([np.sqrt(2.1),0.]); block=.2*np.eye(2)+np.outer(q,q)
        h=np.kron(np.eye(n*n),block)
        g0=periodic_laplacian((n,n),beta=.2,gamma=.1).toarray(); g=np.kron(g0,np.eye(2))
        symbol=regularizer_symbol((n,n),beta=.2,gamma=.1)
        corners=np.array([[x,y] for x in hvals for y in (symbol.min(),symbol.max())])
        t=time.perf_counter(); rho,alpha,_,_=select_joint_constant(corners,(.01,100)); selection=time.perf_counter()-t
        direct=spectral_radius(reduced_matrix(h,g,rho,alpha)); envelope=local_envelope(corners,rho,alpha)
        rows.append(dict(n=n,rho=rho,alpha=alpha,direct_radius=direct,local_envelope=envelope,absolute_error=abs(direct-envelope),selection_seconds=selection))
    out=ROOT/'results'/'raw'; out.mkdir(parents=True,exist_ok=True)
    (out/'constant_coeff.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps(rows,indent=2))
if __name__=='__main__': main()
