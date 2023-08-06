'''
Created on Jun 24, 2012

@author: jonathanfriedman 
'''

from pandas import DataFrame as DF
from pysurvey.core.core_methods import _get_axis
import numpy as np

#-------------------------------------------------------------------------------
# Diversity methods   

def beta_diversity(frame, order = 1):
    '''
    Return the beta diversity of all samples calculated using the Hill number of given order.
    This is the 'effective number of distinct samples'. 
    
    -------- UNTESTED ---------
    '''
    from survey.diversity import hill_diversity
    return hill_diversity(frame.values, q=order)

def neutral_correlation(frame, method='pearson', neutral=False):
    '''
    Calculate the neutral correlation between all rows.
    Return DataMatrix of corr and p-val.
    '''
    import scipy.stats as stats
    method = method.lower()
    if method not in set(['pearson', 'kendall', 'spearman']): raise IOError('Specified correlation method is not supported.')
    if method == 'pearson'  : corr_fun = stats.pearsonr
    elif method == 'kendall': corr_fun = stats.kendalltau
    elif method == 'spearman' : corr_fun = stats.spearmanr
    mat = frame.values
    row_labels = frame.index
    n = len(row_labels)
    c_mat = np.zeros((n, n))
    p_mat = np.zeros((n, n))
    s = mat.sum(axis=0)
    for i in xrange(n):
        for j in xrange(0, n):
            x = mat[i, :]
            y = mat[j, :]/(s-x)
            c_temp, p_temp = corr_fun(x, y)
            c_mat[i][j] = c_temp
            p_mat[i][j] = p_temp
            if i==j: p_mat[i][j] = 1
    c = DF(c_mat, index=row_labels, columns=row_labels)
    p = DF(p_mat, index=row_labels, columns=row_labels)
    return c, p

def MI(frame, axis=0):
    '''        
    Compute Mutual Information between all cols.
    Return DM object. 
    '''
    import pysurvey.util.InformationTheory.MI as MI
    axis = _get_axis(axis)
    if   axis == 0: data = frame.T
    elif axis == 1: data = frame 
    x = data.values
    row_labels = data.index()        
    MI_mat = MI.MI(x)
    return DF(MI_mat, index=row_labels, columns=row_labels)

def VI(frame, axis=0):
    '''        
    Compute Variation of Information between all cols.
    Return DM object.
    '''
    import pysurvey.util.InformationTheory.MI as MI
    axis = _get_axis(axis)
    if   axis == 0: data = frame.T
    elif axis == 1: data = frame 
    x = data.values
    row_labels = data.index
    MI_mat = MI.MI(x)
    return DF(MI_mat, index=row_labels, columns=row_labels)

#-------------------------------------------------------------------------------
# Clustering/dimension reduction
       
def fuzzy_clustering(frame, k, r=2, metric='euclidean', axis=1):
    '''
    Perform fuzzy c-means clustering on rows or cols.
    k = number of clusters.   
    r = fuzziness exponent. Less fuzzy as r -> 1.
    '''
    import scipy.cluster.hierarchy as sch
    from pysurvey.util.R_pysurvey.util import c_means
    from pandas import Series
    axis = _get_axis(axis)
    D = frame.dist_mat(metric=metric, axis=axis)
    
    ## cluster each row and return a dict of cluster membership
    if hasattr(k, '__iter__'):
        width_best = 0
        avg_widths = DF(np.zeros(len(k)),
                                  columns=[metric], 
                                  index=[str(ki) for ki in k])
        for i,ki in enumerate(k):
            memb, memb_hard, stats = c_means(D.values, ki, r, diss=True)
            avg_widths[metric][str(ki)] = stats['avg_width']
            if stats['avg_width'] > width_best:
               memb_best       = memb
               memb_hard_best = memb_hard
               stats_best     = stats
        membership      = DF(memb_best, index=D.index)
        membership_hard = Series(memb_hard_best, D.index)
        return avg_widths, membership, membership_hard, stats_best
    else: 
        memb, memb_hard, stats = c_means(D.values, k, r, diss=True)
        membership      = DF(memb, index=D.index)
        membership_hard = Series(memb_hard, D.index)
        return membership, membership_hard, stats

def mean_sad(frame, rarefy=True, **kwargs):
    '''
    Compute the mean species abundance distribution with Preston binning.
    If rarefy: down-sample all samples to have the same number of counts.
    Return a Preston object
    '''
    from survey.sandbox.untb.preston_bin import Preston
    ## get the bins of the deepest sample (=sample with largest # total counts)
    if rarefy:
        n = kwargs.pop('n',1e3)
        rarefied = frame.rarefy(n)
        n_reads = n
        deepest = rarefied.index[-1]
    else:
        rarefied = frame    
        n_reads  = frame.sum(axis=1)
        n_reads.sort()
        deepest = n_reads.index[-1]
    abunds_deepest = rarefied.xs(deepest)
    pres_deepest = Preston()
    pres_deepest.bin_abunds(abunds_deepest)
    bins = pres_deepest.bins
    ## 
    pres_avg = Preston()
    i = 0
    for s,abunds in frame.T.iteritems():
        if i==0: 
            pres_avg.bin_abunds(abunds, bins)
        else:
            pres_t = Preston()
            pres_t.bin_abunds(abunds, bins)
            pres_avg += pres_t
        i+=1
    pres_avg *= 1./i
    return pres_avg
    
if __name__ == '__main__':
    pass
    
    
