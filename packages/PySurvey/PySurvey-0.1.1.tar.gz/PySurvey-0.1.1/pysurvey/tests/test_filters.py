'''
Created on Dec 20, 2011

@author: jonathanfriedman
'''
import unittest, operator
import numpy as np
from pysurvey.util import filters
from pandas import Series
from pandas.util.testing import assert_series_equal

expectedComperators = {'==': operator.eq,
                       '!=': operator.ne,
                       '>=': operator.ge,
                       '<=': operator.le,
                       '>': operator.gt,
                       '<': operator.lt,
                       'in':operator.contains    
                       }

expectedActors = {'sum': np.sum,
                  'avg': np.mean,
                  'med': np.median,
                  'var': np.var,
                  'std': np.std,
                  'presence': filters._presence_fun,
                  }

_s = Series([1,2,3], index=['a','b','c'])
_s2 = Series([4,5,6], index=['a','b','sum'])
_s3 = Series([np.nan,2,3], index=['a','b','c'])

class TestLineages(unittest.TestCase):
    def setUp(self):
        self.series  = _s.copy() 
        self.series2 = _s2.copy() 
        self.series3 = _s3.copy() 
        
    def test_parse_comperator(self):
        for k,ncs in filters.namedComperators.iteritems():
            for nc in ncs:
                self.assertEqual(filters.parse_comperator(nc), expectedComperators[k],
                                 'Named Comperator %s failed to parse correctly' %nc)
        fun = lambda x:x
        self.assertEqual(filters.parse_comperator(fun), fun)
        self.assertRaises(TypeError, filters.parse_comperator,1)

    def test_parse_actor(self):
        for k,nas in filters.namedActors.iteritems():
            for na in nas:
                self.assertEqual(filters.parse_actor(na), expectedActors[k],
                                 'Named Actor %s failed to parse correctly' %na)
        
        fun = lambda x:x
        self.assertEqual(filters.parse_actor(fun), fun)
        
        self.assertRaises(TypeError, filters.parse_actor,1)
        
        result   = filters.parse_actor('a')(self.series)
        expected = self.series['a']
        self.assertEqual(result, expected)
        
        result = filters.parse_actor('sum')(self.series2)
        expected = self.series2.sum()
        self.assertEqual(result, expected)
        
        result = filters.parse_actor('_sum')(self.series2)
        expected = self.series2['sum']
        self.assertEqual(result, expected)
    
    def test_Filter(self):
        f = lambda x: x>=3
        fil = filters.Filter(f)
        self.assertTrue(fil(5))
        self.assertTrue(fil(3))
        self.assertFalse(fil(2))
        
        fil = filters.Filter(('a','<',self.series['a']+1))
        self.assertTrue(fil(self.series))
        self.assertFalse(fil(self.series2))
        
        nan_vals = (True,False)
        for nan_val in nan_vals:
            fil = filters.Filter(('a','<',1), nan_val=nan_val)
            self.assertEqual(fil(self.series3), nan_val)
        
        fil = filters.Filter(('sum','<=',self.series.sum()), nan_val=False)
        self.assertTrue(fil(self.series))
        self.assertFalse(fil(self.series2))

        fil = filters.Filter(('a','in',(1,'aaa')))
        self.assertTrue(fil(self.series))
        self.assertFalse(fil(self.series2))
    
    def test_parse_filters(self):
        def test_filter_tuple(fils):
            self.assertTrue(isinstance(fils,tuple))
            for fil in fils:
                self.assertTrue(isinstance(fil,filters.Filter))
        from itertools import product
        c1 = lambda x: x>=3
        c2 = ('a','<',1)
        c3 = filters.Filter(c1)
        for p in product((c1,c2,c3), repeat=1): 
            fils =  filters.parse_filters(p)
            test_filter_tuple(fils)
        
        for p in product((c1,c2,c3), repeat=2): 
            fils =  filters.parse_filters(p)
            test_filter_tuple(fils)
          
        
if __name__ == '__main__':
    import nose
    # nose.runmodule(argv=[__file__,'-vvs','-x', '--ipdb-failure'],
    #                exit=False)
    nose.runmodule(argv=[__file__,'-vvs','-x'],
                   exit=False)
    
    
