import numpy as np
from src.operators import periodic_laplacian
from src.selector import predict_then_certify, select_hierarchy


def test_hierarchy_returns_rigorous_status_and_finite_parameters():
    n=3; block=np.diag([.05,.21]); blocks=np.repeat(block[None],n*n,axis=0)
    g0=periodic_laplacian((n,n),beta=.2,gamma=.1).toarray(); ge=np.linalg.eigvalsh(g0)
    corners=np.array([[h,g] for h in np.diag(block) for g in (ge.min(),ge.max())])
    result=select_hierarchy(blocks,g0,corners)
    assert result.status in {'CERTIFIED_TIGHT','CERTIFIED_CONSERVATIVE','UNCERTIFIABLE'}
    assert .01 <= result.rho <= 100 and 0 < result.alpha <= 2
    assert np.isfinite(result.envelope)
    predicted=predict_then_certify(blocks,g0,corners)
    assert predicted.status=='CERTIFIED_USEFUL'
    assert predicted.envelope<1
