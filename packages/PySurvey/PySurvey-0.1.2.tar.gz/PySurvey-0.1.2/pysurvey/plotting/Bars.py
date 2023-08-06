'''
Created on Jul 8, 2011

@author: jonathanfriedman

Customized bar plots, including stacked and grouped bars.
'''
import pylab
import numpy as np
from colors import array2colors


def multibar(left, heights, style = 'stacked', **kwargs):
    '''
    Make a stacked/grouped bar plot.
    Row of heights represent samples and cols variables/categories.
    In stacked style, each row will be represented by 1 bar, with the first col being on the bottom.
    In grouped style, each row will be represented by m = #cols bars, with the first col being on the left.
    Supports only vertical (rather than horizontal) bars, and positive values!
    '''
    ## parse inputs
    if 'width' in kwargs: width  = kwargs.pop('width')
    else:
        if style == 'stacked':   width = 0.8
        elif style == 'grouped': width = 0.5 
    bottom = kwargs.pop('bottom', 0)
    cmap   = kwargs.pop('cmap', 'Spectral')
    colors = kwargs.pop('colors', None)
    labels = kwargs.pop('labels', None)
    ## set some defaults for bar
    if 'align' not in kwargs: 
        align = 'center'
        kwargs['align'] = align
    if 'linewidth' not in kwargs: kwargs['linewidth'] = 0.3
    if 'alpha' not in kwargs: kwargs['alpha'] = 0.8
    ## format input data.
    hs    = np.asarray(heights) 
    left  = np.array(left, dtype = float)
    n,m   = np.shape(hs)
    ## Set labeling/legend        
    if labels: 
        label_flag = True
    else:
        label_flag = False
        labels     = ['']*m      
    ## get bar colors
    if colors is None: colors = array2colors(np.arange(m), cmap=cmap)
    ## make new figure
    fig   = pylab.figure()
    ax    = fig.add_subplot(111)
    rects = [] # list of rectangle objects returned by the bar function.
    ## set bar width
    if   style == 'stacked': w = width 
    elif style == 'grouped': 
        w    = width/m
        if align == 'center': left -= (m-1.)/2*w 
    else: raise ValueError( 'Unknown style %s' %style) 
    ## plot
    for i in xrange(0,m):
        rects.append( ax.bar(left, hs[:,i], width = w, bottom = bottom, color = colors[i], label = labels[i], **kwargs) ) 
        if style == 'stacked': 
            bottom += hs[:,i]
        elif style == 'grouped':
            left += w
    if label_flag: pylab.legend(loc = 'best')
    return rects


    
if __name__ == '__main__':
    from Beautification import *
    x = np.arange(10)
    y = np.random.rand(10,4)
    multibar(x,y, style = 'grouped', labels = ['A','B','C','D'])
    pylab.xticks(x, ['A','B','C','D'])   
    
    ax = pylab.gca()
    half_frame(ax)
    polish_legend(ax)
    pylab.show()
    
    
    
    