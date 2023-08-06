from astatsa.expectation import ExpectationFast, ExpectationSlow
import numpy as np
from astatsa.utils import assert_allclose
from .test_doubt import check_my_doubt
from astatsa.expectation import ExpectationFaster


def test_efficient_exp():
    shape = (4, 4)
    for exp_class in [ExpectationSlow, ExpectationFast, ExpectationFaster]:
        yield check_expectation_one, exp_class

        sequence = (np.random.randn(*shape) for i in range(1))
        yield check_efficient_exp, exp_class, sequence

        sequence = (np.random.randn(*shape) for i in range(5))
        yield check_efficient_exp, exp_class, sequence

        sequence = (np.random.randn(*shape) for i in range(1000))
        yield check_efficient_exp, exp_class, sequence

        yield check_my_doubt, exp_class


def check_expectation_one(exp_class):
    e = exp_class()
    x = np.random.rand(2, 2)
    dt = np.random.rand()
    e.update(x, dt)
    v = e.get_value()
    assert_allclose(v, x)


def check_efficient_exp(exp_class, sequence):
    """ Checks that the dt is working ok. """
    exp1 = exp_class()
    xs = []
    T = 0
    for x in sequence:
        dt = np.random.rand()
        xs.append(x * dt)
        T += dt
        exp1.update(x, dt=dt)

    es1 = exp1.get_value()
    expected = np.array(xs).sum(axis=0) / T

    assert_allclose(es1, expected)



