'''
Created on Aug 5, 2011

@author: jonathanfriedman
'''

import numpy as np
import scipy.stats as stats
import cPickle as pickle
import pylab

from scipy.special import gammaln as gl
from pandas import Series


def probability_0(n,a,b):
    '''
    Probability of getting a 0 value from a beta-binomial distribution with parameters a,b with n attempts. 
    '''
    lp = gl(n+b) + gl(a+b) - gl(a+b+n) - gl(b)
    p = np.exp(lp)
    return p


def avg_fracs(counts, method='normalize', **kwargs):
    '''
    Return the average fraction of each otu, averaged over all samples.
    '''
    if method in ['normalize', 'pseudo','dirichlet']:
        fracs     = counts.to_fractions(method, **kwargs)
        p = fracs.mean()
    elif method == 'bayes':
        otus = counts.columns
        samples = counts.index
        frac_avg = Series(np.zeros(len(otus)), otus)
        ct = counts.sum(axis=1)
        x = np.linspace(0,1,500)
        for otu, c in counts.iteritems():
            temp = np.zeros(len(x))
            for sample, tot in ct.iteritems():
                ai = c[sample] + 1
                bi = tot - c[sample] + 1
                temp += stats.beta(ai,bi).pdf(x)
            frac_avg[otu] = np.trapz(temp*x/len(samples),x)
        p = frac_avg
    else: raise ValueError, "Unknown method '%s'" %method
    return p


def detection_freq(counts):
    '''
    Compute the detection freq of all otus in counts.
    '''
    n_samples = len(counts.index)
    f = lambda x: len(np.nonzero(x>0)[0] )
    present = counts.apply(f)
    F_obs = present/float(n_samples)
    return F_obs


def objective(M, *args):
    '''
    Objective function for fitting M.
    Returns the sum of squared errors between predicted and observed
    detection frequencies of all OTUs.
    '''
    p, ct, F_obs, model  = args
    F_expt, F_var = expected_detection_freq(M, p, ct, model)
    if np.min(F_var) > 0:
        error = np.min( np.sum((F_obs-F_expt)**2)/F_var )
    else:
        error = np.min( np.sum((F_obs-F_expt)**2) )
#    error = np.sum((F_obs-F_expt)**2)
#    error = np.sum( np.abs( ((F_obs-F_expt)/F_expt) ) )
    return error


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
    
    

def expected_detection_freq(M, p, ct, model='betabinomial'):
    '''
    The expected detection frequency of each OTU, given the parameter M = mN_T.
    This function assumes neutrality, larger population size (continuous limit), and unbiased sampling from
    the local community.
    The parameter p (fraction in the meta community) is estimated from the counts.
    
    Beta binomial model:
        In this model, the distribution of counts of each OTU is a beta-binomial whose parameters are:
            a_i = p_imN_T
            b_i = (1-p_i)mN_T = (1-p_i)/p_i * a_i
        
        Thus the probability that OTU i will be present in a samples of size C_jT is
            Pr(c_ij > 0) = 1 - Pr(c_ij = 0) = 1 - pdf_BB(0 | a_i,b_i, c_jT),
        and the expected frequency of detection of OTU i is
            <Detection Freq> = sum_j Pr(c_ij > 0).
    Beta model:
        The distribution of fractions of each OTU is a binomial with parameters a_i, b_i as given above.
        There's a detection threshold in terms of a minimal fraction. 
        The expected detection frequency of each OTU is the probability of it's fraction exceeding the detection threshold.
        This is given by
            <Detection Freq> = 1 - cdf_Beta(th | a_i,b_i)
    Binomial model:
        The fraction of each OTU is constant across all samples.
        Thus the probability that OTU i will be present in a samples of size C_jT is
            Pr(c_ij > 0) = 1 - Pr(c_ij = 0) = 1 - pdf_Binomial(0 | p, c_jT),
        and the expected frequency of detection of OTU i is
            <Detection Freq> = sum_j Pr(c_ij > 0).
    '''
    otus    = p.index
    F_expt = Series(np.zeros(len(otus)), otus)
    F_var  = Series(np.zeros(len(otus)), otus)
    a = p * M
    b = (1-p)/p * a
    if model == 'betabinomial':
        samples = ct.index
        n = len(samples)
        for otu in otus:
            ai = a[otu]
            bi = b[otu]
            for sample in samples:
                p0 = probability_0(ct[sample],ai,bi)
                F_expt[otu] += 1 - p0
                F_var[otu]  += (1 - p0)*p0
        F_expt /= n
        F_var  /= n**2
    elif model == 'beta':
        for otu in otus:
            ai = a[otu]
            bi = b[otu]
            F_expt[otu] = stats.beta(ai,bi).sf(ct)
    elif model == 'binomial':
        samples = ct.index
        for otu in otus:
            pi = p[otu]
            temp = [1-(1-pi)**n for n in ct]
            F_expt[otu] = np.sum(temp)
        F_expt /= len(samples)
        pass
    else: raise ValueError, 'Unknown model %s' %model
    return (F_expt, F_var)


class DetFreq(object):
    '''
    Class for fitting different community assembly models based on the detection frequency of all OTUs.
    '''
    def __init__(self, **kwargs):
        '''
        Constructor
        '''
        set_defaults = kwargs.get('set_defaults', True)
        self.counts  = kwargs.get('counts', None)
        if set_defaults:
            if self.counts is None: raise ValueError, "Can't set default values if counts are not given."
            p_def       = avg_fracs(self.counts)
            F_obs_def   = detection_freq(self.counts)
            c_tot_def   = self.counts.sum(axis=1)
            det_lim_def = 1./c_tot_def.mean() 
        else:
            p_def       = None
            F_obs_def   = None
            c_tot_def   = None
            det_lim_def = None
        self.p       = kwargs.get('p', p_def)         #estimated proportion in metacommunity
        self.F_obs   = kwargs.get('F_obs', F_obs_def)     #observed detection frequency
        self.c_tot   = kwargs.get('c_tot', c_tot_def)
        self.det_lim = kwargs.get('det_lim', det_lim_def)
        self.M       = kwargs.get('M', {})
        self.error   = kwargs.get('error', {})
        self.F_expt  = kwargs.get('F_expt', {})
        self.R2      = kwargs.get('R2', {})


    def set_p(self, p=None):
        if p is not None: self.p = p
        else: self.p = avg_fracs(self.counts)

    def set_Fobs(self, Fobs=None):
        if Fobs is not None: self.F_obs = Fobs
        else: self.F_obs = detection_freq(self.counts)
        
    def set_Fexpt(self, model, Fexpt=None):
        if Fexpt is None:
            M = self.M[model]
            p = self.p
            if model == 'beta': 
                det_arg = self.det_lim
            elif model == 'betabinomial': 
                det_arg =  self.c_tot 
            Fexpt = expected_detection_freq(M, p, det_arg, model)
        else:
            Fexpt = Fexpt 
        self.Fexpt[model] = Fexpt
               
    def set_c_tot(self, c_tot=None):
        if c_tot is not None: self.c_tot = c_tot
        else: self.c_tot = self.counts.sum(axis=1)

    def set_det_lim(self, det_lim=None):
        if det_lim is not None: self.c_tot = det_lim
        else: self.det_lim = 1./self.c_tot.mean()    
        
    def set_R2(self, model):
        self.R2[model]     = R2(self.F_obs, self.F_expt[model])

    def estimate_M(self, models='betabinomial',  **kwargs):
        '''
        Main function used to find best fitting values of M (=mN_T).
        '''
        if isinstance(models, str): models = [models]
        for model in models:
            if model == 'binomial':
                M_opt  = 0
                F_expt,F_var = expected_detection_freq(M_opt, self.p, self.c_tot, model)
                error  = np.min( np.sum((self.F_obs-F_expt)**2) )
            elif model in ['betabinomial', 'beta']:
                from openopt import NLP
                #set up optimization problem
                tol = kwargs.get('tol', 1e-5) 
                lb  = kwargs.get('lb', tol)
                M0  = kwargs.get('M0', 1e1)
                #set up problem
                prob = NLP(x0=M0, f = objective, lb=lb, iprint = 1,ftol=tol,xtol=tol,gtol=tol)
                if model == 'beta': det_arg = self.det_lim
                elif model == 'betabinomial': det_arg =  self.c_tot
                prob.args.f = (self.p, det_arg, self.F_obs, model)
                #solve problem
                sol   = prob.solve('ralg')
                M_opt = sol.xf
                error = sol.ff
                F_expt,F_var = expected_detection_freq(M_opt, self.p, det_arg, model)
            else:
                raise ValueError, "Unknown model '%s'" %model 
            self.F_expt[model] = F_expt
            self.M[model]      = M_opt
            self.error[model]  = error
            self.R2[model]     = R2(self.F_obs, self.F_expt[model])
            

    def plot_fit(self, models='all', **kwargs):
        ## parse input args
        if models == 'all': models = self.F_expt.keys()
        if isinstance(models, str): models = [models]
        kwargs_obs  = kwargs.get('kwargs_obs',{})
        kwargs_obs.setdefault('marker','s')
        kwargs_obs.setdefault('linestyle','')
        kwargs_obs.setdefault('label','Observed')
        kwargs_expt = kwargs.get('kwargs_expt',{})
        kwargs_expt.setdefault('linewidth',2)
        xlog = kwargs.get('xlog',True)
        ylog = kwargs.get('ylog',True)
        label_fs = kwargs.get('label_fs',16)
        legend     = kwargs.get('legend',True)
        legend_fmt = kwargs.get('legend_fmt','%.2f')
        legend_loc = kwargs.get('legend_loc','best')
        show_R2 = kwargs.get('show_R2',True)
        R2_fmt  = kwargs.get('R2_fmt','%.2f')
        new_fig = kwargs.get('new_fig',True)
        file = kwargs.get('file',None)
        show = kwargs.get('show',True)
        ## plot observed freqs
        p = self.p
        p.sort()
        x = p.values
        if xlog: x = np.log10(x)
        obs  = self.F_obs.reindex_like(p)
        y = obs.values
        if ylog: y = np.log10(y)
        if new_fig: pylab.figure()
        pylab.plot(x, y, **kwargs_obs)
        ## plot expected freqs
        for model in models:  
            expt = self.F_expt[model].reindex_like(p)
            y = expt.values
            R2 = self.R2[model]
            if ylog: y = np.log10(y)
            if model != 'binomial': label = ('%s. mN = ' + legend_fmt) %(model, self.M[model])                
            else:                   label = 'binomial' 
            if show_R2: label += ('\nR^2 = ' + R2_fmt) %R2
            pylab.plot(x, y, label=label, **kwargs_expt)
        if xlog: xlabel = 'log10(Mean relative abundance)'
        else:    xlabel = 'Mean relative abundance'
        if ylog: ylabel = 'log10(Detection Frequency)'
        else:    ylabel = 'Detection Frequency'
        pylab.xlabel(xlabel, fontsize=label_fs)
        pylab.ylabel(ylabel, fontsize=label_fs)
        if legend: pylab.legend(loc=legend_loc)
        if file is not None: pylab.savefig(file)
        if show: pylab.show()


def test_expected_freq_beta():
    M = 14.6519656889131
    det_limit = 1./134
    file = 'Sloan_EM_data.pick'
    f = open(file,'r')
    p, F_obs, F_expt_sloan = pickle.load(f)
    f.close()
    index = [str(i) for i in xrange(len(p))]
    p = Series(p,index)
    F_obs = Series(F_obs,index)
    F_expt_sloan = Series(F_expt_sloan,index)
    fit = DetFreq(M={'sloan':M}, det_lim=det_limit, p=p, F_obs=F_obs, F_expt={'sloan':F_expt_sloan}, set_defaults=False )
    fit.set_R2('sloan')
    fit.estimate_M('beta')
    M_opt = fit.M['beta']
#    assert np.abs(M_opt-M)/M < 0.01
    fit.plot_fit(xlog=True, ylog=True)
    

if __name__ == '__main__':
#    test_expected_freq_beta()

    from survey.SurveyMatrix import SurveyMatrix as SM
    from survey.Lineages import Lineages
##    cols = ['otu1','otu2','otu3']
##    rows = ['sample1','sample2']
##    mat  = np.array([ [1.,0,5],[0,1,1] ])
##    counts    = SM(mat, index = rows, columns = cols)
#    
##    path = '/Users/jonathanfriedman/Documents/Alm/huge/data/'
##    lin_file = path + 'lineages_all.pick'
##    counts_file = path + 'otu_table_ggref_saliva.pick'
#    
    dofit = True
    if dofit:
        path = '/Users/jonathanfriedman/Documents/Alm/HMP_new/data_survey/'
        lin_file = path + 'hmp1.v35.hq.otu.lookup.pick'
        counts_file = path + 'Saliva.pick'
        
        lins = Lineages.fromPickle(lin_file)
        counts = SM.fromPickle(counts_file)
        print np.shape(counts)
        grouped = counts.group_taxa(lins, 'p')
    #    grouped = grouped.filter_cols(min_sum=1)
    #
        print np.shape(counts)
        fit = DetFreq(counts=grouped)
        fit.estimate_M('betabinomial')
        M_opt = fit.M['betabinomial']
    #    assert np.abs(M_opt-M)/M < 0.01
        
        file = 'temp.pick'
        fw = open(file,'w')
        pickle.dump(fit, fw)
        fw.close()
    else:
        file = 'temp.pick'
        f = open(file,'r')
        fit = pickle.load(f)
        f.close()
    
    fit.plot_fit(show=False)    
    fit.plot_fit(xlog=True, ylog=False, show=False)
    pylab.show()
    