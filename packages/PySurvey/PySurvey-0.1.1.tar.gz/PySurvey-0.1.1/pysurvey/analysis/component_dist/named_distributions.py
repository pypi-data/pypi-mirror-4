'''
Created on Oct 14, 2011

@author: jonathanfriedman

Auxiliary file for storing information about the different named distributions.
'''
import numpy as np
import scipy.stats as stats
from probabilities import *


tol = 1e-10

dist_names = {'binomial': ['binomial','bino','binom'],
              'beta': ['beta'],
              'beta_s': ['beta_s'],
              'betabinomial': ['betabinomial','betabino','betabinom','bb'],
              'logitnorm': ['logitnorm','logitn'],
              'zero': ['zero','zero_inflated'],
              'multinomial': ['multinomial','multinom','multi'],
              'dirmultinomial': ['dirmultinomial','dirmultinom','dirmulti','dm','dirichletmultinomial','dirichlet-multinomial'],
              'dirichlet': ['dir','dirichlet'],
              } 

dist_props = {'binomial': {'pdf_fun': stats.binom, 
                            'cdf_fun': stats.binom, 
                            'll_fun':  binomial_ll,
                            'fit_fracs': False,
                            'kwargs': {'lb': [tol],'ub': [1]},
                            },
               'beta':    {'pdf_fun': beta_pdf, 
                            'cdf_fun':beta_cdf, 
                            'll_fun': beta_ll,
                            'fit_fracs': True,
                            'kwargs': {'lb': [tol,tol]},
                            },
               'beta_s':    {'pdf_fun': beta_s_pdf, 
                            'cdf_fun':beta_s_cdf, 
                            'll_fun': beta_s_ll,
                            'fit_fracs': True,
                            'kwargs': {'lb': [tol,tol,-np.inf]},
                            },
               'betabinomial':{'pdf_fun': betabinom_pdf, 
                            'cdf_fun':betabinom_cdf, 
                            'll_fun': dirmulti_ll,
                            'fit_fracs': False,
                            'kwargs': {'lb': [tol,tol]},
                            },
               'zero':    {'pdf_fun': zero_delta_pdf, 
                            'cdf_fun':zero_delta_cdf, 
                            'll_fun': delta_zero_ll,
                            'fit_fracs': False,
                            },
               'logitnorm': {'pdf_fun': logit_norm_pdf, 
                            'cdf_fun':logit_norm_cdf, 
                            'll_fun': logitnorm_ll,
                            'fit_fracs': True,
                            'kwargs': {'lb': [-np.inf,0]},
                            },
               'multinomial': {'pdf_fun': None, 
                            'cdf_fun':None, 
                            'll_fun': multinomial_ll,
                            'fit_fracs': False,
                            'kwargs': {'lb': lambda k: [0]*(k), 'ub':lambda k:[1]*(k),
                                       'Aeq': lambda k: np.ones((1,k)), 'beq':np.array([1])},
                            },
               'dirmultinomial':{'pdf_fun': None, 
                            'cdf_fun':None, 
                            'll_fun': dirmulti_ll,
                            'fit_fracs': False,
                            'kwargs': {'lb': lambda k: [tol]*k},
                            },
               'dirichlet':{'pdf_fun': None, 
                            'cdf_fun':None, 
                            'll_fun': dir_ll,
                            'fit_fracs': True,
                            'kwargs': {'lb': lambda k: [tol]*k},
                            },
               }

def get_dist_name(dist_name):
    names = filter(lambda k: dist_name.lower() in dist_names[k], dist_names.keys())
    return names[0]


