'''
Created on Aug 5, 2011

@author: jonathanfriedman

Module for fitting the distribution of components across samples.
Support fitting the marginal distribution of a single component, or the joint distribution of all components.
'''

import numpy as np
import scipy.stats as stats
import cPickle as pickle
import pylab

from named_distributions import dist_props, get_dist_name


def get_marginal_counts(counts, col):
    '''
    Get the marginal counts of given col.
    '''
    marg = counts.reindex(columns=[col])
    marg['other'] = counts.sum(axis=1) - counts[col]
    marg = marg.reindex(columns=[col,'other'])
    return marg


def parse_dist_funs(dist_funs, type):
    if type not in ['cdf','pdf']: 
        raise ValueError, 'Unknown type %s' %type
    if isinstance(dist_funs, str):
        dist_name = get_dist_name(dist_funs)  
        dist_funs = dist_props[dist_name][type+'_fun']
    if hasattr(dist_funs, '__call__'):
        dist_funs = [dist_funs]
    else:
        n = len(dist_funs)
        for i in range(n): 
            if isinstance(dist_funs[i], str):
                dist_name = get_dist_name(dist_funs[i]) 
                dist_funs[i] = dist_props[dist_name][type+'_fun']
    return dist_funs

    
def make_mixture_dist(dist_funs, params, p, type='pdf'):
    dist_funs = parse_dist_funs(dist_funs, type)
    n = len(dist_funs)
    def dist_fun(x):
        vals = 0
        for i in range(n):
            vals += p[i] * dist_funs[i](params[i],x)
        return vals
    return dist_fun

    
def fitted_distribution(dist_funs, params, p, x=np.linspace(0,1), type='pdf'):
    dist_fun  = make_mixture_dist(dist_funs, params, p, type=type)
    dist = dist_fun(x) 
    return dist
 



class ComponentDistBase(object):
    '''
    Base class for fitting different community assembly models based on the counts/frequency of taxa across samples.
    '''
    def __init__(self, counts, **kwargs):
        '''
        Constructor
        '''
        self.counts      = counts
        fracs_method     = kwargs.get('fracs_method', 'pseudo')
        self.fracs       = kwargs.get('fracs', self.counts.to_fractions(fracs_method))
        self.counts_tot  = kwargs.get('counts_tot', self.counts.sum(axis=1))
        self.fitted      = kwargs.get('fitted', {})
     
    def toPickle(self, file):
        ''' pickles into file'''
        f = open(file, 'w')
        pickle.dump(self, f)
        f.close()
        
    @classmethod    
    def fromPickle(cls, file):
        ''' unpickles from file'''
        f = open(file, 'r')
        temp = pickle.load(f)
        f.close()
        return temp
            
    def estimate_params(self, name, ll_funs, a0, fit_fracs=False, **kwargs):
        '''
        Estimate the parameters of the component distribution.
        The fitted distribution is the one given by the ll_funs.
        ll_funcs = functions that evaluate the log-likelihood of the observations, 
                   or a str naming a supported distribution.
                   If more than one ll_fun is given, a mixture of the given ll_funs is fitted.
                   Supported distributions = binomial, beta, betabinomial, logit-normal
        '''
        from estimate import estimate
        from mixtures import EM
        from copy import copy
        n,k = np.shape(self.counts)
        ll_funs_in = copy(ll_funs)
        if isinstance(ll_funs, str):
            dist_name = get_dist_name(ll_funs)  
            fit_fracs = dist_props[dist_name]['fit_fracs']
            kwargs_default = dist_props[dist_name]['kwargs']
            for key,item in kwargs_default.iteritems():
                if hasattr(item,'__call__'): kwargs.setdefault(key, item(k))
                else:                        kwargs.setdefault(key, item)
            ll_funs = dist_props[dist_name]['ll_fun']
        if hasattr(ll_funs, '__call__'):
            if fit_fracs: obs = self.fracs
            else:         obs = self.counts
            a_best, ll_best =  estimate(obs.values, ll_funs, a0, **kwargs)
            a_best = np.array([a_best])
            p_best = np.array([1.])
        else:
            kwargs.setdefault('comp_kwargs', [{}]*len(ll_funs))
            n = len(ll_funs)
            for i in range(n): 
                if isinstance(ll_funs[i], str):
                    dist_name = get_dist_name(ll_funs[i])
                    kwargs_default = dist_props[dist_name]['kwargs']
                    for key,item in kwargs_default.iteritems():
                        if hasattr(item,'__call__'): kwargs['comp_kwargs'][i].setdefault(key, item(k))
                        else:                        kwargs['comp_kwargs'][i].setdefault(key, item)
                    ll_funs[i] = dist_props[dist_name]['ll_fun']
            p0 = kwargs.pop('p0', [1./n]*n)
            if fit_fracs: obs = self.fracs
            else:         obs = self.counts
            ll_best,a_best,p_best = EM(obs.values, ll_funs, a0, p0, **kwargs)
        fit_d = {'ll':ll_best, 'p':p_best, 'params':a_best, 'obs':obs,
                 'fracs':fit_fracs, 'll_funs':ll_funs_in, 'a0':a0}
        if not hasattr(self,'fitted'): self.fitted = {}
        self.fitted[name] = fit_d
        
        
    def get_fitted_dist(self, name, x=np.linspace(0,1), **kwargs):
        fit = self.fitted[name]
        type = kwargs.get('type','pdf')
        dist_funs = kwargs.get('dist_funs', fit['ll_funs'])
        params   = kwargs.get('params', fit['params'])
        p        = kwargs.get('p', fit['p'])
        dist = fitted_distribution(dist_funs, params, p, x, type=type)
        return dist
    
    
    def get_gof(self, names='all', type='ks', **kwargs):
        '''
        Calculate the goodness-of-fit of a given fit.
        '''
        if isinstance(names,str):
            if names == 'all': 
                names = self.fitted.keys()
                return self.get_gof(names, type, **kwargs)
            else: 
                fit = self.fitted[names]
                dist_funs = kwargs.get('dist_funs', fit['ll_funs'])
                params   = kwargs.get('params', fit['params'])
                p        = kwargs.get('p', fit['p'])
                obs = fit['obs'].values
                if np.max(obs.sum(axis=1))==1: obs = obs[:,0] #if fracs where fitted
                if type == 'ks':
                    cdf = make_mixture_dist(dist_funs, params, p, type='cdf')
                    D, pval = stats.kstest(obs, cdf)
                    return D, pval
                
                elif type == 'chi2': # for discrete data
                    if fit['ll_funs'] in ['betabinomial']:   
                        o = fit['obs'].values[:3,:]
                        n,k = np.shape(o)
                        N = np.tile(o.sum(axis=1),(k,1)).T
                        p_fit = params[0]/params.sum()
                        e = N*np.tile(p_fit,(n,1))
#                        o[o==0] = 1 #
#                        G = 2*np.sum(o*np.log(o/e)) # G statistic
                        G = np.sum((o-e)**2/e)
                        df =  n*k-n-k
                        print G,df
                        p_val = stats.chi2(df).sf(G)
                        return p_val
                else: raise ValueError, 'Unknown gof type %s' %type
        else:
            gof = {}
            for name in names:
                gof[name] = self.get_gof(name, type, **kwargs)
            return gof
         
            


class MarginalDist(ComponentDistBase):
    '''
    Class for fitting the marginal dist of a single component.
    '''
    def __init__(self, counts, component=None, **kwargs):
        '''
        Constructor
        '''
        if component is None:
            counts = counts
        else:
            counts = get_marginal_counts(counts, component)
        ComponentDistBase.__init__(self, counts, **kwargs)
        self.component   = self.counts.columns[0]
    
        
    def get_fitted_dist(self, name, x=np.linspace(0,1), **kwargs):
        fit = self.fitted[name]
        type = kwargs.get('type','pdf')
        dist_funs = kwargs.get('dist_funs', fit['ll_funs'])
        params   = kwargs.get('params', fit['params'])
        p        = kwargs.get('p', fit['p'])
        dist = fitted_distribution(dist_funs, params, p, x, type=type)
        return dist    
            
    
    def plot_fit(self, names='all', **kwargs):
        eps  = kwargs.pop('eps',1e-10)
        x    = kwargs.pop('x',np.linspace(eps,1-eps,100))
        type = kwargs.pop('type','pdf')
        new_fig  = kwargs.pop('new_fig',True)
        plot_obs = kwargs.pop('plot_obs', new_fig)
        bins     = kwargs.pop('bins', 20)
        fs         = kwargs.pop('fs',16)
        legend     = kwargs.pop('legend',True)
        ll_fmt     = kwargs.pop('ll_fmt', '.1f')
        show_gof   = kwargs.pop('show_gof',False)
        gof_fmt    = kwargs.pop('gof_fmt', '.2e')
        legend_loc = kwargs.pop('legend_loc','best')
        file = kwargs.pop('file',None)
        show = kwargs.pop('show',True)
        kwargs.setdefault('linewidth',3)
        
        if isinstance(names,str):
            if names == 'all': names = self.fitted.keys()
            else: names = [names]
        
        #plot obs
        if new_fig: pylab.figure()
        if plot_obs:
            fit = self.fitted[names[0]] 
            obs = fit['obs'].values[:,0]
            if   type == 'pdf': cumulative = False
            elif type == 'cdf': cumulative = True
            pylab.hist(obs, bins=bins, normed=True, label='Observed', cumulative=cumulative, alpha=0.7)
        
        for name in names:
            fit = self.fitted[name] 
            #plot fit
            pdf = self.get_fitted_dist(name, x, type=type)
            ll = fit['ll']
            label = ('%s , ll = %' + ll_fmt) %(name, ll)
            if show_gof:
                gof = self.get_gof(name)
                label += (', KS p = %' + gof_fmt) % gof[-1]
            pylab.plot(x,pdf, label=label, **kwargs)
        pylab.ylabel(type, fontsize=fs)
        pylab.xlabel('fraction',  fontsize=fs)
        if legend: pylab.legend(loc=legend_loc)
        if file is not None: pylab.savefig(file)
        if show: pylab.show()
        
        
class JointDist(ComponentDistBase):
    '''
    Class for fitting different community assembly models based on the counts/frequency of taxa across samples.
    '''
    def __init__(self, counts, **kwargs):
        '''
        Constructor
        '''
        ComponentDistBase.__init__(self, counts, **kwargs)
        self.marginals   = {}


    def estimate_marginals(self, name, ll_funs, a0, fit_fracs=False, components='all', **kwargs):
        '''
        Estimate the marginal distributions of given components.
        '''
        from copy import copy
        if components == 'all': components = self.counts.columns 
        fracs_method = kwargs.get('fracs_method', 'pseudo')
        for component in components:
            print component
            mfit = self.marginals.get(component, MarginalDist(self.counts, component, fracs_method=fracs_method))
            mfit.estimate_params(name, copy(ll_funs), copy(a0), fit_fracs, **kwargs)
            self.marginals[component] = mfit
            
          
    def get_marginals_property(self, property, fit_name, **kwargs):
        '''
        Get a property of all fitted marginals (e.g. the goodness-of-fit).
        Return a dictionary keyed by the marginal components ids.
        '''
        props = {}
        fit0 = self.marginals.values()[0]
        if property in fit0.fitted[fit_name]:
            f = lambda fit: fit.fitted[fit_name].__getitem__(property) 
        elif hasattr(fit0,property):
            f = lambda fit: getattr(fit,property)(fit_name, **kwargs) 
        else: raise ValueError, 'Unknown property %s' %property
        for id,fit in self.marginals.iteritems():
                prop = f(fit)
                props[id] = prop
        return props
    
    
    def detection_freq(self, names='all', **kwargs):
        from survey.untb.detection_frequency import DetFreq
        defreq = DetFreq(counts=self.counts)
        
        if isinstance(names,str):
            if names == 'all': names = self.fitted.keys()
            else: names = [names]
        
        for name in names:
            fit = self.fitted[name]
            defreq.M[name] = fit['params'].sum()
            defreq.p
            
        
        fit.set_R2('sloan')
        fit.estimate_M('beta')
        M_opt = fit.M['beta']
    #    assert np.abs(M_opt-M)/M < 0.01
        fit.plot_fit(xlog=True, ylog=True)

ComponentDist = JointDist
            
#        
#def test_marginal():
#    from survey.SurveyMatrix import SurveyMatrix
#    from numpy.random.mtrand import dirichlet, multinomial
#    from numpy.random import rand
#    import probabilities as probs
#    ## make counts
#    cols = ['otu1','otu2','otu3']
#    n    = 100
#    rows = ['sample' + str(i) for i in range(n)]
#    mat  = np.zeros((n,3))
#    a    = np.array([.5,6.5,3])
#    p    = a/a.sum()
#    for i in range(n): 
##        mat[i,:] = np.round(100*dirichlet(a))
#        mat[i,:] = multinomial(100,p)
#    counts  = SurveyMatrix(mat, index = rows, columns = cols)
##    fit = MarginalDist(counts, component='otu2')
##    fit.estimate_params('binomial_mix', ['binomial','binomial'], [[.1],[.9]])
##    fit.estimate_params('binomial', 'binomial', [.9])
##    print fit.fitted
#    fit = JointDist(counts)
#    fit.estimate_marginals('binomial', 'binomial', [.9])
##    fit.estimate_marginals('binomial_mix', ['binomial','binomial'], [[.1],[.9]])
#    fit.estimate_marginals('beta', 'beta', [1,1])
##    for key,val in fit.marginals.iteritems(): print key, val.fitted
#    print fit.get_marginals_property('ll', 'beta')
#    print fit.get_marginals_property('get_gof', 'beta')
#    

if __name__ == '__main__':
#    test_marginal()

    from survey.SurveyMatrix import SurveyMatrix as SM
    from survey.Lineages import Lineages
    
    file = 'test.pick'
    make_fit = False
    if make_fit:
#        path = '/Users/jonathanfriedman/Documents/Alm/HMP_new/data_survey/'
#        lin_file = path + 'hmp1.v35.hq.otu.lookup.pick'
#        counts_file = path + 'Stool.pick'
#        
#        lins = Lineages.fromPickle(lin_file)
#        counts = SM.fromPickle(counts_file)
#        counts = counts.filter_by_vals(axis='rows', min_sum=1000)
#        grouped = counts.group_taxa(lins, 'p')
#        data_file = 'data_temp.pick'
#        grouped.toPickle(data_file)
        
        data_file = 'data_temp.pick'
        grouped = SM.fromPickle(data_file)
        
        fit = MarginalDist(grouped, component='p.Firmicutes', fracs_method='pseudo')
#        fit.estimate_params('binomial_mix', ['binomial','binomial'], [[.1],[.9]])
#        fit.estimate_params('beta_2',['beta','beta'], [[0.1,1],[1,1]])
#        fit.estimate_params('beta_3',['beta','beta','beta'], [[0.1,1],[1,1],[1,.1]])
#        fit.estimate_params('beta', 'beta', [1,1])
#        fit.estimate_params('beta_s', 'beta_s', [1,1,0])
#        fit.estimate_params('logitn', 'logitnorm', [0,1])
        fit.estimate_params('betabinomial', 'betabinomial', [1,1])

#        k = 10
#        fit = JointDist(grouped.keep(k), fracs_method='pseudo')
#        n,k = np.shape(grouped) 
#        fit = JointDist(grouped, fracs_method='pseudo')
#        fit.estimate_params('multi', 'multi', [1./k]*(k), iprint=10)
#        fit.estimate_params('dirmulti', 'dirmulti', [1]*k, iprint=10)
#        fit.estimate_params('dir', 'dir', [1]*k, iprint=10)

        f = open(file,'w')
        pickle.dump(fit,f)
        f.close()
    else:
        f = open(file,'r')
        fit = pickle.load(f)
        f.close()

    names = ['beta','logitn']
    names = ['dir','dirmulti','multi']
#    names = ['multi']
    names = ['betabinomial']
    for name in names:
        print '========= %s ==========' %name
        params =  fit.fitted[name]['params']
        s = np.sum(params)
#        print params
#        print params/s
#        print s
#        print fit.fitted[name]['ll']
        print fit.get_gof(name, 'chi2')
        print '\n'
#    fit.plot_fit(bins=20, show_gof=False)

    
    
    
    
    
    

    