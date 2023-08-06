'''
Created on Dec 15, 2010

@author: jonathanfriedman
'''

import numpy as np
from numpy import array
from pandas import Series
from copy import deepcopy



def _bin_strs(bins):
    '''
    Convert bin boundries to string.
    '''
    strs = []
    for i in range(0,len(bins)-1):
        b1 = bins[i]+1
        b2 = bins[i+1]
        if b1 == b2:     s = '%d' %b1
        elif np.isinf(b2): s = '%d-%s' %(b1,b2)
        else:              s = '%d-%d' %(b1,b2)
        strs.append(s)
    return strs

class Preston(object):
    '''
    Preston binned abundance data.
    '''
    
    def __init__(self):
        self.sn_binned = Series([], index=[])
        self.bins = array([])
        self.abunds = array([])
        self.sn = array([])
        self.n  = array([])
    
    def __repr__(self): return repr(self.sn_binned)
    
    def __len__(self): return len(self.sn_binned) 
    
    def __add__(self,other):
        if isinstance(other, Preston):
            n1 = len(self)
            n2 = len(other)
            dn = np.abs(n1-n2)
            short, long = sorted((self,other), key= lambda x:len(x))
            new = deepcopy(long)
            t = np.r_[short.sn_binned.values,[0]*dn]
            new.sn_binned += t
            new.abunds = np.r_[new.abunds, other.abunds]
        else:
            new = deepcopy(self)
            new.sn_binned += other
        return new
    
    def __sub__(self,other):
        if isinstance(other, Preston):
            n1 = len(self)
            n2 = len(other)
            dn = np.abs(n1-n2)
            short, long = sorted((self,other), key= lambda x:len(x))
            new = deepcopy(long)
            t = np.r_[short.sn_binned.values,[0]*dn]
            new.sn_binned -= t
            if n2 > n1:
                new.sn_binned *= -1
        else:
            new = deepcopy(self)
            new.sn_binned -= other
        return new

    def __mul__(self,other):
        if isinstance(other, Preston):
            n1 = len(self)
            n2 = len(other)
            dn = np.abs(n1-n2)
            short, long = sorted((self,other), key= lambda x:len(x))
            new = deepcopy(long)
            t = np.r_[short.sn_binned.values,[0]*dn]
            new.sn_binned *= t
        else:
            new = deepcopy(self)
            new.sn_binned *= other
        return new
    
    def __pow__(self,n):
        new = deepcopy(self)
        new.sn_binned = new.sn_binned**n
        return new
        
            
    def sum(self):
        return self.sn_binned.sum()        
        
        
    def bin_abunds_R(self,abunds):
        '''
        Do preston binning of abunds, return the counts in each bin and the bin limits
        '''
        from rpy2.robjects.packages import importr  # needed for loading R packages
        import rpy2.robjects.numpy2ri               # allows R functions to accept numpy arrays
        self.abunds = abunds
        untb = importr('untb')
        a    = untb.count(abunds[abunds !=0])
        out  = untb.preston(a) 
        bins_str  = list(out.names)
        sn_binned = array(out)
        self.sn_binned = Series(sn_binned, index=bins_str) 


    def bin_abunds(self, abunds, bins=None):
        '''
        Do preston binning of abunds, return the counts in each bin and the bin limits
        '''
        abunds = abunds[abunds > 0]
        largest = np.floor(np.log2(np.max(abunds)))
        temp    = np.log2(np.max(abunds))
        if temp == largest: largest -= 1
        if bins == None: bins = np.r_[0, 2**np.arange(largest+1), np.Inf]
        bins_str = _bin_strs(bins)
        sn_binned, t = np.histogram(abunds, bins+1)
        self.bins = bins
        self.sn_binned = Series(sn_binned, index=bins_str)
    

    def bin_grouped(self,n,sn):
        '''
        Preston binning of grouped abundance.
        Inputs:
            n  = number of individuals, sorted in ascending order.
            sn = number of species with n individuals
        '''
        largest = np.floor(np.log2(n[-1]))
        temp    = np.log2(np.max(n[-1]))
        if temp == largest: largest -= 1
        bins = np.r_[0, 2**np.arange(largest+1), np.Inf]
        bins_str = _bin_strs(bins)
        sn_binned = array(np.zeros(len(bins_str)), dtype=int)
        for i in range(len(bins)-1):
            b1 = bins[i]+1
            b2 = bins[i+1]
            ind1 = np.where(n>=b1)[0][0]
            if i<(len(bins)-2): 
                ind2 = np.where(n>b2)[0][0]
            else:
                ind2 = len(bins)
            sn_binned[i] = np.sum(sn[ind1:ind2])
        self.n  = n
        self.sn = sn
        self.bins = bins
        self.sn_binned = Series(sn_binned, index=bins_str)
        
    def plot(self, **kwargs):
        import pylab
        pylab.figure()
        kwargs.setdefault('align','center')
        sn_binned = self.sn_binned
        x = np.arange(len(sn_binned)) 
        pylab.bar(x, sn_binned.values, **kwargs)
        pylab.xticks(x, sn_binned.index, rotation =45)


if __name__ == '__main__':
    import scipy.stats as stats
    abunds1 = np.array([5,2,3,10,1,1,16,0,3,5,6,2,1,8,1,134])
    abunds2 = np.array([5,2,3,10,1,1,16])
    z = stats.itemfreq(abunds1)
    n = z[:,0]
    sn = z[:,1]
    pres1 = Preston()
    pres1.bin_abunds(abunds1)
    pres2 = Preston()
    pres2.bin_abunds(abunds2)
    print pres2.bins
    print pres2.sn_binned.index
#    print pres1,'\n'
#    print pres2,'\n'
#    print (pres2**2 - 1)*0.5
#    print pres1-pres2
#    print pres2-pres1
#    pres.preston_grouped(n, sn)
#    print pres
#    pres.preston_abunds(abunds)
#    print pres
#    pres.preston_R(abunds)
#    print pres    
    