'''
Created on April 2, 2013

@author: jonathanfriedman
'''
import unittest
import numpy as np
import pysurvey.analysis.analysis_methods as am
from pysurvey.analysis.diversity import sample_diversity

from pysurvey import Lineages
from pandas import DataFrame as DF
from pandas import Series

from pandas.util.testing import assert_frame_equal, assert_series_equal
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
    
    def test_sample_diversity(self):
        inds = ['Hill_0','Hill_1']
        expected_dive = sample_diversity(self.frame.values, inds)[0]
        expected = DF(expected_dive, 
                      columns=[ind +'.ML' for ind in inds],
                      index=[self.frame.index])
        result = am.sample_diversity(self.frame, inds)
        assert_frame_equal(expected, result)

    def test_dist_mat(self):
        import scipy.cluster.hierarchy as sch
        metric = 'euclidean'
        D = sch.distance.pdist(self.frame, metric)
        D = sch.distance.squareform(D)
        expected = DF(D, index=self.frame.index,
                      columns=self.frame.index)
        result = am.dist_mat(self.frame, metric)
        assert_frame_equal(expected, result)
        
        D = sch.distance.pdist(self.frame.T, metric)
        D = sch.distance.squareform(D)
        expected = DF(D, index=self.frame.columns,
                      columns=self.frame.columns)
        result = am.dist_mat(self.frame, metric, axis=1)
        assert_frame_equal(expected, result)
        
        metric = 'minkowski'
        p = 3
        D = sch.distance.pdist(self.frame, metric, p=p)
        D = sch.distance.squareform(D)
        expected = DF(D, index=self.frame.index,
                      columns=self.frame.index)
        result = am.dist_mat(self.frame, metric, p=p)
        assert_frame_equal(expected, result)
        
        import pysurvey.util.distances as distances
        D = sch.distance.pdist(self.frame, distances.JS)
        D = sch.distance.squareform(D)
        expected = DF(D, index=self.frame.index,
                      columns=self.frame.index)
        result = am.dist_mat(self.frame, 'Js')
        assert_frame_equal(expected, result)

    def test_correlation(self):
        import scipy.stats as stats
        from pysurvey import get_labels
        for ax in (0,1):
            c_mat, p_mat = stats.spearmanr(self.frame.values, axis=ax)
            labels = get_labels(self.frame,1-ax)
            expected_c = DF(c_mat,index=labels,columns=labels) 
            expected_p = DF(p_mat,index=labels,columns=labels) 
            result_c, result_p = am.correlation(self.frame, 'spearman', ax)
            assert_frame_equal(expected_c, result_c)
            assert_frame_equal(expected_p, result_p)
        self.assertRaises(ValueError, am.correlation, (self.frame), **{'method':'foo'})

    def test_PCoA(self):
        points, eigs = am.PCoA(self.frame, 'JSsqrt')
        m = self.frame.shape[1]
        expected_cols = ['PC%d' %i for i in range(1,1+m)]
        self.assert_(np.all(self.frame.index==points.index))
        self.assert_(np.all(points.columns==expected_cols))
        self.assertAlmostEqual(eigs.min(),0)
        # check that eigenvalues are sorted
        self.assert_(np.all(np.diff(eigs.values)<0))
        self.assert_(np.all(eigs.index==expected_cols))
        
        self.assertRaises(ValueError, am.PCoA, (self.frame))
        
    def test_discriminating_components(self):
        from numpy.random import rand
        f1 = self.frame
        f2 = f1+10*rand(*f1.shape)
        disc = am.discriminating_components(f1,f2)
        self.assert_(np.all(disc.columns==['Median1','Median2','p-val']))
        assert_series_equal(disc['Median1'],f1.median().reindex(index=disc.index))
        assert_series_equal(disc['Median2'],f2.median().reindex(index=disc.index))
        # check that p-values are sorted
        self.assert_(np.all(np.diff(disc['p-val'].values)>=0))
        
        disc = am.discriminating_components(f1,f2, 'fisher')

    def test_permute_w_replacement(self):
        perm = am.permute_w_replacement(self.frame2, axis='c')
        for c, permvals in perm.iteritems():
            self.assert_(set(permvals).issubset(set(self.frame2[c])))
        perm = am.permute_w_replacement(self.frame2, axis='r')
        for c, permvals in perm.T.iteritems():
            self.assert_(set(permvals).issubset(set(self.frame2.T[c])))        

    def test_rank_abundance(self):
        ranked = am.rank_abundance(self.frame)
        m = self.frame.shape[1]
        expected_cols = np.arange(1,1+m)
        for c, vals in ranked.T.iteritems():
            self.assert_(set(vals)==(set(self.frame.T[c])))
            self.assert_(np.all(np.diff(vals.values)<=0)) 
        self.assert_(np.all(self.frame.index==ranked.index))
        self.assert_(np.all(ranked.columns==expected_cols)) 
        
if __name__ == '__main__':
    # unittest.main()
    import nose
    # nose.runmodule(argv=[__file__,'-vvs','-x', '--ipdb-failure'],
    #                exit=False)
#    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
#                   exit=False)
    nose.runmodule(argv=[__file__,'-vvs','-x'],
                   exit=False)
    
    
