'''
Created on Dec 10, 2010

@author: jonathanfriedman

Simulate the distribution of log-likelihhod values of data drawn randomly from the data fitted distribution
'''


import numpy as np
import scipy.stats as stats
import cPickle as pickle
from estimate_dist.probabilities import betabino_pmf


from numpy import ones,array,log, zeros, Inf, arange

sites    = [
#'Anteriornares',
#'Buccalmucosa',
#'Hardpalate',
#'Keratinizedgingiva',
#'LAntecubitalfossa',
#'LRetroauricularcrease',
'Midvagina',
#'PalatineTonsils',
#'Posteriorfornix',
#'RAntecubitalfossa',
#'RRetroauricularcrease',
#'Saliva',
#'Stool',
#'Subgingivalplaque',
#'Supragingivalplaque',
#'Throat',
#'Tonguedorsum',
#'Vaginalintroitus'
 ]

path = '/Users/jonathanfriedman/Documents/Alm/HMP_HGT/dawg/'
iter = 10**3
simulate    = False
norm_approx = False
for site in sites:
    ## load read numbers
    file =  path + 'data/' + site + '_reads_tot.pick'
    f    = open(file,'r')
    N    = pickle.load(f)
    f.close() 
    
    ## load ML parameters
    file = path + 'data/otu_dist/' + site + '_filtered_beta_est.pick'
    f    = open(file,'r')
    a,ll    = pickle.load(f)
    f.close()
    
    a        = {'otu_3':np.array([ 2*1.0755506,  2*0.2824313]) , 'otu_41': np.array([ 2*0.0568133 ,  1.15650468])}

    
    ## simulate ll of samples from beta-binomial
    otus = a.keys()[:2]
    otus = ['otu_3', 'otu_41']
    for otu in otus:
        print otu
        a0,a1   = a[otu]
        if simulate:
            ll_bb   = zeros(iter)
            for j in range(iter):
                if not j%50:print j
                p_b  = stats.beta(a0,a1).rvs(len(N))
                k    = array( map(lambda i,pb: stats.binom(i,pb).rvs()  ,N, p_b) ) 
                temp = array( map(lambda n,q:  log( betabino_pmf(a[otu],n,[q]) ), N,k) )
                temp[(temp==- Inf).nonzero()] = 1e-20
                ll_bb[j] = temp.sum()
            file = path + 'data/otu_dist/' + site + '_' + otu + '_betabino_ll_dist.pick'    
            f    = open(file,'w')
            pickle.dump(ll_bb,f)
            f.close()
        if norm_approx:
            from estimate_dist.probabilities import betabino_pmf
            mu = 0
            v  = 0 
            for i,n in enumerate(N):
                print i
                pmf          = betabino_pmf(a[otu],n,arange(n))
                pmf[pmf ==0] = (pmf[pmf>0]).min()
                mu_t         = (pmf*log(pmf)).sum()
                mu2          = (pmf*(log(pmf) )**2).sum()
                v_t          = (mu2 - mu_t**2)
                mu          += mu_t
                v           += v_t 
            file = path + 'data/otu_dist/' + site + '_' + otu + '_betabino_ll_norm.pick' 
            f    = open(file,'w')
            pickle.dump((mu,v**0.5),f)
            f.close()

    
#    ## get p-vals
#    p_vals = zeros(iter)
#    for i, l in enumerate(ll_bb): 
#        p_vals[i] = len( (ll < l).nonzero()[0] )/float(iter)


