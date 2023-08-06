'''
Created on Jul 8, 2011

@author: jonathanfriedman
'''
import pylab as pl
import matplotlib.cm as cm
import numpy as np

from matplotlib.colors import rgb2hex

def array2colors(x, cmap=cm.jet, **kwargs):
    '''
    Return rgba colors corresponding to values of x from desired colormap.
    Inputs:
        x         = 1D iterable of strs/floats/ints to be mapped to colors.
        cmap      = either color map instance or name of colormap as string. 
        vmin/vmax = (optional) float/int min/max values for the mapping.
                    If not provided, set to the min/max of x.
    Outputs:
        colors = array of rgba color values. each row corresponds to a value in x.
    '''
    ## get the colormap
    if type(cmap) is str: 
        if cmap not in cm.datad: raise ValueError('Unkown colormap %s' %cmap)
        cmap = cm.get_cmap(cmap)
    
    x = np.asarray(x)
    isstr = np.issubdtype(x.dtype, str)
    if isstr:
        temp = np.copy(x)
        x_set = set(x)
        temp_d = dict((val,i) for i,val in enumerate(x_set))
        x = [temp_d[id] for id in temp]   
    ## get the color limits
    vmin = kwargs.get('vmin', np.min(x))
    vmax = kwargs.get('vmax', np.max(x))
    ## set the mapping object
    t = cm.ScalarMappable(cmap=cmap)
    t.set_clim(vmin, vmax)
    ## get the colors
    colors = t.to_rgba(x)
    if hex:
       colors = [rgb2hex(c) for c in colors] 
    return colors
  
    
#def test_array2colors():
#    x = np.arange(0,2,.1)
#    pl.scatter(x,x, c = x, s = 50)
#    colors = array2colors(x, cmap = 'Accent', vmax = 1)
#    pl.scatter(x,x**2,c=colors, s = 50, alpha = 0.5)
#    pl.show()
#
#def test_array2colors2():
#    cols = ['a','b','a','c','d','b']
#    x = np.arange(len(cols))
#    colors = array2colors(cols, cmap='hot', hex=True)
#    print colors
#    pl.scatter(x,x**2,c=colors, s = 50)
#    pl.show()
    
if __name__ == '__main__':
    test_array2colors()
    test_array2colors2()
    