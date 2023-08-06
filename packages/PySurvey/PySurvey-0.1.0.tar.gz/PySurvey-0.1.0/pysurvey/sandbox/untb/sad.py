'''
Created on Oct 7, 2011

@author: jonathanfriedman

Computing fitting and ploting Species abundance distributions.
That is, the distribution of number of species with a given number of individuals.
'''

import numpy as np
from numpy import array, arange
import matplotlib.pyplot as plt
import cPickle as pickle

from pandas import Series
from preston_bin import Preston

from rpy2.robjects.packages import importr  # needed for loading R packages
import rpy2.robjects.numpy2ri               # allows R functions to accept numpy arrays
vgam = importr('VGAM')

def pbetabin(k, N, a,b):
    '''
    CDF of beta binomial.
    Online doc: http://rss.acs.unt.edu/Rdoc/library/VGAM/html/betabinUC.html
    '''
    if isinstance(k, (int,float)): k = np.array([k]) 
    try:
        F = [vgam.pbetabin_ab(ki, N, a,b) for ki in k]
    except: 
        print k, N, a,b
    return np.array(F).flatten()


def sad_expct(bins,J,Nm,p):
    '''
    Return the expected number of species represented by bins[i] <= individuals < bins[i+1],
    in a sample of size J, from a neutral local community. 
    The local community is coupled to a metacommunity whose composition is given by p.
    Inputs:
        bins  = bins of number of individuals species are represented by.
        J  = size of sample from the local community.
        Nm = strength of coupling to the metacommunity.
        p  = vector of proportions of all species in the metacommunity.  
    
    '''
#    from survey.component_dist.probabilities import betabino_pmf
#    z  = array([ betabino_pmf((Nm*pi,Nm*(1-pi)),J,x) for pi in p])
#    sn = z.sum(axis=0)
#    return sn 
    z  = array([ np.diff(np.r_[pbetabin(bins[:-1],J, Nm*pi, Nm*(1-pi)),1]) for pi in p])
    sn = z.sum(axis=0)
    return sn


def R2(obs,fit):
    '''
    Calculate the R^2 (coefficient of determination) of a fit.
    Define: 
        SS_fit = sum(obs-fit)^2
        SS_tot = sum(obs-<obs>)^2
        R2 = 1 - SS_fit/SS_tot
    See: 
        http://en.wikipedia.org/wiki/Coefficient_of_determination        
    '''
    SS_fit  = np.sum((obs-fit)**2)
    obs_avg = np.mean(obs)
    SS_tot  = np.sum((obs-obs_avg)**2)
    R2 = 1 - SS_fit/SS_tot
    return R2


def objective(M, *args):
    '''
    Objective function for fitting M.
    Returns the sum of squared errors between predicted and observed sads with preston binning.
    '''
    if M <= 1e-10: 
        print 'M is negative'
        return 1e10
    p, J, preston_obs  = args
    bins = preston_obs.bins
    sn_obs = preston_obs.sn_binned
    x = sad_expct(bins,J,M[0],p)
    y = sn_obs.index
    sn_fit = Series(sad_expct(bins,J,M[0],p),index=sn_obs.index)
    error  = np.sum(((sn_obs-sn_fit)**2))
    return error


def estimate_M(abunds, p, binned=True, **kwargs):
    '''
    Main function used to find best fitting values of M (=mN_T).
    If binned is True: bunds is already a Preston binned object
    '''
    from openopt import NLP
    if binned:
        J = kwargs['J']
        preston_obs = abunds
    else:
        J = np.round(abunds.sum())
        preston_obs = Preston()
        preston_obs.bin_abunds(abunds)
    #set up optimization problem
    tol = kwargs.get('tol', 1e-3) 
    lb  = kwargs.get('lb', 1e-6)
    ub  = kwargs.get('ub', 1e3)
    M0  = kwargs.get('M0', 2)
    #set up problem
#    prob = NLP(x0=M0, f = objective, lb=lb, ub=ub, iprint = 1,ftol=tol,xtol=tol,gtol=tol)
    prob = NLP(x0=M0, f = objective, lb=lb, iprint = 1,ftol=tol,xtol=tol,gtol=tol)
    prob.args.f = (p, J, preston_obs)
    #solve problem
    print 'entering solver'
    sol   = prob.solve('ralg')
#    sol   = prob.solve('goldenSection')
    M_opt = sol.xf[0]
    error = sol.ff
    ## get fit
    bins = preston_obs.bins
    sn_obs = preston_obs.sn_binned
    sn_fit = Series(sad_expct(bins,J,M_opt,p),index=sn_obs.index)
    r2 = R2(sn_obs, sn_fit)
    return sn_obs, sn_fit, M_opt, r2

def plot_fit(sn_obs, sn_fit, **kwargs):
    import pylab
    x = arange(len(sn_obs)) 
    pylab.bar(x, sn_obs.values, align='center')
    pylab.plot(x, sn_fit.values, 'r-o')
    pylab.xticks(x, sn_obs.index, rotation =45)

if __name__ == '__main__':
#    import pylab  
#    s = 20
#    p = array([1./s]*s)
##    abunds = np.array([5,2,3,10,1,1,16])
#    abunds = np.array([5,2,3,10,1,1,16,0,3,5,6,2,1,8,1,134])
#    preston_obs, preston_fit, M_opt, r2 = estimate_M(abunds, p)
#    print M_opt, r2
#    plot_fit(preston_obs, preston_fit)
#    pylab.show()
##    print preston_obs
##    print preston_fit

    from survey.SurveyMatrix import SurveyMatrix as SM
    from survey.Lineages import Lineages 
    import pylab   
    path = '/Users/jonathanfriedman/Documents/Alm/HMP_new/data_survey/'
    lin_file = path + 'hmp1.v35.hq.otu.lookup.pick'
    counts_file = path + 'Stool.pick'
    
    counts = SM.fromPickle(counts_file)
#    lins = Lineages.fromPickle(lin_file)
#    grouped = counts.group_taxa(lins, 'g')
    grouped = counts
    print 'counts grouped'
    abunds = grouped.values[0,:]
    p = grouped.normalize().mean(axis=0).values
    sn_obs, sn_fit, M_opt, r2 = estimate_M(abunds, p)
    print M_opt, r2
    plot_fit(sn_obs, sn_fit)
    file = 'temp.pick'
    fw = open(file,'w')
    pickle.dump((sn_obs, sn_fit, M_opt, r2), fw)
    fw.close()
    pylab.show()
    



