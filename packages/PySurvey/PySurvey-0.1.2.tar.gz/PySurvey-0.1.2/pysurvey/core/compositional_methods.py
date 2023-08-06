'''
Created on Jun 24, 2012

@author: jonathanfriedman 
'''

import numpy as np
from pandas import DataFrame as DF
from numpy import array, asarray, zeros, log, var, matrix
from pysurvey.core.core_methods import _get_axis

def alr(frame, ref=None, axis=0):
    '''
    Compute the additive log-ratio (alr) transformation 
    with respect to the component given in ref.
    
    Parameters
    ----------
    frame : DataFrame
        Frame to be transformed
    ref : valid label | None
        Label of component to be used as the normalization reference.
        i.e.  values of other component will be divided by values of 
        this reference component.
        IF None is passed (default), the last col/row is used as ref.
    axis : {0, 1}
        0 : transform each row (default)
        1 : transform each colum
    ''' 
    axis = _get_axis(axis)
    if ref is None:
        label = frame._get_axis(1-axis)[-1]
    else:
        label = ref
    if axis==0:
        norm = 1.*frame[label]
    elif axis==1:
        norm = 1.*frame.xs(label)
    temp = frame.apply(lambda x: log(x/norm), axis=axis)
    return temp.drop(label,1-axis)

def clr(frame, centrality='mean', axis=0):
    '''
    Do the central log-ratio (clr) transformation of frame.
    'centraility' is the metric of central tendency to divide by 
    after taking the logarithm.
    '''
    temp = log(frame)
    if   centrality is 'mean':   f = lambda x: x - x.mean()
    elif centrality is 'median': f = lambda x: x - x.median()
    z = temp.apply(f, axis=1-axis)
    return z


def variation_mat(frame, shrink=False):
    '''
    Return the variation matrix of frame.
    Element i,j is the variance of the log ratio of components i and j.
    Can also employ shrunken estimation of the variation matrix, 
    following Rainer Opgen-Rhein and Korbinian Strimmer 2007a.
    '''
    frame_a = 1.*asarray(frame)
    k    = frame_a.shape[1]
    V      = zeros((k,k))
    y_mat  = []
    for i in range(k-1):
        for j in range(i+1,k):
            y     = array(log(frame_a[:,i]/frame_a[:,j]))
            y_mat.append(y)
            v = var(y, ddof=1) # set ddof to divide by (n-1), rather than n, thus getting an unbiased estimator (rather than the ML one). 
            V[i,j] = v
            V[j,i] = v
    if not shrink: 
        return matrix(V)
    else:
        from pysurvey.util.R_utilities import var_shrink
        data         = (array(y_mat)).transpose()
        V_shrink_vec = var_shrink(data)
        V_shrink     = zeros((k,k))
        m = 0
        for i in range(k-1):
            for j in range(i+1,k):
                V_shrink[i,j] = V_shrink_vec[m]
                V_shrink[j,i] = V_shrink[i,j]
                m += 1 
        return matrix(V_shrink) 

def replace_zeros(frame, type='multiplicative', e=0.5):
    '''
    Replace the zeros by a small value by imputation.
    Return new object.
    
    Inputs:
        e = [float] fraction of minimal value to use as imputed value delta.
    '''
    new = 1.*frame.copy()
    for i, row in new.iterrows():
        inds_z      = (row ==0).nonzero()[0] # indices of zeros
        inds        = (row > 0).nonzero()[0] # indices of no zeros
        delta       = e * np.min(row[inds])  # imputed value for current sample
        row[inds_z] = delta                  # replace zeros by imputed values
        if type is 'simple':
            row /= row.sum()
        elif type is 'multiplicative':
            row[inds] *= (1-delta*len(inds_z))   
        new.ix[i] = row
    return new 

if __name__ == '__main__':
    rows = ['r1', 'r0', 'r2', 'r3']
    cols = ['c0', 'c1', 'c2']
    metac = DF([[np.nan,'big'],
            ['Entero','small'],
            ['Blautia','tiny']], 
           columns=['name', 'Size'],
           index=cols)
    mat = np.array([[2., np.NAN,1], 
                    [1, 3, 2],
                    [10, 15,3],
                    [0,0,1]])
    df = DF(mat, index=rows, columns=cols)
#    print df,'\n'
#    print filter_by_vals(df,[('sum','<=',3),('presence','>',1)],axis='rows'),'\n'   



