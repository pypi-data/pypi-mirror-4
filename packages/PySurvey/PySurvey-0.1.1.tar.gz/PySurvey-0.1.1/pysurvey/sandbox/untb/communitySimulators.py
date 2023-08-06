'''
Created on Mar 22, 2012

@author: jonathanfriedman

Objects used to simulate various types of communities (steady-state or dynamics).


TODO: steady-state from closed-form distributions. 
    fractions: dirichlet, logit-normal
    abundances: log-normal, multivariate gamma/poisson
    counts: multinomial, dirichlet-multinomial, 
            sampling from given fractions (un/biased, with/out replacement)
TODO: Dynamics simulations using:
    coupled Langevin eqs.
    transition rates.
'''

from numpy import shape, zeros
from numpy.random.mtrand import dirichlet, multinomial

def dirmulti_rvs(a,N):
    probs = dirichlet(a,len(N))
    counts  = zeros(shape(probs))
    for i in range(len(N)): counts[i,:] =  multinomial(N[i],probs[i,:])
    return counts

def multi_rvs(p,N):
    counts = zeros((len(N),len(p)))
    for i in range(len(N)): counts[i,:] =  multinomial(N[i],p)
    return counts

_countsTypes = {'dirmulti': ('dirmulti', 'dirichlet-multinomial','dirmult','neutral'),
                'multi':('multi','multinomial','constant-frac')
                }

class CountsSimulator(object):
    '''
    classdocs
    '''

    def __init__(self, type, *args, **kwargs):
        '''
        Constructor
        '''
        typeStandard = self._parseType(type)
        self.type         = type
        self.typeStandard = typeStandard
        self.args   = args
        self.kwargs = kwargs
    
    def _parseType(self, type):
        typeStandard = filter(lambda key: type.lower() in _countsTypes[key], _countsTypes)
        if not typeStandard: raise ValueError, 'Unknown type: %s' %type
        else: return typeStandard[0]
    
    def get(self):
        pass
        
    def set(self):
        pass
        
    def simulate(self, **kwargs):
        '''
        Simulate n communities.
        '''
        ## parse params
        N = self.kwargs['N']
        if not hasattr(N, '__iter__'): N = [N]*kwargs['n']
        if self.type == 'dirmulti': 
            simFun = dirmulti_rvs
            params = self.kwargs['params']
            if not hasattr(params, '__iter__'): 
                if 'd' not in self.kwargs: 
                    raise ValueError, 'If params is non-iterable, the number of components d must be supplied'
                else:
                    params = [params]*self.kwargs['d']
        elif self.type == 'multi':
            if 'params' not in self.kwargs: 
                if 'd' not in self.kwargs: 
                    raise ValueError, 'If params is not given, the number of components d must be supplied'
                else:
                    d = self.kwargs['d']
                    params = [1./d]*d
            simFun = multi_rvs
        ## draw counts
        counts = simFun(params,N)
        return counts      
        

                
        
        