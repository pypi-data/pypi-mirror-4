'''
Created on Oct 17, 2010

@author: jonathanfriedman

Estimate params of distributions from observations.
'''
import numpy as np
from numpy import exp,log, ones, array, zeros, Inf
from openopt import NLP



def estimate(obs, ll_fun, a0, **kwargs):
    weights = kwargs.get('weights', np.ones(len(obs)))
    #set up optimization problem
    k   = obs.shape[1] #number of categories
    kwargs.setdefault('lb', 1e-10*ones(len(a0)))
    kwargs.setdefault('ub', Inf*ones(len(a0)))
    tol = kwargs.pop('tol', 1e-6)
    kwargs.setdefault('xtol', tol)
    kwargs.setdefault('ftol', tol)
    kwargs.setdefault('gtol', tol)
    kwargs.setdefault('iprint', -1) 
    #set up problem
    p = NLP(x0=a0, f = ll_fun, **kwargs)
    p.args.f = (obs, weights)
    #solve problem
    sol   = p.solve('ralg')
    a_opt = sol.xf
    ll = -sol.ff
    return a_opt, ll


def dirmulti(obs, symmetric = False):
    '''
    Estimate the parameters a of the dirichlet-multinomial distribution from observations obs.
    Inputs:
        obs       = [array] rows are observations, cols are categories, values are counts (integers).
        symmetric = [bool] fit a symmetric dirichlet or not. Note that the number of parameters is the non symmetric case can be very large!
    '''
    from probabilities import dirmulti_ll, dirmulti_sym_ll
    #set up optimization problem
    k  = obs.shape[1] #number of categories
    if symmetric: a0 = [1]
    else:         a0 = [1]*k
    lb = 1e-10*ones(len(a0))
    tol=1e-6
    #set up problem
    if symmetric: p = NLP(x0=a0, f = dirmulti_sym_ll,lb=lb,iprint = 0,ftol=tol,xtol=tol,gtol=tol)
    else:         p = NLP(x0=a0, f = dirmulti_ll,lb=lb,iprint = 0,ftol=tol,xtol=tol,gtol=tol)
    p.args.f = (obs)
    #solve problem
    sol   = p.solve('ralg')
    a_opt = sol.xf
    if symmetric: a_opt = np.tile(a_opt[0],(1,k))[0]  
    ll = -sol.ff
    return a_opt, ll


def betabinom_pos(obs, **kwargs):
    '''
    Estimate the parameters a of the beta-binomial distribution from observations obs, conditional on all observations being positive.
    Inputs:
        obs       = [array] rows are observations, cols are categories, values are counts (integers).
    '''
    from probabilities import betabinom_pos_ll as bb_pos_ll
    #set up optimization problem
    k  = obs.shape[1] #number of categories
    a0 = [1]*k
    lb = 1e-10*ones(len(a0))
    tol=1e-6
    #set up problem
    p = NLP(x0=a0, f = bb_pos_ll,lb=lb,iprint = 0,ftol=tol,xtol=tol,gtol=tol)
    p.args.f = (obs)
    #solve problem
    sol   = p.solve('ralg')
    a_opt = sol.xf
    ll = -sol.ff
    return a_opt, ll




def binomial(obs, **kwargs):
    '''
    Estimate the parameters a of the binomial distribution from observations obs.
    Inputs:
        obs       = [array] rows are observations, cols are categories, values are counts (integers).
    '''
    from probabilities import binomial_ll
    #set up optimization problem
    a0 = [ obs.sum(axis =0)[0]/float(obs.sum()) ]
    print a0
    lb = 1e-10*ones(len(a0))
    tol= 1e-6
    #set up problem
    p = NLP(x0=a0, f = binomial_ll,lb=lb,iprint = 0,ftol=tol,xtol=tol,gtol=tol)
    p.args.f = (obs)
    #solve problem
    sol   = p.solve('ralg')
    a_opt = sol.xf 
    ll = -sol.ff
    return a_opt, ll


def logitnorm_bino(obs, **kwargs):
    '''
    Estimate the parameters mu, sigma of the compound logitnormal-binomial distribution from observations.
    Inputs:
        obs       = [array] rows are observations, cols are categories, values are counts (integers). col1 = # success, col2 = # failures.
    '''
    from probabilities import logitnorm_bino_ll
    #set up optimization problem
    a0 = array([0.1,1.0])
    lb = array([-np.inf,1e-10])
    tol=1e-6
    #set up problem
    p = NLP(x0=a0, f = logitnorm_bino_ll,lb=lb,iprint = 0,ftol=tol,xtol=tol,gtol=tol)
    p.args.f = (obs)
    #solve problem
    sol   = p.solve('ralg')
    a_opt = sol.xf
    ll    = -sol.ff
    return a_opt, ll



def to_fractions(mat, method = 'dirichlet'):
    '''
    Convert counts to fraction, either by simple normalization or dirichlet sampling.
    If dirichlet sampling is used, for each sample (col) fit a dirichlet distribution and sample the fraction from it.
    The prior is a uniform dirichlet (a = ones(len(otus)) )
    Return a new instance.
    '''
    if method is 'normalize': fracs = mat[:,0]/mat.sum(axis = 1)
    else:
        from numpy.random.mtrand import dirichlet
        n,k   = mat.shape
        fracs = zeros((n,k))
        for i in range(n): # for each sample
            N        = mat[i,:]     # counts of each otu in sample
            a        = N+1          # dirichlet parameters
            f        = dirichlet(a) # fractions are random sample from dirichlet
            fracs[i,:] = f
    return fracs


def test_logitnorm_bino():
    from numpy.random.mtrand import multinomial
    from probabilities import logitnorm_bino_ll as l_bino
    import scipy.stats as stats
    import matplotlib.pyplot as plt
    
    n   = int(1e2)
    mu  = 2
    sig = .2
    N   = array([10**3] * n, dtype = int)
    logit_probs = stats.norm(mu,sig).rvs(n)
    probs       = exp(logit_probs)/(1+exp(logit_probs))
    data        = np.zeros((n,2))
    for i in range(n): 
        data[i,:] =  multinomial(N[i],[probs[i],1-probs[i]])  
#    x1 = np.array( r('rbetabin(n=100, size=100, prob=.5, rho=.2)') )
#    x2 = 100 - x1
#    data = np.c_[x1,x2]
    iter    = 100
    mu_est  = 0
    sig_est = 0
    for i in range(iter):
        fracs       = to_fractions(data)
        logit_fracs = log(fracs/(1-fracs))
        mu_est     += logit_fracs[:,0].mean() 
        sig_est    += logit_fracs[:,0].std()
    mu_est  /= iter
    sig_est /= iter 
    print mu_est,sig_est
    
    ## plot
    Nmax = N.max()
    x    = np.linspace(0,Nmax,100)
    pdf_real = map(lambda i: exp( - l_bino((mu,sig),[[i,Nmax-i]]) ), x)
    pdf_est = map(lambda i: exp( - l_bino((mu_est,sig_est),[[i,Nmax-i]]) ), x)
    h_real = plt.plot(x,pdf_real)
    h_est = plt.plot(x,pdf_est)
    plt.legend([h_real,h_est],['real','est'])
    plt.show()
    
#    (a ,ll) = logitnorm_bino(data)
#    print 'Solution is:'
#    print a



def test_dirmulti_sym():
    from numpy.random.mtrand import dirichlet, multinomial
    n = int(2e2)
    a = np.array([1,1])
    N = [10000] * n
    probs = dirichlet(a,n)
    data  = np.zeros((n,len(a)))
    for i in range(n): data[i,:] =  multinomial(N[i],probs[i,:])  
#    x1 = np.array( r('rbetabin(n=100, size=100, prob=.5, rho=.2)') )
#    x2 = 100 - x1
#    data = np.c_[x1,x2]
    (a ,ll) = dirmulti(data, symmetric = False)
    print 'Solution is:'
    print a
    
    from probabilities import dirmulti_ll as ll_dirmulti
    a0 = [1]*len(a)
    weights = np.ones(len(data))
    print estimate(data, ll_dirmulti, a0, weights = weights)



def test_betabinom_pos():
    from numpy.random.mtrand import dirichlet, multinomial
    from numpy.random import rand
    n = int(5e2)
    a = np.array([10,1])
    N = [100] * n
    probs = dirichlet(a,n)
    data  = np.zeros((n,len(a)))
    p_absent = 0.01
    for i in range(n): 
        if rand() > p_absent: data[i,:] =  multinomial(N[i],probs[i,:]) 
        else:                 data[i,:] = [0,N[i]]
#    x1 = np.array( r('rbetabin(n=100, size=100, prob=.5, rho=.2)') )
#    x2 = 100 - x1
#    data = np.c_[x1,x2]
    (a ,ll) = betabinom_pos(data)
    print 'Solution is:'
    print a
    (a ,ll) = dirmulti(data, symmetric = False)
    print 'Solution is:'
    print a



def test_binomial():
    import scipy.stats as stats
    from numpy import log, array
    p = 0.2
    N = 100
    k = stats.binom(N,p).rvs(100)
    l = 1
    obs = []
    for q in k: 
        l *= stats.binom(N,p).pmf(q)
        obs.append([q,N-q])
    ll = log(l)
    print ll
    obs = array(obs)
    print binomial(obs)
    
    from probabilities import binomial_ll as ll_bino
    a0      = [ 0.5*obs.sum(axis =0)[0]/float(obs.sum()) ]
    weights = 1*np.ones(len(obs))
    print estimate(obs, ll_bino, a0, weights = weights)


if __name__ == '__main__':
    test_dirmulti_sym()