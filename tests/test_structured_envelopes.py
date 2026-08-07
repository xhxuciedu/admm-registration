import numpy as np

from src.local_envelope import local_envelope
from src.operators import periodic_laplacian
from src.spectral_tools import reduced_matrix, spectral_radius
from src.structured_envelopes import (
    block_gershgorin_envelope, block_resolvent_envelope,
    block_gershgorin_disks, block_resolvent_error, cayley_blocks, select_disk_alpha,
    commutator_cayley_bound, exact_rectangle, local_rectangle_bounds, rectangle_envelope,
    select_rectangle_alpha,
    gradient_variation_measures,
    comparison_rectangle_bounds, comparison_rectangle_envelope, select_comparison_alpha,
    angular_numerical_radius_bound,
    truncated_kernel_comparison_envelope,
)


def make_system(n=4):
    rng=np.random.default_rng(20260806)
    q=rng.normal(size=(n*n,2)); q/=np.linalg.norm(q,axis=1)[:,None]; q*=np.linspace(.2,1.1,n*n)[:,None]
    blocks=np.einsum('ni,nj->nij',q,q)+.05*np.eye(2)[None]
    h=np.zeros((2*n*n,2*n*n))
    for i,b in enumerate(blocks): h[2*i:2*i+2,2*i:2*i+2]=b
    g0=periodic_laplacian((n,n),beta=.2,gamma=.1).toarray(); g=np.kron(g0,np.eye(2))
    return blocks,h,g0,g


def test_block_cayley_error_is_exact_global_norm():
    blocks,_,_,_=make_system(); mean=np.repeat(blocks.mean(0)[None],len(blocks),axis=0)
    cb,cm=cayley_blocks(blocks,.7),cayley_blocks(mean,.7)
    assert abs(block_resolvent_error(blocks,mean,.7)-max(np.linalg.norm(a-b,2) for a,b in zip(cb,cm))) < 1e-14


def test_structured_certificates_enclose_full_spectrum():
    blocks,h,g0,g=make_system(); mean_block=blocks.mean(0); mean=np.repeat(mean_block[None],len(blocks),axis=0)
    hs=np.linalg.eigvalsh(mean_block); gs=np.linalg.eigvalsh(g0); corners=np.array([[x,y] for x in hs for y in (gs.min(),gs.max())])
    for rho in (.08,.3,1.,5.):
      for alpha in (.4,1.,1.7,2.):
        actual=spectral_radius(reduced_matrix(h,g,rho,alpha))
        assert actual <= block_resolvent_envelope(corners,blocks,mean,rho,alpha)+1e-11
        assert actual <= block_gershgorin_envelope(blocks,g0,rho,alpha)+1e-11


def test_disk_alpha_finite_candidates_match_dense():
    blocks,_,g0,_=make_system(3); rho=.6
    alpha,value,_=select_disk_alpha(blocks,g0,rho)
    centers,radii=block_gershgorin_disks(blocks,g0,rho)
    grid=np.linspace(1e-6,2,20001)[:,None]
    dense=float(np.min(np.max(np.abs(1-grid/2+grid*centers/2)+grid*radii/2,axis=1)))
    assert value <= dense+2e-7


def test_local_rectangle_and_commutator_bounds():
    blocks,h,g0,g=make_system(3)
    for rho in (.2,.8,2.):
        m,M,eta=local_rectangle_bounds(blocks,g0,rho)
        me,Me,etae=exact_rectangle(blocks,g0,rho)
        assert m <= me+1e-11 and M >= Me-1e-11 and eta >= etae-1e-11
        assert np.linalg.norm(
            (np.eye(len(h))-2*rho*np.linalg.inv(h+rho*np.eye(len(h)))) @
            (np.eye(len(g))-2*rho*np.linalg.inv(g+rho*np.eye(len(g)))) -
            (np.eye(len(g))-2*rho*np.linalg.inv(g+rho*np.eye(len(g)))) @
            (np.eye(len(h))-2*rho*np.linalg.inv(h+rho*np.eye(len(h)))),2
        ) <= commutator_cayley_bound(h,g,rho)+1e-10
        for alpha in (.6,1.4,2.):
            assert spectral_radius(reduced_matrix(h,g,rho,alpha)) <= rectangle_envelope(blocks,g0,rho,alpha)+1e-10


def test_rectangle_alpha_candidates_match_dense():
    blocks,_,g0,_=make_system(3); rho=.55
    alpha,value,_=select_rectangle_alpha(blocks,g0,rho)
    grid=np.linspace(1e-6,2,20001)
    m,M,eta=local_rectangle_bounds(blocks,g0,rho)
    dense=float(np.min(np.max(np.sqrt((1-grid[:,None]/2+grid[:,None]*np.array([m,M])/2)**2+(grid[:,None]*eta/2)**2),axis=1)))
    assert value <= dense+2e-7


def test_local_rotation_variation_measures():
    q=np.array([[1.,0.],[2.,0.],[0.,2.]])
    mag,ang=gradient_variation_measures(q,[(0,1),(1,2)])
    assert mag==3.0
    np.testing.assert_allclose(ang,np.sqrt(.5))


def test_comparison_matrix_rectangle_is_rigorous_and_tighter_than_rows():
    blocks,h,g0,g=make_system(3)
    for rho in (.2,.7,2.):
        m,M,eta=comparison_rectangle_bounds(blocks,g0,rho);me,Me,etae=exact_rectangle(blocks,g0,rho)
        assert m<=me+1e-11 and M>=Me-1e-11 and eta>=etae-1e-11
        mr,Mr,etar=local_rectangle_bounds(blocks,g0,rho)
        assert m>=mr-1e-11 and M<=Mr+1e-11 and eta<=etar+1e-11
        for alpha in (.5,1.4,2.):
            assert spectral_radius(reduced_matrix(h,g,rho,alpha))<=comparison_rectangle_envelope(blocks,g0,rho,alpha)+1e-10
        a,v,_=select_comparison_alpha(blocks,g0,rho)
        assert 0<a<=2 and np.isfinite(v)


def test_angular_numerical_radius_certificate():
    blocks,h,g0,g=make_system(3)
    for rho,alpha in ((.2,1.7),(.8,1.4),(2.,2.)):
        actual=spectral_radius(reduced_matrix(h,g,rho,alpha))
        angular=angular_numerical_radius_bound(blocks,g0,rho,alpha,48)
        assert actual<=angular+1e-10
        assert angular<=comparison_rectangle_envelope(blocks,g0,rho,alpha)+.15


def test_truncated_kernel_certificate_is_rigorous():
    blocks,h,g0,g=make_system(4)
    # Use the actual FFT-ordered symbol.
    from src.operators import regularizer_symbol
    symbol=regularizer_symbol((4,4),.2,.1)
    for radius in (0,1,2):
        bound,meta=truncated_kernel_comparison_envelope(blocks,symbol,.6,1.7,radius)
        assert spectral_radius(reduced_matrix(h,g,.6,1.7))<=bound+1e-9
        assert meta['tail_l1']>=0
