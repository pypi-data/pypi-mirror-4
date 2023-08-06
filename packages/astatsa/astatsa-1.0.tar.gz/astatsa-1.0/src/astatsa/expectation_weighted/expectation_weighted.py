from astatsa.expectation_weighted.interface import ExpectationWeightedInterface
from astatsa.utils.np_comparisons import check_all_finite
from contracts import contract
import numpy as np
import warnings
 
 
class ExpectationWeighted(ExpectationWeightedInterface):
    ''' 
        This operator allows, for each time step, to give a different weight
        to each element. The weight tensor should have the same shape as the value.
     '''
 
    def __init__(self):
        self.mass = None
        self.accum = None
         
        self._result = None
         
    def merge(self, other):
        warnings.warn('To test')
        assert isinstance(other, ExpectationWeighted)
        self.update(other.get_value(), other.get_mass())
        
        
    @contract(value='array,shape(x)', weight='array(>=0),shape(x)')
    def update(self, value, weight):
        check_all_finite(value)
        check_all_finite(weight)
        assert value.shape == weight.shape
         
        # If first time
        if self.accum is None:
            self.accum = (value * weight).astype('float64')
            self.mass = weight.astype('float64')
            self._result = None
        else:
            self.accum += value * weight
            self.mass += weight
            self._result = None
 
    def get_value(self, fill_value=np.nan):
        """ Returns the value of the expectation. Raises ValueError if never updated. """
        if self.accum is None:
            msg = 'No value given yet.'
            raise ValueError(msg)
 
        if self._result is not None:
            return self._result
        
        self._result = self._compute_value(fill_value)
        return self._result
    
    def _compute_value(self, fill_value):
        zeros = self.mass == 0
        mass = self.mass.copy()
        # set to one the mass
        mass[zeros] = 1
        result = self.accum / mass
        result[zeros] = fill_value 
        return result.copy()
 
    def get_mass(self):
        return self.mass.copy()
