'''
Created on Jul 13, 2012

@author: jonathanfriedman
'''
import unittest
import numpy as np
import survey2.core.metadata_methods as mm

from pandas import DataFrame as DF
from pandas.util.testing import assert_frame_equal

rows = ['r1', 'r0', 'r2', 'r3']
cols = ['c0', 'c1', 'c2']
metac = DF([[np.nan,'big'],
            ['Entero','small'],
            ['Blautia','tiny']], 
           columns=['name', 'size'],
           index=cols)
metar = DF([[np.nan,20],
            ['subject2',50],
            ['subject1',35]], 
           columns=['name', 'age'],
           index =['r3','r2','r1']) 
mat = np.array([[2., np.nan,1], 
                [1, 3, 2],
                [10, 15,3],
                [0,0,1]])
df = DF(mat, index=rows, columns=cols)


class TestFrameMethods(unittest.TestCase):

    def setUp(self):
        self.frame = df.copy()
        self.metar = metar.copy()    
        self.metac = metac.copy() 
    
    def test_filter_by_meta(self):
        # smaller
        result   = mm.filter_by_meta(df,metar, ('_age','<',35), axis='r')
        expected = df.drop(['r0','r1','r2'], axis=0)
        assert_frame_equal(expected, result)
        # smaller equal
        result   = mm.filter_by_meta(df,metar, ('_age','<=',35), axis='r')
        expected = df.drop(['r0','r2'], axis=0)
        assert_frame_equal(expected, result)
        # greater
        result   = mm.filter_by_meta(df,metar, ('_age','>',35), axis='r')
        expected = df.drop(['r0','r1','r3'], axis=0)
        assert_frame_equal(expected, result)
        # equal
        result   = mm.filter_by_meta(df,metar, ('_age','=',35), axis='r')
        expected = df.drop(['r0','r2','r3'], axis=0)
        assert_frame_equal(expected, result)
        # not equal
        result   = mm.filter_by_meta(df,metar, ('_age','!=',35), axis='r')
        expected = df.drop(['r0','r1'], axis=0)
        assert_frame_equal(expected, result)
        # empty result
        result   = mm.filter_by_meta(df,metar, ('_age','<',0), axis='r')
        expected = df.drop(df.index, axis=0)
        assert_frame_equal(expected, result)
        # filtering columns
        result   = mm.filter_by_meta(df,metac, ('_size','==','tiny'), axis='c')
        expected = df.drop(['c0','c1'], axis=1)
        assert_frame_equal(expected, result)
        # non-existing filtering column
        self.assertRaises(KeyError, 
                          mm.filter_by_meta,
                          *(df, metac, ('_missing','>',0)))
        # keeping elements with missing metadata
        result   = mm.filter_by_meta(df,metar, ('_age','<',35), axis='r', 
                                     filter_missing=False)
        expected = df.drop(['r1','r2'], axis=0)
        assert_frame_equal(expected, result)
        # user-defined filter function
        expected = df.drop(['c0'], axis=1)
        f_size   = lambda x: x['size'] in ['small', 'tiny']
        result   = mm.filter_by_meta(df,metac, f_size, axis='c')
        assert_frame_equal(expected, result)
        result   = mm.filter_by_meta(df,metac, ('_size','in',['small', 'tiny']), axis='c')
        assert_frame_equal(expected, result)
        # multiple filter functions
        f_name = lambda x: x['name'].startswith('E') if isinstance(x['name'], str) else False
        result   = mm.filter_by_meta(df,metac, 
                                     (f_size, f_name),
                                     axis='c')
        expected = df.drop(['c0','c2'], axis=1)
        assert_frame_equal(expected, result)
        
    def test_drop_missing_meta(self):
        # drop cols
        result = mm.drop_missing_meta(df,metac)
        expected = df.drop(['c0'], axis=1)
        assert_frame_equal(expected, result)
        # drop rows
        result = mm.drop_missing_meta(df,metar, axis='r')
        expected = df.drop(['r0','r3'])
        assert_frame_equal(expected, result)
        # drop based on specific metadata
        result = mm.drop_missing_meta(df,metar, axis='r', labels='age')
        expected = df.drop(['r0'])
        assert_frame_equal(expected, result)
        # drop based on several specific metadata
        result = mm.drop_missing_meta(df,metar, axis='r', labels=('age','name'))
        expected = df.drop(['r0','r3'])
        assert_frame_equal(expected, result)
                
    def test_sort_by_meta(self):
        result = mm.sort_by_meta(df,metac,columns='name')
        expected = df.reindex(columns=['c0','c2','c1'])
        assert_frame_equal(expected, result)   
        result = mm.sort_by_meta(df,metar, axis=0,columns='age')
        expected = df.reindex(index=['r3','r1','r2','r0'])
        assert_frame_equal(expected, result)     
        

if __name__ == '__main__':
    # unittest.main()
    import nose
    # nose.runmodule(argv=[__file__,'-vvs','-x', '--ipdb-failure'],
    #                exit=False)
#    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
#                   exit=False)
    nose.runmodule(argv=[__file__,'-vvs','-x'],
                   exit=False)
    
    