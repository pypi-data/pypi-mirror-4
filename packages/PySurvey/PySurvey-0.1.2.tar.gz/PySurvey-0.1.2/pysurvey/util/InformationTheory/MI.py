'''
Created on Jun 14, 2010

@author: jonathanfriedman

Method for estimating mutual information.
'''
import numpy as np
from survey import MetaDataFrame as MDF
from itertools import product


def estimateJointPmf(x,y, **kwargs):
    '''
    Estimate pmf over alphabet from observations x.  
    Only for discrete distributions. Continues values must be discretized before estimation!
    Inputs:
        x,y    = [np array] observation vector. All elements must be included in alphabet.
        method = [string] estimation method. Valid methods are:
                ML     - maximum likelihood estimate (simple counting). Works when n >> p (many observations over small alphabet).
                shrink - Method proposed by Hausser & Strimmer (2009).  Works for  p << n (few observations over large alphabet). 
    Outputs:
        pmf      = [DataMatrix] estimated pmf over alphabet.
    '''
    ## Set up
    n   = float(len(x))                               # number of observations
    method = kwargs.pop('method', 'ML')
    xAlph = kwargs.get('xAlpg', list(set(x)))
    yAlph = kwargs.get('yAlpg', list(set(y)))
    nxAlph = len(xAlph)
    nyAlph = len(yAlph)
    # init pmf
    p  = np.zeros((nyAlph,nxAlph), float) 
    try:
        pmf = MDF(p, columns=xAlph, index=yAlph) 
    except:
        print 3  
    
    ## Compute pmf
    if method == 'ML':
        for xa, ya in product(xAlph, yAlph):
            pmf[xa][ya] = len(np.where((x==xa) & (y==ya))[0])
        pmf = pmf/n
    elif method == 'shrink':
        tk        = 1.0/nxAlph/nyAlph
        pmf_ML    = estimateJointPmf(x,y, method='ML' , **kwargs)
        print pmf_ML
        var_ML    = pmf_ML * (1 - pmf_ML)/(n-1)
        reg_const = var_ML.sum().sum() / ( (tk - pmf_ML)**2 ).sum().sum()
        if  reg_const > 1: reg_const = 1
        pmf = reg_const * tk  +  (1 - reg_const) * pmf_ML       
    return pmf


def MIpair(x,y, **kwargs):
        pmf  = estimateJointPmf(x,y, **kwargs) # joint distribution
        
        pmf_x = pmf.sum(axis = 0) # marginal pmf, summing columns
        pmf_y = pmf.sum(axis = 1) # marginal pmf, summing rows
        pmf_x_mesh = np.tile(pmf_x.values, (len(pmf.index),1))
        pmf_y_mesh = np.tile(pmf_y.values, (len(pmf.columns),1)).transpose()
        
        ## mutual info        
        MI = ( pmf * np.log( pmf/pmf_x_mesh/pmf_y_mesh ) ).sum().sum()
        
#        ## coef of constraint
#        H_x  = -(pmf_x * np.log(pmf_x)).sum() # entropy of x
#        H_y  = -(pmf_y * np.log(pmf_y)).sum() # entropy of y
#        C_xy = MI/H_y 
#        C_yx = MI/H_x
        
#        ## variation of info
#        H_xy = -(pmf * np.log(pmf)).sum().sum() # joint entropy of x & y
#        VI   = (H_xy - MI)/H_xy
        return MI


def VIpair(x,y, **kwargs):
        pmf  = estimateJointPmf(x,y, **kwargs) # joint distribution
        
        pmf_x = pmf.sum(axis = 0) # marginal pmf, summing columns
        pmf_y = pmf.sum(axis = 1) # marginal pmf, summing rows
        pmf_x_mesh = np.tile(pmf_x.values, (len(pmf.index),1))
        pmf_y_mesh = np.tile(pmf_y.values, (len(pmf.columns),1)).transpose()
        
        ## mutual info        
        MI = ( pmf * np.log( pmf/pmf_x_mesh/pmf_y_mesh ) ).sum().sum()
        
#        ## coef of constraint
#        H_x  = -(pmf_x * np.log(pmf_x)).sum() # entropy of x
#        H_y  = -(pmf_y * np.log(pmf_y)).sum() # entropy of y
#        C_xy = MI/H_y 
#        C_yx = MI/H_x
        
        ## variation of info
        H_xy = -(pmf * np.log(pmf)).sum().sum() # joint entropy of x & y
        VI   = (H_xy - MI)/H_xy
        return VI


def MI(x):
    import scipy.cluster.hierarchy as sch
    temp = sch.distance.pdist(x, MIpair)
    return sch.distance.squareform(temp)


def VI(x):
    import scipy.cluster.hierarchy as sch
    temp = sch.distance.pdist(x, VIpair)
    return sch.distance.squareform(temp)

if __name__ == '__main__':   
    from numpy.random import random_integers
    import matplotlib.pyplot as plt
    x1 = np.array([1,1,1,0,0,0,0,2,2,2,2,2])
    x2 = np.array([0,0,1,0,1,1,1,1,1,1,0,0])
    n = 1000
#    m = 100 
#    x1 = np.r_[random_integers(0,1,n), np.zeros(m)] 
#    x2 = np.r_[random_integers(0,1,n), np.zeros(m)] 
    print MIpair(x1, x2)
    
    x = random_integers(0,1,(3,n))
    print MI(x)
    
#    info   = Information()
#    print info.MI([x1,x2], method = 'ML', alphabet = [[0,1]], shared_alph = True)

    
#    ## Compare to R entropy library
#    import rpy2.robjects as ro
#    from rpy2.robjects.packages import importr
#    import rpy2.robjects.numpy2ri
#    
#    rent = importr('entropy')
#    r = ro.r
#    
#    print rent.mi_shrink(counts_ML)
#    
    
