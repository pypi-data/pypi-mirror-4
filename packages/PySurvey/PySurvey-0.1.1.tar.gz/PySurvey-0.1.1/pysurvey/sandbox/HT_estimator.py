'''
Created on Jun 17, 2011

@author: jonathanfriedman

General Horowitz Thompson estimator, used to estimate the quantity t = sum(Yi) from a survey, 
where Yi is a property of type i. 
Follows the description from Chao and Shen 2003.
For useage example see function 'entropy_CS'.
'''

import numpy as np
import scipy.stats as stats
from numpy import where, sum, ones, array, log, exp

def coverage(counts):
    '''
    Calculate the coverage estimate given survey counts.
    Currently treats only singletons as 'rare' types.
    '''
    n  = sum(counts)                # total number of samples taken
    f1 = len(where(counts == 1)[0]) # number of singletons
    if f1 == n: f1-=1               # avoid 0 coverage (after R 'Entropy' package)
    c  = 1 - 1.0*f1/n               # coverage estimator
    return c


def sampling_prob(counts):
    '''
    Estimate the sampling probabilities of observed components.
    Note that 0 counts would be assosiated with a 0 estimated probability, which is not valid.
    '''
    c_est  = coverage(counts)         # get coverage estimate
    p_ML   = 1.0*counts/counts.sum()  # ML estimate of sampling probabilities
    p_est  = p_ML*c_est
    return p_est


def HT_estimator(Y_fun, p, n):
    '''
    Get the HT estimator of sum(Y) given the sampling probabilities p and the sample size n.
    Y_fun is a function that takes p_i as an argument.
    '''
    l = 1-(1-p)**n # probability of discovery of each component. Assume random sampling w replacement.
    Y = array([Y_fun(x) for x in p])
    t = sum(Y/l)
    return t 


def entropy_CS(counts):
    '''
    This is the Chao-shen entropy estimator.
    '''
    p_est = sampling_prob(counts[counts>0])
    n     = sum(counts)
    f     = lambda x: -x*log(x) 
    H_est = HT_estimator(f, p_est, n)
    return H_est  


def test():
    from numpy.random.mtrand import dirichlet, multinomial
    from numpy.random.mtrand import multivariate_normal as mvn
    
    S      = 1e3          # number of components
    a      = .1*ones(S)   # dirichlet parameter
    p      = dirichlet(a) # sampling probabilites of different components
    n      = 1e2
    counts_temp = multinomial(n,p)
    ind    = where(counts_temp > 0)
    counts = counts_temp[ind]
    c_est  = coverage(counts)
    c_tru  = sum(p[ind])     
    p_est  = sampling_prob(counts_temp)
    print c_est
    H_est = entropy(counts) 
    H_tru = sum([-x*log(x) for x in p])
    print H_tru, H_est
    
#    f = lambda x: -x*log(x)
#    f = lambda x: 1
#    t_est = HT_estimator(f, p_est[p_est>0], n)
#    t_tru = sum([f(x) for x in p])
#    print t_tru, t_est, chao1(counts), len(ind[0])

if __name__ == '__main__':
    test()  