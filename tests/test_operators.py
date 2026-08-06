import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from src.metrics import compose_displacements, jacobian_determinant_2d
from src.operators import data_hessian, periodic_difference, periodic_laplacian, regularizer_symbol


def test_difference_adjoint():
    rng=np.random.default_rng(1); d=periodic_difference(12)
    x,y=rng.normal(size=12),rng.normal(size=12)
    assert abs((d@x)@y-x@(d.T@y)) < 1e-12


def test_hessian_blocks():
    q=np.array([[1.,2.],[-2.,3.]])
    got=data_hessian(q,mu=2).toarray()
    expected=np.block([[2*np.outer(q[0],q[0]),np.zeros((2,2))],[np.zeros((2,2)),2*np.outer(q[1],q[1])]])
    np.testing.assert_allclose(got,expected)


def test_fft_symbol_solve_matches_sparse():
    shape=(5,7); rho=.4
    g=periodic_laplacian(shape,beta=.7,gamma=.2)
    symbol=regularizer_symbol(shape,beta=.7,gamma=.2)
    rng=np.random.default_rng(2); b=rng.normal(size=shape)
    fft=np.fft.ifftn(np.fft.fftn(b)/(symbol+rho)).real
    direct=spsolve(g+rho*sparse.eye(np.prod(shape)),b.ravel()).reshape(shape)
    np.testing.assert_allclose(fft,direct,atol=1e-11)


def test_jacobian_and_composition_translation():
    u=np.zeros((8,9,2)); u[...,0]=.2; u[...,1]=-.1
    np.testing.assert_allclose(jacobian_determinant_2d(u),1)
    np.testing.assert_allclose(compose_displacements(u,u),2*u)
