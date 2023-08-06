
__all__ = ['Expectation', 'ExpectationSlow', 'ExpectationFast']

from contracts import contract
import numpy as np

from .interface import ExpectationInterface
from .expectation_fast import ExpectationFast, ExpectationFaster
from .expectation_slow import ExpectationSlow 

Expectation = ExpectationFast
