'''
Created on Dec 20, 2011

@author: jonathanfriedman
'''
import unittest
import numpy as np
import pysurvey.analysis.diversity as dive

class TestDiversity(unittest.TestCase):
    def setUp(self):
        self.k    = 10
        self.even = np.r_[np.ones(self.k), np.zeros(2)]
        self.uneven = self.even.copy() 
        self.uneven[0]*=10
        self.counts_mat = np.array([self.even, self.uneven])
        
        p_even = self.even/self.even.sum()
        p_uneven = self.uneven/self.uneven.sum()
        self.D_even = np.sum(p_even**2)
        self.D_uneven = np.sum(p_uneven**2)
        p_even[p_even==0] = 1
        p_uneven[p_uneven==0] = 1
        self.H_even = -np.sum(p_even*np.log(p_even))
        self.H_uneven = -np.sum(p_uneven*np.log(p_uneven))


    def test_richness(self):
        assert dive.richness(self.even, method='ml')==(self.k,0)
        assert dive.richness(self.even*2, method='ml')==(self.k,0)

    def test_hill_number(self):
        assert dive.hill_number(self.even, 0)==(self.k, self.k)
        assert dive.hill_number(self.uneven, 0)==(self.k, self.k)
        assert dive.hill_number(self.uneven, 1)==(np.exp(self.H_uneven), self.H_uneven)
        assert dive.hill_number(self.uneven, 2)==(1/self.D_uneven, self.D_uneven)
        
    def test_sample_diversity(self):
        indices = ['Hill_0','Hill_1','Hill_2']
        D, indices, methods = dive.sample_diversity(self.counts_mat, indices=indices)
        D_expt = np.array([[self.k, np.exp(self.H_even), 1/self.D_even],
                           [self.k, np.exp(self.H_uneven), 1/self.D_uneven]])
        assert np.shape(D)==(2,len(indices))
        assert methods==['ML']*3
        assert np.all(D==D_expt)



if __name__ == '__main__':
    import nose
#    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
#                   exit=False)
    nose.runmodule(argv=[__file__,'-vvs','-x'],
               exit=False)
    
    
