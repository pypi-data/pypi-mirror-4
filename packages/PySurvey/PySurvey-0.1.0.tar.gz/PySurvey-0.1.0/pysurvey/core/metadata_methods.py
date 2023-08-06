'''
Created on Jun 24, 2012

@author: jonathanfriedman 
'''

from pandas import DataFrame as DF
from core_methods import _get_axis
import numpy as np

#-------------------------------------------------------------------------------
# filter/sort/group by metadata
def sort_by_meta(frame, meta, axis=1, **kwargs):
    '''
    Sort frame by a metadata column.
    Missing metadata are replaced by NaNs before sorting.

    Parameters
    ----------
    frame : frame 
        Frame to be sorted.
    meta : frame
        Metadata be which frame will be sorted.
    axis :  {0 | 1 (default)}
        0 : sort rows.
        1 : sort columns.
    **kwargs : 
        Additional keyword argument to be passed to DataFrame's sort method
        called on the metadata frame.
        
    Returns
    -------
    Sorted frame (new instance).
    '''
    axis = _get_axis(axis)                
    if axis==0:
        meta_sorted = meta.reindex(index=frame.index).sort(**kwargs)
        new = frame.reindex(index=meta_sorted.index)
    elif axis ==1:
        meta_sorted = meta.reindex(index=frame.columns).sort(**kwargs)                  
        new = frame.reindex(columns=meta_sorted.index)
    return new

def filter_by_meta(frame, meta, criteria, axis='cols', verbose=True, 
                   how='all', filter_missing=True):
    '''
    Filter frame by a metadata, keeping only cols/rows that pass the filtering criteria.
    For more information see survey2.util.filters and survey2.filter_by_vals
    Inputs:
        criteria = [dict] keyed by metadata labels, with values being filtering functions returning bool.
        axis     = [int/str] indicate whether to filter rows or cols.
        filter_missing = [bool] indicate whether to filter out NAN's or not.

    Parameters
    ----------
    frame : frame 
        Frame to be filtered
    meta : frame
        Metadata be which frame will be filtered.
    criteria : filter-parsable/iterable of filter-parsables
        The filtering criteria. 
        Each criterion can be:
            - A triplet of (actor,comperator,value), where the actor extracts the 
              quantity of interest from each row/column and the comperator compares 
              it to the given value and returns a bool.
              Named actors include: 'sum','avg','med', 'var', 'std' and 'presence'.
              A row/col label can also be used to filter by its values. 
              To filter by the values fo a row/col who's label is a named actor, prefix 
              an underscore to it (e.g. '_sum').
              Name comperators include: '==', '!=', '>', '<', '>=', '<=', 'in'.
            - A function that accepts a Series and returns a bool.
            - A survey2.util.filters.Filter object.
    axis :  {0 | 1 (default)}
        0 : filter rows.
        1 : filter columns.
    verbose : bool (default True)
        Determines whether to print filtering info.
    how : {'all' (default) | 'any' | callable}
        'all'    - Keep row/cols that pass all filtering criteria.
        'any'    - Keep row/cols that pass any of the filtering criteria.
        callable - to be used to reduce the list of bools returned by the filters 
                   for each row/col.
    filter_missing : bool (default True) 
        Indicate whether to filter out NAN's or not.
        
    Returns
    -------
    Filtered frame (new instance).
    '''   
    from core_methods import filter_by_vals
    axis = _get_axis(axis) 
    if axis==0:
        meta   = meta.reindex(index=frame.index)
        labels = frame.index
    elif axis ==1:
        meta   = meta.reindex(index=frame.columns)                 
        labels = frame.columns                           
    ## set behavior on missing metadata
    if filter_missing is True:
        nan_val = False
    elif filter_missing is False:
        nan_val = True
    else:
        nan_val = None
    ## filter metadata                
    meta_f = filter_by_vals(meta, criteria, axis=0, verbose=False, how=how, nan_val=nan_val)   
    labels_f = meta_f.index
    ## filter frame
    if axis == 1:
        filtered = frame.reindex(columns=labels_f)
    elif axis == 0:
        filtered = frame.reindex(index=labels_f)
    ## print message
    if verbose:
        axis_s = {0:'rows',1:'columns'}
        s = ['Dropped %d %s' %(len(labels)-len(labels_f),axis_s[axis]),
             'Resulting size is (%d,%d)' %filtered.shape]
        print '\n'.join(s) +'\n'
    return filtered


def drop_missing_meta(frame, meta, axis='cols', labels='all', verbose=True):
    '''
    Remove cols/rows with missing metadata.
    
    Parameters
    ----------
    axis :  {0 | 1 (default)}
        0 : drop rows.
        1 : drop columns.
    labels : 'all'/iterable
        Labels of cols/rows that will be checked for missing metadata.
        Other rows/cols will not be dropped.
    verbose : bool (default True)
        Determines whether to print info. 
      
    Returns
    -------
    Filtered frame (new instance).
    '''
    axis = _get_axis(axis)
    criteria = []
    if labels == 'all': 
        labels = meta.columns
    elif not hasattr(labels, '__iter__'):
        labels = (labels,)
    for l in labels: 
        criteria.append(('_'+l, lambda x,y:True, True)) #fake filter that always return true
    return filter_by_meta(frame, meta, criteria, axis=axis, verbose=verbose, filter_missing=True)

if __name__ == '__main__':
    rows = ['r1', 'r0', 'r2', 'r3']
    cols = ['c0', 'c1', 'c2']
    metac = DF([[np.nan,'big'],
                ['Entero','small'],
                ['Blautia','tiny']], 
               columns=['name', 'size'],
               index=cols)
    metar = DF([[np.nan,20],
                ['subject2',50],
                ['subject1',35]], 
               columns=['name', 'age'],
               index =['r3','r2','r1']) 
    mat = np.array([[2., np.NAN,1], 
                    [1, 3, 2],
                    [10, 15,3],
                    [0,0,1]])
    df = DF(mat, index=rows, columns=cols)
    
    print df,'\n'
    print metar, '\n'
    print metac, '\n'
#    print filter_by_meta(df,metar, [('_age','<=', 35),('_name','in', ['subject2','subject3'])], 
#                         axis='r',filter_missing=True, how='any'), '\n'
#    print filter_by_meta(df,metar, {'age':'< 35'}, axis='r',filter_missing=False), '\n'
    print drop_missing_meta(df,metar, axis='r', labels='all'), '\n'
#    print sort_by_meta(df,metar, axis=0,columns='age'), '\n'
#    print sort_by_meta(df,metar, axis=0,columns='age', ascending=False), '\n'
#    print sort_by_meta(df,metac,columns='name')
    
    ## test metadata sorting
#    df['a'] = 1
#    z = df.sort_by_meta(ascending=True, column='size')
#    z = df.sort_by_meta(ascending=True, axis='rows')
    
    
    