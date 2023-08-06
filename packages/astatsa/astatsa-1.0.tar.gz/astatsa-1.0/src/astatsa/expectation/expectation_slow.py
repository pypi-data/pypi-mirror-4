from . import ExpectationInterface, contract

__all__ = ['ExpectationSlow']


class ExpectationSlow(ExpectationInterface):
    
    ''' A class to compute the mean of a quantity over time '''
    def __init__(self, max_window=None):
        ''' 
            If max_window is given, the covariance is computed
            over a certain interval. 
        '''
        self.num_samples = 0.0
        self.value = None
        self.max_window = max_window

    @contract(value='array', dt='>0')
    def update(self, value, dt=1.0):
        if self.value is None:
            self.value = value
        else:
            self.value = weighted_average(self.value, float(self.num_samples),
                                          value, float(dt))
        self.num_samples += dt
        if self.max_window and self.num_samples > self.max_window:
            self.num_samples = self.max_window

    def get_value(self):
        return self.value

    def get_mass(self):
        return self.num_samples


@contract(A='array', wA='>=0', B='array', wB='>=0')
def weighted_average(A, wA, B, wB):
    mA = wA / (wA + wB)
    mB = wB / (wA + wB)
    return (mA * A + mB * B)
