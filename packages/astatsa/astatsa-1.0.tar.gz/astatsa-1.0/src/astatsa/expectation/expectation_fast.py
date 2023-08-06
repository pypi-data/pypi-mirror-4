from . import ExpectationInterface, contract, np
from astatsa.utils import check_all_finite
import warnings

__all__ = ['ExpectationFast', 'ExpectationFaster']


class ExpectationFast(ExpectationInterface):
    ''' A more efficient implementation. '''

    MAX_MASS = 100  # TODO: watch np.max(self.accum) instead

    def __init__(self, max_window=None, extremely_fast=False):
        '''  
            extremely_fast: saves memory; might crash on some python 
            interpreters
            TODO: put automatic tests to detect this
        '''
        self.max_window = max_window
        self.accum_mass = 0.0
        self.accum = None
        self.needs_normalization = True
        self.extremely_fast = extremely_fast
        
    def merge(self, other):
        warnings.warn('to test')
        assert isinstance(other, ExpectationFast)
        self.update(other.get_value(), other.accum_mass)

    @contract(cur_mass='float,>=0')
    def reset(self, cur_mass=1.0):
        self.accum = self.get_value()
        self.accum_mass = cur_mass

    @contract(value='array', dt='float,>=0')
    def update(self, value, dt=1.0):
        check_all_finite(value)

        if self.accum is None:
            self.accum = value * dt
            self.accum_mass = dt
            self.needs_normalization = True
            self.buf = np.empty_like(value)
            self.buf.fill(np.NaN)
            self.result = np.empty_like(value)
            self.result.fill(np.NaN)
        else:
            if self.extremely_fast:
                np.multiply(value, dt, self.buf)  # buf = value * dt
                np.add(self.buf, self.accum, self.accum)  # accum += buf
            else:
                self.buf = value * dt
                self.accum += self.buf

            self.needs_normalization = True
            self.accum_mass += dt

        if self.max_window and self.accum_mass > self.max_window:
            self.accum = self.max_window * self.get_value()
            self.accum_mass = self.max_window

        
        # Do not let pass too much before normalization
        if self.accum_mass > ExpectationFast.MAX_MASS:
            self.get_value()

    def get_value(self):
        if self.accum is None:
            raise ValueError('No value given yet.')
        if self.needs_normalization:
            # In the case dt=0 for the first sample
            if self.accum_mass > 0:
                ratio = 1.0 / self.accum_mass
            else:
                ratio = 1.0
            if self.extremely_fast:
                np.multiply(ratio, self.accum, self.result)
            else:
                self.result = ratio * self.accum
            self.needs_normalization = False
        return self.result

    def __call__(self):
        return self.get_value()

    def get_mass(self):
        return self.accum_mass


class ExpectationFaster(ExpectationFast):
    def __init__(self):
        ExpectationFast.__init__(self, extremely_fast=True)
        
        
        
