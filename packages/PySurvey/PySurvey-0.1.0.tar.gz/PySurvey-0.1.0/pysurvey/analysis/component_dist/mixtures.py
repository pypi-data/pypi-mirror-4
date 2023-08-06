'''
Created on Feb 23, 2011

@author: jonathanfriedman

Functions for estimating parameters of different mixture models using EM.
'''

import numpy as np
from numpy import zeros, exp, where, log, array, sum, arange, cumsum
from numpy.random import rand
from estimate import estimate
from matplotlib.mlab import find
import matplotlib.pyplot as plt


def EM(obs, ll_funs, a0, p0, **kwargs):
    '''
    p(x) = sum p(comp) * p(x | comp)
    Inputs:
        ll_funs = list of functions evaluating the log-likelihood of observations.
        a0 = initial parameters of component distribution. nested array.
        p0 = initial component mixture probabilities. array.
        EM_type = which variant of EM to use. ( standard (default) | SEM | CEM)
    '''
    from probabilities import delta_zero_ll
    EM_type       = kwargs.get('EM_type', 'standard')
    zero_inflated = kwargs.get('zero_inflated', False)
    min_improve = kwargs.get('min_improve', 10**-3)
    max_iter    = kwargs.get('max_iter', 20)
    comp_kwargs = kwargs.get('comp_kwargs', [{}]*len(ll_funs))
    converged = False
    iter    = 0
    ll_best = -10**20
    a_vec   = a0
    p_vec   = p0
    a_best  = a_vec
    p_best  = p_vec
    
    while not converged and iter < max_iter:
        ll = 0
        p_vec_old = p_vec
        a_vec_old = a_vec
        # (E) Compute component assignments, given components parameters.
        z      = zeros( (len(obs), len(p_vec)) ) # array of components probs for each sample. each sample is a row, and each component a col.
        z_hard = zeros(len(obs)) # array of hard component membership assignments
        for i,x in enumerate(obs):
            j = 0 # component number
            lz = zeros(len(p_vec))
            for p,a,ll_fun in zip(p_vec,a_vec,ll_funs):
#                z[i,j] = p * exp( -ll_fun(a,array([x])) )
                lz[j] = log(p) - ll_fun(a,array([x]))
                j += 1
            for j in range(len(p_vec)): z[i,j] = 1./np.sum( exp(lz-lz[j]))
#            z[i,:] = z[i,:]/sum(z[i,:]) # normalize to get probabilities
            z_c    = cumsum(z[i,:]) # cdf of component assignments for current obs
            if EM_type is 'SEM': # SEM modification
                z_hard[i] = find(z_c > rand())[0] 
                z[i,:] *= 0
                z[i,z_hard[i]] = 1.0
            elif EM_type is 'CEM': # CEM modification
                z_hard[i] = np.argmax(z[i,:]) 
                z[i,:] *= 0
                z[i,z_hard[i]] = 1.0
            
        ## (M) Compute component parameters given component assignments
        tol = 1e-100
        z[z==0] = tol
        p_vec = z.sum(axis=0)/z.sum() # set new component probabilities
        for i in range(len(p_vec)):
            if ll_funs[i] is delta_zero_ll:
                ll_comp = -delta_zero_ll(1, obs, weights = z[:,i])
            else: 
                a_opt, ll_comp = estimate(obs, ll_funs[i], a_vec[i], weights = z[:,i], **comp_kwargs[i]) # find best parameters and ll given component assignments
                a_vec[i] = a_opt
            ll      += ll_comp 
        ll_best = ll
        a_best  = a_vec
        p_best  = p_vec 

        iter += 1    
        print 'iteration ' + str(iter) +', ll = ' + str(ll)
        ## check for convergence
        max_diff = 0
        for p,p_old in zip(p_vec,p_vec_old):
            d = abs(p-p_old)/p_old
            if d > max_diff: max_diff = d 
        for a,a_old in zip(a_vec,a_vec_old):
            for t, t_old in zip(a, a_old):
                d = abs(t-t_old)/t_old
                if d > max_diff: max_diff = d 
        if max_diff <  min_improve: converged = True 
    return ll_best,a_best,p_best
    
    
def test_EM_1():
    '''
    mix of 2 beta-binom
    '''
    from numpy.random.mtrand import dirichlet, multinomial
    from numpy.random import rand
    import scipy.stats as stats
    n = int(1e3)
    a1 = np.array([.1,.1])
    a2 = np.array([1,10])
    N = [100] * n

    data  = np.zeros((n,len(a1)))
    p_absent = 0.3
    for i in range(n): 
        if rand() < p_absent: data[i,:] = multinomial(N[i],dirichlet(a1)) 
        else:                 data[i,:] = multinomial(N[i],dirichlet(a2)) 
    print data[:20,:]
    from probabilities import dirmulti_ll as ll_dirmulti
    ll_funs = [ll_dirmulti,ll_dirmulti]
    a0      = array([ [1.0]*len(a1), [1.0,5] ])
    p0      = array([0.3,0.7])
    ll_best,a_best,p_best =  EM(data, ll_funs, a0, p0)
    print ll_best,a_best,p_best
    
    from survey2.util.R_utilities import dbetabin
    x = arange(0,N[0])
    pmf1 = dbetabin(x, N[0],a_best[0][0],a_best[0][1])
    pmf2 = dbetabin(x, N[0],a_best[1][0],a_best[1][1])
    plt.hist(data[:,0], bins = N[0], normed = True)
    plt.plot(x, p_best[0]*pmf1, lw =2) 
    plt.plot(x, p_best[1]*pmf2, lw =2)
    plt.plot(x, p_best[0]*pmf1+p_best[1]*pmf2, lw =2)
    plt.show()


def test_EM_2():
    '''
    zero inflated beta-binom
    '''
    from numpy.random.mtrand import dirichlet, multinomial
    from numpy.random import rand
    import scipy.stats as stats
    n = int(1e3)
    a1 = np.array([.5,1])
    a2 = np.array([1,10])
    N = [100] * n

    data  = np.zeros((n,len(a1)))
    p_absent = 0.8
    for i in range(n): 
        if rand() < p_absent: data[i,:] = multinomial(N[i],dirichlet(a1)) 
        else:                 data[i,:] = array([0,N[i]]) 
    print data[:20,:]
    from probabilities import dirmulti_ll, delta_zero_ll
    ll_funs = [dirmulti_ll,delta_zero_ll]
    a0      = array([ [1.0]*len(a1), [1.0,5] ])
    p0      = array([0.9,0.1])
    ll_best,a_best,p_best =  EM(data, ll_funs, a0, p0)
    print ll_best,a_best,p_best
    
    from survey2.util.R_utilities import dbetabin
    x = arange(0,N[0])
    pmf1 = dbetabin(x, N[0],a_best[0][0],a_best[0][1])
    pmf2 = zeros(len(x))
    pmf2[0] = 1
    plt.hist(data[:,0], bins = N[0], normed = True)
    plt.plot(x, p_best[0]*pmf1, lw =2) 
    plt.plot(x, p_best[1]*pmf2, lw =2)
    plt.plot(x, p_best[0]*pmf1+p_best[1]*pmf2, lw =2)
    plt.show()

        

def test_EM_3():
    '''
    mix of 2 binom
    '''
    from numpy.random.mtrand import dirichlet, multinomial
    from numpy.random import rand
    import scipy.stats as stats
    n = int(1e2)
    a1 = np.array([.7])
    a2 = np.array([.9])
    N = [5000] * n

    data  = np.zeros((n,2))
    p_absent = 0.7
    for i in range(n): 
        if rand() < p_absent: k = stats.binom(N[i],a1).rvs() 
        else:                 k = stats.binom(N[i],a2).rvs() 
        data[i,:] = array([k,N[i]-k]) 
    
    from probabilities import binomial_ll as ll_binomial
    ll_funs = [ll_binomial,ll_binomial]
    a0      = array([ [.2], [.4] ])
    p0      = array([0.9,0.1])
    comp_kwargs = [{'ub':[1]}]*2
    ll_best,a_best,p_best = EM(data, ll_funs, a0, p0, comp_kwargs=comp_kwargs)
    print ll_best,a_best,p_best
    
    x = arange(0,N[0])
    pmf1 = stats.binom(N[0],a_best[0]).pmf(x)
    pmf2 = stats.binom(N[0],a_best[1]).pmf(x)
    plt.hist(data[:,0], bins = N[0], normed = True)
    plt.plot(x, p_best[0]*pmf1, lw =2) 
    plt.plot(x, p_best[1]*pmf2, lw =2)
    plt.plot(x, p_best[0]*pmf1+p_best[1]*pmf2, lw =2)
    plt.show()


def test_EM_4():
    '''
    zero inflated binom
    '''
    from numpy.random.mtrand import dirichlet, multinomial
    from numpy.random import rand
    import scipy.stats as stats
    n = int(1e3)
    a1 = np.array([.05])
    N = [10] * n

    data  = np.zeros((n,2))
    p_absent = 0.8
    for i in range(n): 
        if rand() < p_absent: k = stats.binom(N[i],a1).rvs() 
        else:                 k = 0 
        data[i,:] = array([k,N[i]-k]) 
    
    from probabilities import binomial_ll, delta_zero_ll 
    ll_funs = [binomial_ll,delta_zero_ll]
    a0      = array([ [.7], [1] ])
    p0      = array([0.9,0.1])
    ll_best,a_best,p_best = EM(data, ll_funs, a0, p0)
    print ll_best,a_best,p_best
    
    x = arange(0,N[0])
    pmf1 = stats.binom(N[0],a_best[0]).pmf(x)
    pmf2 = zeros(len(x))
    pmf2[0] = 1
    plt.hist(data[:,0], bins = N[0], normed = True)
    plt.plot(x, p_best[0]*pmf1, lw =2) 
    plt.plot(x, p_best[1]*pmf2, lw =2)
    plt.plot(x, p_best[0]*pmf1+p_best[1]*pmf2, lw =2)
    plt.show()

def test_EM_5():
    '''
    single binom
    '''
    from numpy.random.mtrand import dirichlet, multinomial
    from numpy.random import rand
    import scipy.stats as stats
    n = int(1e3)
    a1 = np.array([.1])
    a2 = np.array([.3])
    N = [50] * n

    data  = np.zeros((n,2))
    p_absent = 0.0
    for i in range(n): 
        if rand() < p_absent: k = stats.binom(N[i],a1).rvs() 
        else:                 k = stats.binom(N[i],a2).rvs() 
        data[i,:] = array([k,N[i]-k]) 
    
    from probabilities import binomial_ll as ll_binomial
    ll_funs = [ll_binomial]
    a0      = array([ [.6] ])
    p0      = array([1])
    ll_best,a_best,p_best = EM(data, ll_funs, a0, p0)
    print ll_best,a_best,p_best
    
    x = arange(0,N[0])
    pmf1 = stats.binom(N[0],a_best[0]).pmf(x)
#    pmf2 = stats.binom(N[0],a_best[1]).pmf(x)
    plt.hist(data[:,0], bins = N[0], normed = True)
    plt.plot(x, p_best[0]*pmf1, lw =2) 
#    plt.plot(x, p_best[1]*pmf2, lw =2)
#    plt.plot(x, p_best[0]*pmf1+p_best[1]*pmf2, lw =2)
    plt.show()

if __name__ == '__main__':
    test_EM_3()