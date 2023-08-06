'''
Created on Dec 14, 2010

@author: jonathanfriedman

Fit different forms of Relative species abundance (RSA) curve.
'''

import numpy as np
import scipy.stats as stats
import cPickle as pickle
import matplotlib.pyplot as plt

from numpy import ones, zeros, log, exp, array, arange
from scipy.special import gammaln as gl
from openopt import NLP

from preston_bin import bin_rsa

#import rpy2.robjects as ro
#from rpy2.robjects.packages import importr  # needed for loading R packages
#import rpy2.robjects.numpy2ri               # allows R functions to accept numpy arrays
#untb = importr('untb')


def logseries_expt(n, x, g, S):
    '''
    Get the expected number of species with abundance n.
    Use the 'generalized' logseries presented in eq. 1 of Volkov et al. 2007.
    '''
    ltheta = log(S) - log( (1-x)**-g -1 ) + gl(g)
    lphi = ltheta + n*log(x) - gl(n+1)  + gl(n+g)
    phi  = exp(lphi)
    return phi


def neutral_expt(n,J,theta, m = 1):
    '''
    Expected number of species with abundance n according to neutral theory.
    Uses eq. 1 (m=1), or 6 from Etienne & Alonso 2005.
    '''
    if m == 1: # if not dispersal limited
        lphi = log(theta) - log(n) + gl(J+1) - gl(J+1-n) + gl(J+theta-n) - gl(J+theta)
        phi  = exp(lphi)
    return phi



def RSA_error(params, n, rsa_data, f_expt):
    J     = n[-1]
    if f_expt is 'neutral':
        theta = params
        expt    = neutral_expt(n,J,theta) # expected number of species with abundance n
    elif f_expt is 'logseries':
        x,g = params
        S   = rsa_data.sum()
        expt    = logseries_expt(n,x,g,S) # expected number of species with abundance n
    rsa_fit = bin_rsa(n,expt)
    m = len(rsa_data)
    rsa_fit[m-1] += (rsa_fit[m:]).sum()
    rsa_fit = rsa_fit[:m] 
    error = (rsa_fit - rsa_data)**2
    return error.sum()



def RSA_fit(abunds, f_expt = 'neutral'):
    '''
    Find the community parameters that minimize the least-squares error of the theoretical RSA curve compared to the observed one.
    '''
    from preston_bin import bin_abunds
    J              = abunds.sum()
    n              = arange(1,J+1)
    rsa_data, bins = bin_abunds(abunds)
    
    #set up optimization problem
    if f_expt is 'neutral':     a0 = [ 100 ]
    elif f_expt is 'logseries': a0 = [0.9, .001]
    lb = 1e-10*ones(len(a0))
    tol= 1e-6
    #set up problem
    p = NLP(x0=a0, f = RSA_error,lb=lb,iprint = 0,ftol=tol,xtol=tol,gtol=tol)
    p.args.f = (n,rsa_data, f_expt)
    #solve problem
    sol   = p.solve('ralg')
    a_opt = sol.xf 
    error = -sol.ff
    return a_opt, error
    
    

if __name__ == '__main__':
    from preston_bin import bin_abunds
    
#    J     = 10**4
#    n     = arange(1,J+1)
#    theta = .1
#    expt  =  neutral_expt(n, J, theta)
#    rsa   = bin_rsa(n,expt)
#    abunds = []
#    for i in range(len(rsa)):
#        abunds += int( round(rsa[i]) ) * [2**(i)]
#    abunds = array(abunds)
    
    site = 'Stool'
    ## load abundance data
    path    = '/Users/jonathanfriedman/Documents/Alm/HMP_HGT/dawg/'
    file    = path + 'data/' +site + '_samples_sum.pick'
    f       = open(file,'r')
    abunds,otus  = pickle.load(f)
    f.close()

#    ## load unfiltered abundance data
#    path = '/Users/jonathanfriedman/Documents/Alm/HMP_HGT/dawg/'
#    ts_file = path + 'data/hmp_' +site + '.pick'
#    f       = open(ts_file,'r')
#    abunds  = pickle.load(f)
#    f.close()
#    ## aggregate all samples
#    counts , otus, samples = abunds.to_matrix()
#    abunds = counts[:,2]

    ## data RSA
    J              = abunds.sum()
    n              = arange(1,J+1)
    rsa_data, bins = bin_abunds(abunds)
    
#    ## do fit
    f_expt            = 'logseries'
    params_opt, error = RSA_fit(abunds, f_expt)
    print params_opt, error
    if f_expt is 'neutral':
        theta = params_opt
        expt_opt    = neutral_expt(n,J,theta) # expected number of species with abundance n
    elif f_expt is 'logseries':
        x,g = params_opt
        S   = rsa_data.sum()
        expt_opt    = logseries_expt(n,x,g,S) # expected number of species with abundance n
    rsa_opt          = bin_rsa(n,expt_opt)
    
    
#    plt.plot(n,expt,'-*', lw = 2)
    plt.figure()
    w = 0.8
    plt.bar(arange(len(rsa_data))-w/2,rsa_data, width = w)
    plt.plot(arange(len(rsa_opt)),rsa_opt, 'r-*', lw=2)
    plt.xticks(arange(len(rsa_data)))
    
#    rsa_abunds, bins = bin_abunds(abunds)
#    plt.figure()
#    plt.bar(arange(len(rsa_abunds))-w/2,rsa_abunds, width = w)
    plt.show()
    
    
    
      