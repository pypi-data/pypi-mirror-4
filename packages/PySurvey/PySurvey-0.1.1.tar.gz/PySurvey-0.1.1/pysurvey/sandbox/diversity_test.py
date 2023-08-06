'''
Created on Apr 26, 2011

@author: jonathanfriedman

Use for testing of concepts related to diversity.
All the functions implemented in this file are in development and should not be used! 
'''

import numpy as np
import scipy.stats as stats
from numpy import where, sum, ones, array, log, exp

def coverage(counts):
    '''
    Calculate the coverage estimate given survey counts.
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
    l = 1-(1-p)**n # probability of discovery of each component
    Y = array([Y_fun(x) for x in p])
    t = sum(Y/l)
    return t      

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

def entropy(counts):
    '''
    This is the Chao-shen entropy estimator
    '''
    p_est = sampling_prob(counts[counts>0])
    n     = sum(counts)
    f     = lambda x: -x*log(x) 
    H_est = HT_estimator(f, p_est, n)
    return H_est     


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


def hill_number_gen(counts, q1, q2):
    '''
    Return the generalized Hill number of order q1, q2.
    Does not take into account finite sample effects!
    '''
    p  = 1.*counts/sum(counts)
    s1 = sum(p**q1)
    if q1 is 0: s1 -= len(where(p==0)[0])
    s2 = sum(p**q2)
    if q2 is 0: s2 -= len(where(p==0)[0])
    lq = s1*s2
    q  = q1+q2
    if q is 2:
        if q1 is 1:
            plp = p*log(p)
            plp[p == 0] = 0
            lq = -sum(plp) 
            N  = exp(lq)     
    else:      N  = lq**(1./(2-q))
    return N, lq


def discovery_number(counts, q):
    p  = 1.*counts/sum(counts)
    nq = sum(p*(1-p)**q)
    if q is 0: N = 1./(1-np.prod((1-p)**p))
    else:      N = 1./(1-nq**(1./q))
    return N, nq


def ratio_number(counts,q):
    counts = counts[counts>0]
    D  = len(counts)
    p  = 1.*counts/sum(counts)
    s1 = sum(p**(q+1))
    s2 = sum(p**(1-q))
    if q is 1:    s2 -= len(where(p==0)[0])
    elif q is -1: s1 -= len(where(p==0)[0])
    rq = s1*s2
    if q is 0: N = 1.*D/rq
    else:      N = 1.*D/rq
    return N, rq


def median_number(counts,q):
    counts = counts[counts>0]
    D  = len(counts)
    p  = 1.*counts/sum(counts)
    mq = np.median(p**q)
    if q is 0: N = mq**(-.1/q)
    else:      N = mq**(-.1/q)
    return N, mq


#def discovery_number(counts, q):
#    p = 1.*counts/sum(counts)
#    if q is 0: N = exp(-sum(p*log(p))) # wrong! need to modify
#    else:      
#        nq = sum( p*( 1-(1-p)**q ) )
##        print q, nq
#        N  = 1./(1-(1-nq)**(1./q))
#    return N, nq


def moment_number(counts, q):
    p  = 1.*counts/sum(counts)
    Mq = sum(p*exp(q*p))
    if q is 0: N = 1./sum(p**2)
    else:      N = q/log(Mq)
    return N, Mq


def test_hill():
    c  = array([10,10,10])
    c1 = array([10,10,10,1])
    c2 = array([10,10,10,10])
    c3 = array([10,10,10,10000])
    qs = [1,2,100]
    for q in qs:
        N  = hill_number(c,q)
        N1 = hill_number(c1,q) 
        N2 = hill_number(c2,q) 
        N3 = hill_number(c3,q)
        D  = discovery_number(c,q) 
        print q, N, N1,N2,N3


def test_discovery():
    import matplotlib.pyplot as plt
    ts = np.linspace(0,1,100)
    qs = [2,5,15]
#    qs = np.arange(0,10,1)
#    ts = np.linspace(-1,1,10)
    q2 = 3
    for q in qs:
        nqs = []
        Ns  = []
        for t in ts:
            c1  = array([t,1-t])
#            c1  = array([0.6,0.4,0,0,0,0])
#            c1  = array([t/2,t/2,(1-t)/2,(1-t)/2])
            N1,nq1 = median_number(c1,q)
#            c2  = array([0,0,t,(1-t)/2,(1-t)/2])
##            c2     = array([0,0,0.3,0.2,0.4,0.1])
            c2  = array([t/2,t/2,(1-t)/2,(1-t)/2])
            N2,nq2 = median_number(c2,q)
            print N2/N1
#            c      = (c1+c2)/2.
#            Ng,nq  = ratio_number(c) # gamma diversity
#            nq_avg = (nq1 + nq2)/2
#            Na     = (N1 + N2)/2 # alpha diversity
#            print Ng,Na, Ng/Na
            nqs.append(nq1)
            Ns.append(N1)
        plt.plot(ts,Ns, label = 'q = %.1f' %q)
    plt.xlabel('p1', fontsize  =18)
    plt.ylabel('N eff', fontsize  =18)
    plt.legend()
    plt.grid()
    plt.show()
             


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
    '''
    '''
    test_discovery()

