import numpy as np 
from contracts import contract

from astatsa.expectation import Expectation
from astatsa.mean_variance import MeanVariance


__all__ = ['PredictionStats']


class  PredictionStats:

    @contract(label_a='str', label_b='str')
    def __init__(self, label_a='a', label_b='b'):
        self.label_a = label_a
        self.label_b = label_b
        self.Ea = MeanVariance()
        self.Eb = MeanVariance()
        self.Edadb = Expectation()
        self.R = None
        self.R_needs_update = True
        self.num_samples = 0
        self.last_a = None
        self.last_b = None

    @contract(a='array,shape(x)', b='array,shape(x)', dt='float,>0')
    def update(self, a, b, dt=1.0):
        self.Ea.update(a, dt)
        self.Eb.update(b, dt)
        da = a - self.Ea.get_mean()
        db = b - self.Eb.get_mean()
        self.Edadb.update(da * db, dt)
        self.num_samples += dt

        self.R_needs_update = True
        self.last_a = a
        self.last_b = b

    def get_correlation(self):
        ''' Returns the correlation between the two streams. '''
        if self.R_needs_update:
            std_a = self.Ea.get_std_dev()
            std_b = self.Eb.get_std_dev()
            p = std_a * std_b
            zeros = p == 0
            p[zeros] = 1
            R = self.Edadb() / p
            R[zeros] = np.NAN
            self.R = R
        self.R_needs_update = False
        return self.R



    
