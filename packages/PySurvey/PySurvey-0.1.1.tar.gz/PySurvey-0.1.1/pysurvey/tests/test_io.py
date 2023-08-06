'''
Created on Dec 20, 2011

@author: jonathanfriedman
'''
import unittest, os, tempfile
import numpy as np
import pysurvey.io.io as io
from pysurvey import Lineages
from pandas import DataFrame as DF
from pandas.util.testing import assert_frame_equal

exp_vals = np.array([[1, 2, 3],
                     [4, 5, 6],
                     [7, 8, 9]])
expected_counts =  DF(exp_vals.T, 
                      index=['sample_1','sample_2','sample_3'], 
                      columns=['otu_1','otu_2','otu_3']) 

lins_d = {'otu_1':'k__Bacteria;p__Nitrospirae;c__Nitrospira;o__Nitrospirales;f__Nitrospiraceae;g__Nitrospira;s__',
          'otu_2':'k__Bacteria;p__Bacteroidetes;c__Bacteroidia;o__Bacteroidales;f__Rikenellaceae;g__;s__',
          'otu_3': 'k__Bacteria;p__Bacteroidetes;c__Bacteroidia;o__Bacteroidales;f__Prevotellaceae;g__Prevotella;s__'}
expected_lins = Lineages.from_dict(lins_d)
 

class TestLineages(unittest.TestCase):
    def setUp(self):
        pass
        
    def test_read_txt(self):
        countsfile = 'data/fake_data.counts'
        counts = io.read_txt(countsfile, verbose=False) 
        assert_frame_equal(counts, expected_counts)
        countsT = io.read_txt(countsfile, T=False, verbose=False) 
        assert_frame_equal(countsT, expected_counts.T)
        
        countsfile = 'data/fake_data_lin.counts'
        counts,lins = io.read_txt(countsfile, verbose=False)
        assert_frame_equal(counts, expected_counts)
        self.assertEqual(lins, expected_lins)
        
        countsfile = 'data/fake_data_lin2.counts'
        counts,lins = io.read_txt(countsfile, verbose=False,
                                  lin=True, lin_label='consensus lins')
        assert_frame_equal(counts, expected_counts)
        self.assertEqual(lins, expected_lins)

    def test_write_txt(self):
        outfile = tempfile.mkstemp()[1]
        
        io.write_txt(expected_counts, outfile)
        counts = io.read_txt(outfile, verbose=False) 
        assert_frame_equal(counts, expected_counts)

        io.write_txt(expected_counts, outfile, 
                     lin=expected_lins, lin_label='consensus lins')        
        counts,lins = io.read_txt(outfile, verbose=False,
                          lin=True, lin_label='consensus lins')
        assert_frame_equal(counts, expected_counts)
        self.assertEqual(lins, expected_lins)
        
        os.remove(outfile)

        

if __name__ == '__main__':
    import nose
    # nose.runmodule(argv=[__file__,'-vvs','-x', '--ipdb-failure'],
    #                exit=False)
#    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
#                   exit=False)
    nose.runmodule(argv=[__file__,'-vvs','-x'],
                   exit=False)
    
    
