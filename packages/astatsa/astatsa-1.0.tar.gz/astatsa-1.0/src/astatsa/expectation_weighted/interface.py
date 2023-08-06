from abc import ABCMeta, abstractmethod
from contracts import contract

class ExpectationWeightedInterface():
    __metaclass__ = ABCMeta
    
    
    @abstractmethod
    @contract(value='array,shape(x)', weight='array(>=0),shape(x)', returns='None')
    def update(self, value, weight):
        """ 
            weight: weight for each single element. 
            if 0, ignore this value
        """
        pass

    @abstractmethod
    @contract(returns='array')
    def get_value(self):
        """ 
            Returns the value of the expectation. 
            Raises ValueError if never updated.
            
            For those weights which were never updated, return np.nan. 
        """
        pass
