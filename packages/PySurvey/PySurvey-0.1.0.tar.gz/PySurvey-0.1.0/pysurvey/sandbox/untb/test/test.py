'''
Created on Dec 14, 2010

@author: jonathanfriedman
'''

import numpy as np
from numpy import array, arange
import matplotlib.pyplot as plt
import cPickle as pickle


import rpy2.robjects as ro
from rpy2.robjects.packages import importr  # needed for loading R packages
import rpy2.robjects.numpy2ri               # allows R functions to accept numpy arrays


untb = importr('untb')

site = 'Midvagina'
## load abundance data
path = '/Users/jonathanfriedman/Documents/Alm/HMP_HGT/dawg/'
ts_file = path + 'data/hmp_' +site + '.pick'
f       = open(ts_file,'r')
abunds  = pickle.load(f)
f.close()

counts , otus, samples = abunds.to_matrix()
c = (counts[:,:-1]).sum(axis = 1)
print len(c[c!=0])
a = untb.count(c[c!=0])

#abunds = array([10000,1,1,10,2,2,5,0,0,0,0,0,0,0])
#a = untb.count(abunds[abunds !=0])

#print 'optimizing'
#opt = untb.optimal_params(a)
#
#print opt

preston  = untb.preston(a)

cat = list(preston.names)
c   = array(preston)

w = 0.8
plt.bar(arange(len(c))-w/2,c, width = w)
plt.xticks(arange(len(c)), cat, rotation=45)
plt.show()

