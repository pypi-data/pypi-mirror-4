'''
Created on Oct 6, 2010

@author: jonathanfriedman
'''

import cPickle as pickle
import numpy as np
from framePatch import DataFrame
from metaFrame import MetaDataFrame
from copy import deepcopy
from decorators import copyattr, BaseDocer

class SurveyMatrix(MetaDataFrame):
    '''
    Class for storing survey counts.
    Cols correspond to types/categories (e.g. OTUs), rows correspond to samples (e.g. different time points).
    '''

    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        MetaDataFrame.__init__(self, *args, **kwargs)        

    @property
    def _constructor(self): return SurveyMatrix
           
    def __array_wrap__(self, result): return SurveyMatrix(result, index=self.index, columns=self.columns)


    

    

        
          

        
    

    
    

def test_range_abunds():
#    path = '/Users/jonathanfriedman/Documents/Alm/HMP_HGT/dawg/data/'
#    file = 'hmp_Midvagina.counts'
#    abunds = SurveyMatrix.fromTxt(path + file)
    
    cols = ['otu1','otu2','otu3']
    rows = ['sample1','sample2']
    mat  = np.array([ [5.,3,1],[0,0,21] ])
    x    = SurveyMatrix(mat, index = rows, columns = cols)
      
    fracs = x.to_fractions('normalize')
    fracs.plot_range_abunance(show = True, frac_log = True)
#    fracs.scatter_diversity(q1 =0, q2 =1, show = True)
#    abunds.plot_diversity(['Hill_0','Hill_1'], show = True, y_log = True, sample_labels = False, methods = ['chao1','CS'])
    

def test_fromTxt():
#    file = 'demo/data/fake_data_lin.counts'
#    counts, lins = SurveyMatrix.fromTxt(file, lin=True)
    file = 'demo/data/fake_data.counts'
    counts = SurveyMatrix.fromTxt(file)
#    path = '/Users/jonathanfriedman/Documents/Alm/HMP_new/data/'
#    site = 'Mid vagina'
#    file = path + 'hmp_' + site + '.counts'
#    counts = SurveyMatrix.fromTxt(file, T=False)
    counts[counts==1] = -1
    print counts
    print counts.metar
    print counts.metac 

def test_group_taxa():
    ## make lineages
    from survey.Lineages import Lineages
    line1 = 'k__Bacteria;p__Firmicutes;c__Clostridia;o__Clostridiales;f__Veillonellaceae;g__;s__' 
    line2 = 'k__Bacteria;p__Proteobacteria;c__Gammaproteobacteria;o__;f__;g__;s__'
    line3 = line2
    lins  = Lineages.fromDict({'otu1':line1,'otu2':line2,'otu3':line3})
    ## make counts
    cols = ['otu1','otu2','otu3']
    rows = ['sample1','sample2']
    mat  = np.array([ [5.,3,1],[0,0,21] ])
    x    = SurveyMatrix(mat, index = rows, columns = cols)
    print x
    print np.shape(x.metac), np.shape(x.metar)
    y =x.group_taxa(lins, 'o') 
    print y
    print y.metac


def test_bar(counts, lins):
    # get phyla counts
    counts_phyla = counts.group_taxa(lins, level = 'g')
    fracs = counts_phyla.filter_rows(min_sum = 1e4).normalize().keep(5, 'avg', axis=0, biggest=True, sort=True)
#    (fracs**1).bar_plot(show = True, legend = False, label_rows = False, draw = False)
    fracs.stacked_plot(show=True, x_label='Sample', y_label='fraction', legend=True )
    ## plot with lins
#    fracs = counts.filter_rows(min_sum = 1e4).normalize().keep(5, 'avg', axis=0, biggest=True, sort=True)
#    fracs.bar_plot_lins(lins, show = True, legend = False, label_rows = False, draw = False)

def test_rarefy():
    cols = ['otu1','otu2','otu3']
    rows = ['sample1','sample2']
    mat  = np.array([ [100.,3,1],[0,100,21] ])
    x    = SurveyMatrix(mat, index = rows, columns = cols)
    print x.rarefy(100)
    print x.rarefy(100, replace=True)


def test_correlation():
    from numpy.random.mtrand import dirichlet
    n,k = 10,4
    rlabels = ['r%d' %i for i in xrange(n)]
    clabels = ['c%d' %i for i in xrange(k)]
    a = [0.5,0.3,0.1,0.1]
#    a = [2,2,2,2.]
    a0 = np.sum(a)
    ai,aj = np.meshgrid(a, a)
    c_expt = -(ai*aj/(a0-ai)/(a0-aj))**0.5 
    t = dirichlet(a,n)
    x = SurveyMatrix(t, columns=clabels, index=rlabels)
    c,p = x.T.correlation()
    c_n,p_n = x.T.neutral_correlation()
    print c_expt
    print
    print p.values
    print
    print p_n.values
    
if __name__ == '__main__':
    
    file = '/Users/jonathanfriedman/Documents/Alm/HMP_new/metagenomics/data/kpileup/temp.txt'
    
#    print DataFrame.from_txt(file)
    temp = SurveyMatrix.from_txt(file)
    print temp
    
#    rows = ['r2', 'r0', 'r1']
#    cols = ['c0', 'c1']
#    metac = DataFrame([['sample1','big'],['sample0','small']], index = ['c1','c0'], columns = ['name', 'size'])
#    metar = DataFrame([['otu0',5],['otu2',10]], index = ['r0','r2'], columns = ['name', 'IQ'])
#    mat = np.array([ [2., 1], [1, 3], [10, 15] ])
#    df = SurveyMatrix(mat, index=rows, columns=cols, meta_cols = metac, meta_rows=metar)
#    z = df.filter_by_vals(min_avg=5, axis='r')
#    print z
    
#    z = df.filter(['c0'])
#    print type(z)
#    z = df.filter([])
#    print type(z)
    
#    test_rarefy()
    
#    from survey.Lineages import Lineages
#    import pylab
#    path = '/Users/jonathanfriedman/Documents/Alm/HMP_new/data_survey/'
#    site = 'Mid vagina'
#    site = 'Stool'
#    file = path + site + '.pick'
#    counts = SurveyMatrix.fromPickle(file)
#    
#    grouped = counts
#    ## load lins
#    file = path + 'hmp1.v35.hq.otu.lookup.pick'
#    lins = Lineages.fromPickle(file)
#    grouped = counts.group_taxa(lins, level='o', best=True)
##    print grouped.normalize().mean()
#    
#    mean_sad_rar =  grouped.mean_sad()
#    mean_sad =  grouped.mean_sad(rarefy=False)
#    print mean_sad.sn_binned.sum()
#    print mean_sad_rar.sn_binned.sum()
#    mean_sad.plot()
#    mean_sad_rar.plot()
#    pylab.show()
    
    
#    test_fromTxt()
    
#    from survey.Lineages import Lineages
#    path = '/Users/jonathanfriedman/Documents/Alm/huge/data/'
#    # load counts
#    file = path + 'subjectA.gut.phyla.pick'
#    counts = SurveyMatrix.from_pickle(file)
#    counts_epoch = counts.filter_by_meta({'epoch':'=0'}, axis='r')
#    # load lins
#    file = path + 'lineages_all.pick'
#    lins = Lineages.fromPickle(file)
    
#    file = path + 'otu_table_ggref_saliva.counts'
#    counts.filter_cols(min_present=1).toTxtLin(lins,file)  
#    
#    test_bar(counts, lins)
#    
#    ## keep on most abundant otus
#    fracs = counts.normalize()
#    print fracs.get_meta('r'), '\n'
#    z = fracs.keep(2,'avg',axis='c')
#    print z, '\n'
#    print z.get_meta('r'), '\n'
#    print z.get_meta('c'), '\n'
  
#    cols = ['otu1','otu2','otu3','otu4']
#    rows = ['sample1','sample2']
#    mat  = np.array([ [5.,3,0,1],[1,2,21,5] ])
#    x    = SurveyMatrix(mat, index = rows, columns = cols)
#    print x
#    print x.permute_w_replacement()

#    print x.basis_corr('SparCC', oprint=False)
#    x.normalize().stacked_plot(show=True)
#
#    print x.rank_abundance()
#    x.T.plot_rank_abundance(show = True, xlog = False, legend = True)
#    
#    ## test normalization
#    print x.to_fractions('normalize')
#    print x.to_fractions('pseudo')
#    print x.to_fractions()
#
#    ## test diversity
#    print x.sample_diversity()
#    print x.beta_diversity()
#   
#    y = x.to_fractions('normalize')
#    print 2**(y.dist_mat(metric = 'JSsqrt'))
#    print y
#    y.plot_incidence_abunance(show = True, y_log = False, frac_log = False)
#    
#    indices = ['Hill_0','Hill_1','Hill_2']
#    methods = ['chao1','ML','ML']
#    dive = x.sample_diversity(indices = indices, methods = methods)
#    dive.plot_cols()

#    f = x.to_fractions()
#    print type(f), f
    
    
        
        