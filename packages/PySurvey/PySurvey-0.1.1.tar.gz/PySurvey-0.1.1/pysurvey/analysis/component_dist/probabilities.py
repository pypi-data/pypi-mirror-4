'''
Created on Oct 17, 2010

@author: jonathanfriedman

Function that evaluate the probabilities of observations from several distributions.
'''

import numpy as np
import scipy.stats as stats
import scipy.integrate as integrate

from scipy.special import gammaln as gl
from scipy.special import hyp1f1, gamma
from scipy.integrate import quad
from numpy import log, tile, pi, exp, sqrt, sum
from pysurvey.util.R_utilities import dbetabin, pbetabin


#-------------------------------------------------------------------------------
####### log-likelihood functions #########
# Each function takes an 1D array of parameters, and an nXm array of observations,
# where each row is a sample and each col is a component.
# Return a single number which is the -log-likelihood of all observations.

def delta_zero_ll(a, obs, weights = None,  **kwargs):
    '''
    Compute the -log likelihood of seeing observations obs from a delta function located on 0 (for the first category).
    Inputs:
        obs       = [array] rows are observations, cols are categories, values are counts (integers).
    '''
    if weights is None: weights = kwargs.get('weights', np.ones(len(obs)))

    ll    = 0
    for i in range(obs.shape[0]):
        x  = obs[i,:]
        if x[0] == 0: ll_t = 0
        else: ll_t = -1e10
        ll  -= weights[i] * ll_t
    return ll


def dir_ll(a,obs, weights = None,  **kwargs):
    '''
    Compute the -log likelihood of seeing observations obs from dirichlet with parameters a.
    Inputs:
        a         = [array] vector of parameters of the dirichlet distribution.
        obs       = [array] rows are observations, cols are categories, values are fraction (each row sums to 1).
    '''
    a = np.array(a)
    if weights is None: weights = kwargs.get('weights', np.ones(len(obs)))
    a0    = a.sum()
    a0_gl = gl(a0)
    a_gl  = gl(a)
    ll    = 0
    for i in range(obs.shape[0]):
        x  = obs[i,:]
        ll_t = a0_gl - sum(a_gl) + sum( (a-1)*log(x) )
        ll  -= weights[i] * ll_t
    return ll


def beta_ll(a,obs, weights = None,  **kwargs):
    '''
    Compute the -log likelihood of seeing observations obs from dirichlet with parameters a.
    Inputs:
        a         = [array] vector of parameters of the dirichlet distribution.
        obs       = [array] rows are observations, cols are categories, values are fraction (each row sums to 1).
    '''
    a = np.array(a)
    if weights is None: weights = kwargs.get('weights', np.ones(len(obs)))
    ll = 0
    b = stats.beta(a[0],a[1])
    for i in range(obs.shape[0]):
        x  = obs[i,0]
        t = b.pdf(x)
        if t == 0: t=1e-100
        ll -= weights[i] * np.log(t)
#        if np.abs(ll) == np.inf: 
#            print a, t
    return ll


def beta_s_ll(a,obs, weights = None,  **kwargs):
    '''
    Compute the -log likelihood of seeing observations obs from the distribution derived from the near-neutral model
    of Sloan et al 2005.
    The normalization constant is , Beta(a1,a2)*1F1(a1,a1+a2,a3)
    or Beta(Nmp,Nm(1-p))*1F1(Nmp,Nm,2aN(1-m)) in terms of the near neutral model parameters.
    Inputs:
        a         = [array] vector of parameters of the dirichlet distribution. 
                            The first two elements are the parameters of the neutral beta distribution.
                            The third is the scale on the exponent, which is assumed to be small.
        obs       = [array] rows are observations, cols are categories, values are fraction (each row sums to 1).
    '''
    a = np.array(a)
    if weights is None: weights = kwargs.get('weights', np.ones(len(obs)))
    ll = 0
    b = stats.beta(a[0],a[1])
    for i in range(obs.shape[0]):
        x  = obs[i,0]
        t = b.pdf(x) * np.exp(a[2]*x)/ hyp1f1(a[0],a[0]+a[1],a[2])
        if t == 0: t=1e-100
        ll -= weights[i] * np.log(t)
#        if np.abs(ll) == np.inf: 
#            print a, t
    return ll


def multinomial_ll(a,obs, weights = None,  **kwargs):
    '''
    Compute the -log likelihood of seeing observations obs from multinomial with parameters a.
    Inputs:
        a         = [array] vector of parameters of the multinomial distribution.
        obs       = [array] rows are observations, cols are categories, values are counts (integers).
    '''
    a = np.array(a)
    a[a<=0] = 1e-100
#    a = np.r_[a,1-sum(a)]
    if weights is None: weights = kwargs.get('weights', np.ones(len(obs)))
    ll    = 0
    for i in range(obs.shape[0]):
        x  = obs[i,:]
        x0 = sum(x)
        ll_t = gl(x0+1) - sum(gl(x+1)) + sum(x*log(a))
        if np.isnan(ll_t):
            print a
            print sum(a)
        ll  -= weights[i] * ll_t
    return ll


def dirmulti_ll(a,obs, weights = None,  **kwargs):
    '''
    Compute the -log likelihood of seeing observations obs from dirichlet-multinomial with parameters a.
    Inputs:
        a         = [array] vector of parameters of the dirichlet distribution.
        obs       = [array] rows are observations, cols are categories, values are counts (integers).
    '''
    a = np.array(a)
    if weights is None: weights = kwargs.get('weights', np.ones(len(obs)))
    a0    = a.sum()
    a0_gl = gl(a0)
    a_gl  = gl(a)
    ll    = 0
    for i in range(obs.shape[0]):
        x  = obs[i,:]
        x0 = sum(x)
        ll_t = gl(x0+1) + a0_gl + sum(gl(x+a)) - sum(a_gl) - gl(x0+a0) - sum(gl(x+1))
        ll  -= weights[i] * ll_t
    return ll


def binomial_ll(a,obs, weights = None, **kwargs):
    '''
    Compute the -log likelihood of seeing observations obs from dirichlet-multinomial with parameters a.
    Inputs:
        a         = [array] probability of 'success.
        obs       = [array] rows are observations, cols are categories, values are counts (integers).
    '''  
    if weights is None: weights = kwargs.get('weights', np.ones(len(obs)))
    a     = a[0]
    if a == 0: a = 1e-100
    ll    = 0
    for i in range(obs.shape[0]):
        x    = obs[i,:]
        k    = x[0]
        N    = sum(x)
        ll_t = gl(N+1) - gl(k+1) - gl(N-k+1) + k*log(a) +(N-k)*log(1-a)  
        ll  -= weights[i] * ll_t
    return ll



def dirmulti_sym_ll(a,obs, symmetric = True, weights = None,  **kwargs):
    '''
    Compute the -log likelihood of seeing observations obs from dirichlet-multinomial with parameters a.
    Inputs:
        a         = [array] vector of parameters of the dirichlet distribution.
        obs       = [array] rows are observations, cols are categories, values are counts (integers).
        symmetric = [bool] fit a symmetric dirichlet or not.
    '''
    if symmetric: a = tile(a,(1,obs.shape[1]))[0]
    else:         a = np.array(a)
    if weights is None: weights = kwargs.get('weights', np.ones(len(obs)))
    a0    = a.sum()
    a0_gl = gl(a0)
    a_gl  = gl(a)
    ll    = 0
    for i in range(obs.shape[0]):
        x  = obs[i,:]
        x0 = sum(x)
        ll -= gl(x0+1) + a0_gl + sum(gl(x+a)) - sum(a_gl) - gl(x0+a0) - sum(gl(x+1))
    return ll


def betabinom_pos_ll(a,obs, **kwargs):
    '''
    Compute the -log likelihood of seeing observations obs from beta-binomial with parameters a.
    conditional on all observations being positive.
    Inputs:
        a         = [array] vector of parameters of the dirichlet distribution.
        obs       = [array] rows are observations, cols are categories, values are counts (integers).
    '''
    a = np.array(a)
    a0    = a.sum()
    a0_gl = gl(a0)
    a_gl  = gl(a)
    ll    = 0
    for i in range(obs.shape[0]):
        x   = obs[i,:]
        if x[0] == 0: continue
        x0  = sum(x)
        bb0 = gamma(a0)*gamma(x0+a[1])/gamma(x[1])/gamma(a0+x0)
        ll -= gl(x0+1) + a0_gl + sum(gl(x+a)) - sum(a_gl) - gl(x0+a0) - sum(gl(x+1)) - log(1 - bb0)
    return ll

    
def logitnorm_bino_ll(a, obs, **kwargs):
    '''
    Compute the -log likelihood of seeing observations obs from compound logitnormal-binomial distribution.
    Inputs:
        obs       = [array] number 'of successes' (col1), and failures (col2) values are counts (integers).
        mu        = [float] mean of logit-norm
        sigma     = [float] std of logit-norm
    '''  
    def integrand(p,k,n,mu,sigma):
        f = exp(gl(n+1)-gl(k+1)-gl(n-k+1)) * p**k * (1-p)**(n-k)* \
            1/sqrt(2*pi)/sigma /p /(1-p) * exp(-(log(p/(1-p))-mu)**2 / 2 /sigma**2)
        return f
    
    mu,sigma = a
    ll = 0
    for o in obs:
        k = o[0]
        n = sum(o)
        l = quad(integrand, 0, 1, args=(k,n,mu,sigma),full_output=1)[0]
        ll -= log(l)
    return ll


def logitnorm_ll(a, obs, weights = None, **kwargs):
    a = np.array(a)
    if weights is None: weights = kwargs.get('weights', np.ones(len(obs)))
    ll = 0
    n = stats.norm(a[0],a[1])
    for i in range(obs.shape[0]):
        p = obs[i,0]
        x = log(p/(1-p))
        t = n.pdf(x) /p / (1-p)
        if np.isnan(t) or t==0: 
            t = 1e-100
        ll -= weights[i] * np.log(t)
    return ll

def zsm_ll(J,P,m, N, **kwargs):
    '''
    Return the probability of observing N individuals from a zero-sum multinomial with parameters J,P,m.
    For details see McKane et al. 2004.
    '''
    a0    = a.sum()
    a0_gl = gl(a0)
    a_gl  = gl(a)
    ll    = 0
    for i in range(obs.shape[0]):
        x  = obs[i,:]
        x0 = sum(x)
        ll -= gl(x0+1) + a0_gl + sum(gl(x+a)) - sum(a_gl) - gl(x0+a0) - sum(gl(x+1))
    return ll
    

####### probability functions #########
# Each function takes an 1D array of parameters, and an array of observations.
# Returns 1D array of probabilities (pdf or cdf) of each of the observations. 
def betabino_pmf(a,N,k):
    '''
    Return the probabilities of k successes in N trials from a beta-binomial distribution with params a.
    '''
    pmf = map(lambda x: exp(- dirmulti_ll(a,np.array([[x, N-x]]), symmetric = False)), k)
    return np.array(pmf)

def beta_pdf(params,x):
    pdf = stats.beta(params[0],params[1]).pdf(x)
    return pdf

def betabinom_pdf(params,x):
    a,b = params
    if a<0:
        a = 1e-10
    pdf = dbetabin(x[:,0],x.sum(axis=1),a,b)
    return pdf

def beta_s_pdf(params,x):
    temp = stats.beta(params[0],params[1]).pdf(x)
    pdf  = temp * np.exp(params[2]*x)/ hyp1f1(params[0],params[0]+params[1],params[2])
    return pdf

def beta_cdf(params,x):
    cdf = stats.beta(params[0],params[1]).cdf(x)
    return cdf

def betabinom_cdf(params,x):
    a,b = params
    if a<0:
        a = 1e-10
    cdf = pbetabin(x[:,0],x.sum(axis=1),a,b)
    return cdf

def beta_s_cdf(params,x):
    fun = lambda x, params: beta_s_pdf(params,x)
    cdf  = np.array([integrate.quad(fun,0,xi,args=(params))[0] for xi in x])
    return cdf


def logit_norm_pdf(params,x):
    logit_x = np.log(x/(1-x)) 
    pdf = stats.norm(params[0],params[1]).pdf(logit_x) /x / (1-x)
    return pdf

def logit_norm_cdf(params,x):
    logit_x = np.log(x/(1-x)) 
    cdf = stats.norm(params[0],params[1]).cdf(logit_x) 
    return cdf

def zero_delta_pdf(params,x):
    pdf = np.zeros(len(x))
    pdf[x==0] = 1
    return pdf

def zero_delta_cdf(params,x):
    cdf = np.zeros(len(x))
    cdf[x>0] = 1
    return cdf

def test_dir_ll(ll_fun):
    obs = np.array([[0.5,0.5],[0.9,0.1]])
    a = [5.,5]
    ll = ll_fun(a, obs)
    return ll

if __name__ == '__main__':
    obs = np.array([[2.,8],[10,10000]])
    a = np.array([.2])
    print -log(stats.binom(sum(obs),a[0]).pmf(obs[0][0]))
    print binomial_ll(a, obs)
    print multinomial_ll(a, obs)
    
    obs = np.array([[2.,8, 5, 10]])
    a = np.array([.2,.3])
    print multinomial_ll(a, obs)
    
#    from timeit import timeit 
#    print timeit('test_dir_ll(dir_ll)', number = 100, setup = 'from survey.component_dist.probabilities import test_dir_ll,dir_ll')
#    print timeit('test_dir_ll(beta_ll)', number = 100, setup = 'from survey.component_dist.probabilities import test_dir_ll,beta_ll')

#    import scipy.stats as stats
#    from numpy import log, array
#    p = 0.2
#    N = 100
#    n = 5
#    k = stats.binom(N,p).rvs(n)
#    l = 1
#    obs = []
#    for q in k: 
#        l *= stats.binom(N,p).pmf(q)
#        obs.append([q,N-q])
#    ll = log(l)
#    print ll
#    obs = array(obs)
#    print binomial(p,obs)
    
    
#    obs = np.array([[1,1]]) * 1e1
#    a = np.array([1,1])
#    print np.exp(-dirmulti(a,obs, symmetric = False))
#    print betabino_pmf(a, 10, np.array([0,1,2]) )
    
#    obs = np.array([[200,800],[10,10]])
#    print logitnorm_bino((0,1),obs)
    
    
#    from numpy.random.mtrand import dirichlet, multinomial
#    n = int(1e2)
#    a = np.array([.2]*50)
#    N = [200] * n
#    probs = dirichlet(a,n)
#    obs  = np.zeros((n,len(a)))
#    for i in range(n): obs[i,:] =  multinomial(N[i],probs[i,:])  
#    
#    
#    print dirmulti([a[0]],obs)
    
    
    
