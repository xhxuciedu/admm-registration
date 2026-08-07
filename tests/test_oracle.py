import numpy as np
from src.local_envelope import theta
from src.oracle import arnoldi_radius,dense_oracle,exact_conditional_alpha,periodic_reduced_operator
from src.operators import periodic_laplacian,regularizer_symbol
from src.spectral_tools import reduced_matrix,spectral_radius


def test_conditional_alpha_matches_dense_grid_for_complex_modes():
    lam=np.array([.2+.3j,-.4+.1j,.8-.2j]);a,v,_=exact_conditional_alpha(lam)
    grid=np.linspace(1e-6,2,200001);dense=np.min(np.max(np.abs(1+grid[:,None]*(lam-1)/2),axis=1))
    assert v<=dense+2e-6


def test_matrix_free_periodic_operator_equals_dense():
    n=4;rng=np.random.default_rng(4);q=rng.normal(size=(n*n,2));blocks=np.einsum('ni,nj->nij',q,q)+.05*np.eye(2)[None]
    h=np.zeros((2*n*n,2*n*n))
    for i,b in enumerate(blocks):h[2*i:2*i+2,2*i:2*i+2]=b
    g0=periodic_laplacian((n,n),.2,.1).toarray();g=np.kron(g0,np.eye(2));symbol=regularizer_symbol((n,n),.2,.1)
    rho,alpha=.4,1.7;op=periodic_reduced_operator(blocks,symbol,rho,alpha);dense=reduced_matrix(h,g,rho,alpha)
    x=rng.normal(size=2*n*n);np.testing.assert_allclose(op@x,dense@x,atol=2e-12)
    ar,_=arnoldi_radius(blocks,symbol,rho,alpha);assert abs(ar-spectral_radius(dense))<1e-8


def test_dense_oracle_beats_diagnostic_grid():
    h=np.diag([.05,.3,1.2]);g=np.diag([.1,.8,2.]);o=dense_oracle(h,g,(.01,10),grid_points=61)
    rhos=np.geomspace(.01,10,200);best=1
    for r in rhos:
        lam=np.linalg.eigvals(np.eye(3)-2*r*np.linalg.inv(h+r*np.eye(3))) * np.linalg.eigvals(np.eye(3)-2*r*np.linalg.inv(g+r*np.eye(3)))
        best=min(best,exact_conditional_alpha(lam)[1])
    assert o.radius<=best+1e-7
