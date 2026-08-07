import numpy as np
from scipy.linalg import block_diag

from src.candidate_roots import select_alpha, select_four_corner, select_joint_constant, select_rho
from src.local_envelope import certified_envelope, global_four_corners, local_envelope, theta
from src.spectral_tools import full_state_matrix, reduced_matrix, spectral_radius
from src.admm_registration import solve_quadratic


def random_spd(rng, n, floor=0.1):
    a = rng.normal(size=(n, n))
    return a.T @ a + floor * np.eye(n)


def test_full_reduced_nonzero_spectra():
    rng = np.random.default_rng(20260806)
    for alpha in (0.5, 1.0, 1.7, 2.0):
        h, g = random_spd(rng, 5), random_spd(rng, 5)
        full = np.linalg.eigvals(full_state_matrix(h, g, 0.73, alpha))
        reduced = np.linalg.eigvals(reduced_matrix(h, g, 0.73, alpha))
        nz = full[np.abs(full) > 1e-9]
        assert len(nz) == len(reduced)
        for z in reduced:
            assert np.min(np.abs(nz-z)) < 1e-8


def test_commuting_local_formula():
    h = np.diag([0.2, 2.0, 4.0]); g = np.diag([0.5, 3.0, 7.0])
    vals = np.linalg.eigvals(reduced_matrix(h, g, 1.3, 1.8))
    expected = 1 - 1.8 + 1.8 * theta(np.diag(h), np.diag(g), 1.3)
    np.testing.assert_allclose(np.sort(vals), np.sort(expected), atol=1e-12)


def test_perturbation_certificate_random_noncommuting():
    rng = np.random.default_rng(7)
    for _ in range(50):
        ht, gt = random_spd(rng, 4), random_spd(rng, 4)
        dh, dg = rng.normal(size=(4,4)), rng.normal(size=(4,4))
        dh, dg = .02*(dh+dh.T), .02*(dg+dg.T)
        h, g = ht+dh, gt+dg
        if min(np.linalg.eigvalsh(h).min(), np.linalg.eigvalsh(g).min()) < 0: continue
        rho, alpha = 0.9, 1.6
        rhs = np.linalg.norm(reduced_matrix(ht,gt,rho,alpha),2) + alpha*(np.linalg.norm(dh,2)+np.linalg.norm(dg,2))/rho
        assert spectral_radius(reduced_matrix(h,g,rho,alpha)) <= rhs + 1e-11


def test_candidates_match_dense_diagnostic():
    corners = np.array([[0.1,0.2],[0.1,8.0],[3.0,0.2],[3.0,8.0]])
    lohi=(0.05,20.0); delta=.03
    rho, value, _ = select_rho(corners, lohi, delta)
    grid=np.geomspace(*lohi, 200000)
    dense=min(certified_envelope(corners,r,1,delta,0) for r in grid)
    assert value <= dense + 2e-7
    alpha, avalue, _ = select_alpha(corners,rho,(1e-6,2),delta)
    agrid=np.linspace(1e-6,2,100000)
    adense=min(certified_envelope(corners,rho,a,delta,0) for a in agrid)
    assert avalue <= adense + 2e-7


def test_solver_stopping_rules_and_objective():
    h=np.diag([0.3,2.0]); g=np.diag([1.1,0.4]); b=np.array([-1.0,.7])
    result=solve_quadratic(h,g,b,rho=.8,alpha=1.5,atol=1e-10,rtol=1e-9)
    exact=np.linalg.solve(h+g,-b)
    assert result['converged']
    np.testing.assert_allclose(result['v'],exact,rtol=1e-7,atol=1e-9)
    assert result['history'][-1,0] < 1e-8


def test_joint_constant_candidates_match_dense_2d_search():
    corners=np.array([[.05,.1],[.05,2.],[1.7,.1],[1.7,2.]])
    rho,alpha,value,_=select_joint_constant(corners,(.01,10.))
    rgrid=np.geomspace(.01,10,1600); agrid=np.linspace(1e-6,2,1200)
    dense=np.inf
    for r in rgrid:
        t=theta(corners[:,0],corners[:,1],r)
        dense=min(dense,float(np.min(np.max(np.abs(1-agrid[:,None]+agrid[:,None]*t),axis=1))))
    assert value <= dense+2e-5


def test_four_corner_envelope_equals_all_pixel_curvatures():
    rng=np.random.default_rng(20260806)
    for _ in range(500):
        h=np.r_[0.0,rng.lognormal(size=rng.integers(2,20))]
        g=np.r_[0.0,rng.lognormal(size=rng.integers(2,20))]
        all_corners=np.array([[a,b] for a in h for b in (g.min(),g.max())])
        four=global_four_corners(h,g)
        for rho,alpha in zip(rng.lognormal(size=3),rng.uniform(1e-4,2,size=3)):
            np.testing.assert_allclose(local_envelope(all_corners,rho,alpha),local_envelope(four,rho,alpha),atol=2e-15)


def test_four_corner_degenerate_and_nullspace_cases():
    for h,g in (([0,0],[0,2]),([0,1],[0,0]),([1,1],[2,2]),([0,1e-14],[0,1e-12])):
        rho,alpha,value,candidates=select_four_corner(h,g,(1e-8,10))
        assert 1e-8<=rho<=10 and 0<alpha<=2 and np.isfinite(value)
        assert len(candidates)>=2
