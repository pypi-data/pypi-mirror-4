from astatsa.expectation_weighted.expectation_weighted import ExpectationWeighted

import numpy as np
from astatsa.utils.np_comparisons import assert_allclose

def test_weighted_1():
    ex = ExpectationWeighted()
    ex.update(np.array([1, 2]), np.array([0, 0]))    
    ex.update(np.array([1, 2]), np.array([0, 0]))
    assert np.all(np.isnan(ex.get_value()))

def test_weighted_2():
    ex = ExpectationWeighted()
    ex.update(np.array([1, 1]), np.array([0, 0]))
    ex.update(np.array([1, 2]), np.array([0, 0]))
    assert_allclose(42, ex.get_value(42))

def test_weighted_3():
    ex = ExpectationWeighted()
    ex.update(np.array([1, 1]), np.array([1, 1]))
    ex.update(np.array([2, 2]), np.array([0, 0]))
    assert_allclose([1, 1], ex.get_value())
    assert_allclose([1, 1], ex.get_mass())




def test_weighted_4():
    ex = ExpectationWeighted()
    ex.update(np.array([1, 1]), np.array([0, 101]))
    ex.update(np.array([2, 2]), np.array([23, 0]))
    assert_allclose([2, 1], ex.get_value())
    assert_allclose([23, 101], ex.get_mass())


