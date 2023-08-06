'''
Created on Apr 26, 2011

@author: jonathanfriedman

Function for estimating different diversity measures from survey data.
Has several options for computing the diversity of individuals samples, and the gamma diversity of a collection of samples (= the sample diversity of the average of all samples).
Only supported beta diversity is the one based on hill numbers proposed by Jost. See function hill_diversity.
'''

try:
    import rpy2.robjects as ro
    from rpy2.robjects.packages import importr  # needed for loading R packages
    from rpy2.robjects.numpy2ri import numpy2ri
    ro.conversion.py2ri = numpy2ri # allows R functions to accept numpy arrays 
except ImportError:
    import warnings
    warnings.warn('R functions are not available since the rpy2 module failed to load.')
finally:
    pass   

import numpy as np
import scipy.stats as stats

from numpy import where, sum, ones, array, log, exp, nonzero

def chao1(counts):
    '''
    Get the chao1 estimator of the number of species
    '''
    f0 = len(where(counts == 0)[0]) # number of un-discoverd
    f1 = len(where(counts == 1)[0]) # number of singletons
    f2 = len(where(counts == 2)[0]) # number of singletons
    if not f2: f2 += 1
    S_obs = len(counts) - f0
    S_est = S_obs + f1*(f1-1)/2.0/(f2+1) 
    return S_est 
    
    
def hill_number(counts, q):
    '''
    Return the Hill number of order q.
    Does not take into account finite sample effects!
    See Hill 1973.
    '''
    counts = counts[counts>0]
    p = 1.*counts/sum(counts)
    lq = sum(p**q)
    if q == 1:
        plp = p*log(p)
        plp[p == 0] = 0
        lq = -sum(plp) 
        N  = exp(lq)     
    else:      N  = lq**(1./(1-q))
    return N, lq


def hill_diversity(counts, q = 1, lev = "alpha"):
    '''
    Implementation of hill diversities (alpha,beta & gamma) from the R 'vegetarian' package.
    Inputs:
        q   = order of diversity.
        lev = level of diversity (alpha,beta or gamma). 
    See:
        http://www.oga-lab.net/RGM2/func.php?rd_id=vegetarian:d
    '''
    vegetarian  = importr('vegetarian')
    x = counts.T
    d = array(vegetarian.d(x,q=q,lev = lev))[0]
    return d


def entropy(x, method = 'shrink', verbose = False):
    '''
    Use the R entropy package to calculate the entropy of observations x using given method.
    Return the entropy value. 
    Valid methods: "ML", "MM", "Jeffreys", "Laplace", "SG", "minimax", "CS", "NSB", "shrink".
    Online Doc: http://strimmerlab.org/software/entropy/ 
    '''
    if method is 'ML':
        p           = 1.*x/sum(x)
        p[p==0]     = 1
        plp         = p*log(p)
        H           = -sum(plp)
    else:
        rentropy = importr('entropy')
        H = np.array(rentropy.entropy(x, method = method, verbose = verbose))
    return H


def richness(counts, method = 'ACE'):
    '''
    Get an estimate of the number of species in a community from survey counts.
    Use R package vegan function estimateR
    See: http://rgm2.lab.nig.ac.jp/RGM2/func.php?rd_id=vegan:specpool
    Inputs:
        counts = vector of observed counts of all species (0s are allowed).
        method = 'ACE'|'chao1'|'ML'
    Outputs:
        Estimated number of species and standard error
    '''
    vegan       = importr('vegan')
    method_l = method.lower()
    if method_l == 'ml':
        S_obs = len(nonzero(counts>0)[0])
        return S_obs, 0
    elif method_l in ('chao1', 'ace'):
        temp  = vegan.estimateR(counts)
        S_obs, S_chao1, se_chao1, S_ACE, se_ACE = array(temp)
        if method_l == 'ace':     return S_ACE, se_ACE
        elif method_l == 'chao1': return S_chao1, se_chao1
    else: raise ValueError("Method '%s' is not supported for function Richness." %method)


def gamma(counts_mat, indices = 'Hill_1', **kwargs):
    '''
    compute the gamma diversity of all samples (jointly) in counts_mat according to given order of diversity, using given methods.
    Currently supports only equally weighted samples.
    Inputs:
        See 'alpha' function.
    Outputs:
        As in 'alpha' function but with only one row. 
    '''
    c_avg = np.array([counts_mat.mean(axis = 1)]).T
    return sample_diversity(c_avg, indices = indices, **kwargs)


def sample_diversity(counts_mat, indices='Hill_1', **kwargs):
    '''
    Compute given indices of alpha diversity of each sample in counts_mat according to given order of diversity, using given methods.
    
    TODO: add computation of measure of variation of the estimated diversities.
    TODO: add lower/upper bounds on hill diversities recently introduced by Haegeman et al., ISME 2013. 
    
    Parameters
    ----------
    counts_mat : array
        matrix of observed counts of all types. cols are types and rows are samples. 
        Some methods would also work with proportions and/or incidence data.
    indices : str/iterable (default 'Hill_1')
        list of indices of diversity to use. 
        Valid values:
          Hill_n   = Hill number of order n
          Richness = Sames as Hill_0.
          Shannon  = Shannon entropy. Same as Reyni_1.
          Renyi_n  = Reyni enropy of order n. Same as log(Hill_n). Reyni_1 is the Shannon entropy.
          Simpson  = Simpson's index of diversity. Same as 1/Hill_2.
          Simpson_Inv = The inverse of simpson's index. Same as Hill_2.
    methods : str/iterable (default 'ML')
        list of same length as indices detailing the methods used to calculate each index.
        Default is ML for all methods.
    
    Returns
    -------
    D : array
        marix of diversity indices. cols are indices and rows are samples.
    indices : list
        parsed indices list.
    methods : list
        parsed methods list.
    '''
    if isinstance(indices, str): indices  = [indices]
    n_smpls  = np.shape(counts_mat)[0]              # number of samples
    n_inds   = len(indices)                         # number of indices to compute.
    methods  = kwargs.get('methods', ['ML']*n_inds) # methods for computing indices.
    if isinstance(methods, str): methods  = [methods]
    D = np.zeros((n_smpls, n_inds))
    for i in xrange(n_smpls):
        counts = counts_mat[i,:]
        for j in xrange(n_inds):
            ind    = indices[j].lower()
            if ind =='shannon': ind = 'renyi_1'
            method = methods[j]
            if ind == 'richness': 
                d, se = richness(counts, method = method)
            elif ind.startswith('hill'):
                q     = float(ind.split('_')[-1])
                if q == 0:   
                    d, se = richness(counts, method = method)
                elif q == 1: 
                    d = entropy(counts, method = method)
                    d = exp(d)
                else:        
                    d, lq = hill_number(counts, q)
            elif ind.startswith('renyi'):
                q     = float(ind.split('_')[-1])
                if q == 0: 
                    d, se = richness(counts, method = method)
                    d     = np.log(d)
                elif q == 1: 
                    d = entropy(counts, method = method)
                else:
                    d, lq = hill_number(counts, q)
                    d     = np.log(d)
            elif ind in ['simpson', 'simpson_inv']:
                d, lq = hill_number(counts, 2)
                if ind == 'simpson': d = 1/d
            else: raise ValueError("%s is not a supported divesity index." %ind)
            D[i,j] = d
    return D, indices, methods
                
    
if __name__ == '__main__': 
    '''
    '''
    pass

