import numpy as np
from scipy.ndimage import shift
from src.metrics import compose_displacements,jacobian_determinant_2d
from src.registration2d import invert_displacement,phase_translation_initialization,predictor_parameters,register,safeguard_displacement,solve_linearized_admm,warp_image


def blob(n=32):
    y,x=np.mgrid[:n,:n];return np.exp(-((x-n*.45)**2+(y-n*.55)**2)/(2*(n*.12)**2))


def test_block_fft_admm_converges_and_predictor_is_finite():
    image=blob(16);gy,gx=np.gradient(image);q=np.stack([gy,gx],-1);res=.1*image
    rho,alpha,value=predictor_parameters(q,image.shape,.2,.05)
    assert rho>0 and 0<alpha<=2 and value<1
    result=solve_linearized_admm(q,res,.2,.05,rho,alpha,max_iter=1000)
    assert result.converged and result.history[-1,0]<result.history[0,0]


def test_registration_reduces_real_objective_and_preserves_jacobian():
    fixed=blob();moving=shift(fixed,(1.2,-.8),order=1,mode='nearest');before=np.mean((moving-fixed)**2)
    result=register(fixed,moving,method='predictor',factors=(2,1),outer_iterations=4,max_iter=200)
    assert np.mean((result.warped-fixed)**2)<before
    assert min(r['min_jacobian'] for r in result.records)>0


def test_inverse_consistent_smooth_warp():
    shape=(40,44);y,x=np.meshgrid(np.arange(shape[0]),np.arange(shape[1]),indexing='ij')
    d=np.stack([.8*np.sin(2*np.pi*x/shape[1]),.7*np.sin(2*np.pi*y/shape[0])],axis=-1)
    inverse=invert_displacement(d);composed=compose_displacements(d,inverse)
    # Nearest-neighbour boundary extension is not bijective at the outer rim.
    assert np.max(np.abs(composed[2:-2,2:-2]))<5e-3


def test_phase_translation_initialization_direction():
    rng=np.random.default_rng(8);fixed=rng.normal(size=(40,40));moving=shift(fixed,(3,-2),order=1,mode='wrap')
    displacement=phase_translation_initialization(fixed,moving)
    np.testing.assert_allclose(displacement[0,0],[3,-2],atol=.15)


def test_displacement_safeguard_removes_folding_and_preserves_translation():
    y,x=np.mgrid[:32,:32];field=np.stack([2*np.sin(x),2*np.sin(y)],axis=-1)+np.array([3.,-2.])
    safe=safeguard_displacement(field)
    assert jacobian_determinant_2d(safe).min()>.05
    np.testing.assert_allclose(safe.mean((0,1)),field.mean((0,1)))
