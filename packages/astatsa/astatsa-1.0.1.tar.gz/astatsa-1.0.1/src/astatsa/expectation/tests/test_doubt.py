from astatsa.utils.np_comparisons import assert_allclose
import numpy as np
from astatsa.expectation.expectation_fast import ExpectationFast

def check_my_doubt(exp_class):
    values = [100.0, 200.0]
    mean = 150.0
    
    for nd in [1, 10, 100, 1000, 2000]:
        
        samples = []
        for v in values:
            samples.extend([v] * nd)
        samples = np.array(samples)
    
        ex = exp_class()        
        for s in samples:
            ex.update(np.array([s]))
            
            # print('accum: %10.4f  mass: %10.4f ' % (ex.accum, ex.accum_mass))
            # ex.get_value()
        
            
        result = ex.get_value()
        # print('accum: %10.4f  mass: %10.4f ' % (ex.accum, ex.accum_mass))
                    
        assert_allclose(result, mean)
        
    

def test_fast():
    check_my_doubt(ExpectationFast)
