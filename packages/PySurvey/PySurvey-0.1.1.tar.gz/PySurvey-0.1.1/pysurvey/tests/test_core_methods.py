'''
Created on Jul 13, 2012

@author: jonathanfriedman
'''
import unittest
import numpy as np
import pysurvey.core.core_methods as cm

from pysurvey import Lineages
from pandas import DataFrame as DF
from pandas import Series

from pandas.util.testing import assert_frame_equal
from numpy.testing import assert_allclose

_arr = np.array([[1., 2., 3.],
                 [4., 0., 6.],
                 [7., 8., 9.]])
_arr2 = [[1.,3,2],
         [6,5,4]]

_rlabels1 = ['r1','r2','r3']
_clabels1 = ['c1','c2','c3']
_frame =  DF(_arr, columns=_clabels1, index=_rlabels1)
_rlabels2 = ['r1','r2',]
_clabels2 = ['a','b','c']
_frame2 = DF(_arr2, columns=_clabels2, index=_rlabels2)

_lins_d = {'c1':'k__Bacteria;p__Nitrospirae;c__Nitrospira;o__Nitrospirales;f__Nitrospiraceae;g__Nitrospira;s__',
           'c2':'k__Bacteria;p__Bacteroidetes;c__Bacteroidia;o__Bacteroidales;f__Rikenellaceae;g__;s__',
           'c3': 'k__Bacteria;p__Bacteroidetes;c__Bacteroidia;o__Bacteroidales;f__Prevotellaceae;g__Prevotella;s__'}
_lins = Lineages.from_dict(_lins_d)

class TestFrameMethods(unittest.TestCase):

    def setUp(self):
        self.frame = _frame.copy()
        self.frame2 = _frame2.copy()
        self.lins = _lins    
    
    def test_get_axis(self):
        self.assertEqual(cm._get_axis('0'), 0)
        self.assertEqual(cm._get_axis('1'), 1)
        self.assertEqual(cm._get_axis('r'), 0)
        self.assertEqual(cm._get_axis('c'), 1)
        self.assertEqual(cm._get_axis('rows'), 0)
        self.assertEqual(cm._get_axis('cols'), 1)
        self.assertEqual(cm._get_axis('R'), 0)
        self.assertEqual(cm._get_axis('C'), 1)
        self.assertRaises(ValueError, cm._get_axis, ('z'))

    def test_get_labels(self):
        self.assertEqual(cm.get_labels(self.frame,0), _rlabels1)
        self.assertEqual(cm.get_labels(self.frame,1), _clabels1)
        
    def test_set_labels(self):
        # set from list
        rlabels_list = ['x','y','z']
        temp = self.frame.copy()
        cm.set_labels(temp,rlabels_list,0)
        self.assertEqual(cm.get_labels(temp,0), 
                         rlabels_list)
        self.assertRaises(Exception, 
                          cm.set_labels, (temp,[''],0))
        # set from dict
        rlabels_dict = {'r2':'x','r1':'y','r3':'z'}
        temp = self.frame.copy()
        cm.set_labels(temp,rlabels_dict,0)
        self.assertEqual(cm.get_labels(temp,0), ['y','x','z'])
        
    def test_index_numbers(self):
        self.assertEqual(cm._col_numbers(self.frame, ['c1','c3']),
                                         [0,2])
        self.assertEqual(cm._row_numbers(self.frame, ['r2']),
                                         [1])
        self.assertRaises(Exception, cm._col_numbers, 
                          (self.frame, ['c1','c4']))
        
    def test_to_binary(self):
        exp_vals = np.ones((3,3))
        exp_vals[1,1] = 0
        exp_vals[0,0] = 0
        expected = DF(exp_vals, columns=_clabels1, index=_rlabels1)
        result   = cm.to_binary(self.frame, 1)
        assert_frame_equal(result, expected)       

    def test_keep(self):
        # keeping rows
        expected = self.frame.drop(['r1','r2'])
        result   = cm.keep(self.frame, 1)
        assert_frame_equal(result, expected)
        # keeping cols
        exp_vals = np.array([[3., 1],
                             [6., 4],
                             [9., 7]])
        expected =  DF(exp_vals, columns=['c3','c1'], index=_rlabels1)
        result   = cm.keep(self.frame, 2, axis=1)
        assert_frame_equal(result, expected)
        # unsorted result
        expected = self.frame.drop('c2',1)
        result   = cm.keep(self.frame, 2, axis=1, sort=False)
        assert_frame_equal(result, expected)
        # different criterion and smallest values
        expected = self.frame.drop(['r1','r3'])
        result   = cm.keep(self.frame, 1, 
                           criterion='present', 
                           which='last')
        assert_frame_equal(result, expected)
        # user defined sorting function
        f = lambda x: len(np.nonzero(x%4==0)[0])
        expected = self.frame.drop(['r1'])
        result   = cm.keep(self.frame, 2, 
                           criterion=f)
        assert_frame_equal(result, expected)

    def test_vals_by_keys(self):
        expected = [1,7,2] 
        key_pairs = [('c1','r1'),('c1','r3'),('c2','r1')]
        result = cm.vals_by_keys(self.frame, key_pairs)
        self.assertEqual(expected, result)

    
    
    def test_normalize(self):
        exp_vals = [[1./6,3./6,2./6],
                    [6./15,5./15,4./15]]
        expected =  DF(exp_vals, columns=_clabels2, index=_rlabels2)
        result   = cm.normalize(self.frame2)
        assert_frame_equal(result, expected)
        
        exp_vals = [[1./7,3./8,2./6],
                    [6./7,5./8,4./6]]
        expected =  DF(exp_vals, columns=_clabels2, index=_rlabels2)
        result   = cm.normalize(self.frame2, axis='c')
        assert_frame_equal(result, expected)

    def test_to_fractions(self):
        # simple normalization
        exp_vals = [[1./6,3./6,2./6],
                    [6./15,5./15,4./15]]
        expected =  DF(exp_vals, columns=_clabels2, index=_rlabels2)
        result   = cm.to_fractions(self.frame2, 'normalize')
        assert_frame_equal(result, expected)
        # adding identical psuedo counts
        exp_vals = [[3./12,5./12,4./12],
                    [8./21,7./21,6./21]]
        expected =  DF(exp_vals, columns=_clabels2, index=_rlabels2)
        result   = cm.to_fractions(self.frame2, 
                                   'pseudo', p_counts=2)
        assert_frame_equal(result, expected)
        # adding variable psuedo counts
        exp_vals = [[2./8,5./10,3./8],
                    [6./8,5./10,5./8]]
        p_counts =  [[1,2,1],
                    [0,0,1]]
        expected =  DF(exp_vals, columns=_clabels2, index=_rlabels2)
        result   = cm.to_fractions(self.frame2, 
                                   'pseudo', p_counts=p_counts,
                                   axis=1)
        assert_frame_equal(result, expected)
        # dirichlet random sample
        result = cm.to_fractions(self.frame2)
        assert_allclose(result.sum(axis=1),1)
        self.assert_(np.all(self.frame2.index==result.index))
        self.assert_(np.all(self.frame2.columns==result.columns))
        
    def test_rarefy(self):
        n = 9
        # with replacement
        result = cm.rarefy(self.frame,n, replace=True)
        assert_allclose(result.sum(axis=1),n)
        self.assertEqual(result['c2']['r2'], 0)
        self.assert_(np.all(self.frame.index==result.index))
        self.assert_(np.all(self.frame.columns==result.columns))
        # without replacement
        result = cm.rarefy(self.frame,n)
        assert_allclose(result.sum(axis=1),n)
        self.assertEqual(result['c2']['r2'], 0)
        self.assert_('r1' not in result.index)
        self.assert_(np.all(self.frame.columns==result.columns))
    
    def test_filter_by_vals(self):
        cr1 = ('r1','>',1)
        cr2 = ('presence','>=',3)
        expected = self.frame.drop(['c1'],1)
        result = cm.filter_by_vals(self.frame, cr1)
        assert_frame_equal(result, expected)
        
        expected = self.frame.drop(['c2'],1)
        result = cm.filter_by_vals(self.frame, cr2)  
        assert_frame_equal(result, expected)
        
        expected = self.frame.drop(['c1','c2'],1)
        result = cm.filter_by_vals(self.frame, (cr1,cr2)) 
        assert_frame_equal(result, expected)
        
        expected = self.frame
        result = cm.filter_by_vals(self.frame, (cr1,cr2), how='any') 
        assert_frame_equal(result, expected)
        
        expected = self.frame.drop('r2',0)
        result = cm.filter_by_vals(self.frame, cr2, axis='r')
        assert_frame_equal(result, expected)
        
        cr3 = ('r1','<',0.4)
        expected = self.frame.drop(['c3'],1)
        result = cm.filter_by_vals(self.frame, cr3, norm=True)
        assert_frame_equal(result, expected)        

    def test_group_taxa(self):
        expected = DF(self.frame.sum(axis=1), columns=['k__Bacteria'])
        result = cm.group_taxa(self.frame, self.lins, 'k') 
        assert_frame_equal(result, expected.reindex_like(result))     
        
        bac = self.frame['c2']+self.frame['c3']
        nit = self.frame['c1']
        expected  = DF([bac,nit], index=['p__Bacteroidetes', 'p__Nitrospirae']).T
        result = cm.group_taxa(self.frame, self.lins, 'p')
        assert_frame_equal(result, expected.reindex_like(result))    

        expected_labels = ['g__Nitrospira',  'f__Rikenellaceae',  'g__Prevotella']
        expected = cm.set_labels(self.frame,expected_labels, 1, False)
        result = cm.group_taxa(self.frame, self.lins, 'g')
        assert_frame_equal(result, expected.reindex_like(result))
        
        expected_labels = ['g__Nitrospira',  'g__unassigned',  'g__Prevotella']
        expected = cm.set_labels(self.frame,expected_labels, 1, False)
        result = cm.group_taxa(self.frame, self.lins, 'g', best=False)
        assert_frame_equal(result, expected.reindex_like(result))


#group_taxa(frame, lins, level='p', best=True)

if __name__ == '__main__':
    # unittest.main()
    import nose
    # nose.runmodule(argv=[__file__,'-vvs','-x', '--ipdb-failure'],
    #                exit=False)
#    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
#                   exit=False)
    nose.runmodule(argv=[__file__,'-vvs','-x'],
                   exit=False)
    
    
