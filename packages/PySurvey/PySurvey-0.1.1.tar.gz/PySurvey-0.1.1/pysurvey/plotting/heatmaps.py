'''
Created on Aug 11, 2012

@author: jonathanfriedman

Source:
http://stackoverflow.com/questions/11505708/lining-up-labelled-dendrograms-with-a-large-matrix
'''

import scipy
import pylab as pl
import scipy.cluster.hierarchy as sch
import pysurvey.util.distances as distances
import numpy as np

from numpy import arange, log10, nan, array
from matplotlib import pyplot as plt
from matplotlib import ticker as mtk

from matplotlib.ticker import FixedLocator
class FixedDynamicLocator(FixedLocator):
    def __call__(self):
        'Return the locations of the ticks'
        from matplotlib import transforms as mtransforms
        vmin, vmax = self.axis.get_view_interval()
        vmin, vmax = mtransforms.nonsingular(vmin, vmax, expander = 0.05)
        if vmax<vmin:
            vmin, vmax = vmax, vmin
        
        l = self.locs
        locs_inview = l[(l>vmin)&(l<vmax)]
        
        if self.nbins is None:
            return locs_inview
        step = max(int(0.99 + len(locs_inview) / float(self.nbins)), 1)
        ticks = locs_inview[::step]
        for i in range(1,step):
            ticks1 = locs_inview[i::step]
            if np.absolute(ticks1).min() < np.absolute(ticks).min():
                ticks = ticks1
        return ticks

def shrink_ax(ax, left=0, right=0, top=0, bottom=0):
    wshrink = right + left
    hshrink = top + bottom
    left_old, bottom_old, width_old, height_old = ax.get_position().bounds
    left_new   = left_old + left
    bottom_new = bottom_old + bottom
    width_new  = width_old - wshrink
    height_new = height_old - hshrink
    ax.set_position([left_new, bottom_new, width_new,height_new]) 
    
def get_label_sizes(fig, labels, axis):
    sizes = np.zeros(len(labels))
    for i,label in enumerate(labels):
        bbox = label.get_window_extent().inverse_transformed(fig.transFigure)
        if axis=='y':
            sizes[i] = bbox.width
        elif axis=='x':
            sizes[i] = bbox.height
    return sizes

def _list2ints(l):
    s = set(l)
    s.discard(nan)
    d = dict((v,i) for i,v in enumerate(s))
    d[nan] = nan
    ints = array([d[li] for li in l])
    return ints

def _parse_strip(strip):
    if strip is None:
        return None
    strip = np.asarray(strip)
    if not np.issubsctype(strip, np.number):
#    if strip.dtype == object:
        return _list2ints(strip)
    else:
        return strip

def make_dendrogram(matrix, ax, dist_mat, metric, **kwargs):
        ##     
        log      = kwargs.pop('log', False)
        linkage  = kwargs.pop('linkage', 'average')
        if log: data = log10(matrix)
        else:   data = matrix
        if dist_mat: D = data
        else:        D = distances.pdist(data, metric)
        Y = sch.linkage(D, method=linkage)
        kwargs.setdefault('color_threshold', 'default')
        dendro_color = kwargs.pop('dendro_color','k') 
        kwargs.setdefault('link_color_func', lambda k: dendro_color)
        Z = sch.dendrogram(Y, **kwargs)
        return Z

def clustered_heatmap(matrix, dist_mat=False, **kwargs):
    ## parse input args
    #clustering args
    rmetric = kwargs.pop('rmetric', 'euclidean')
    cmetric = kwargs.pop('cmetric', 'euclidean')
    rsort  = kwargs.pop('rsort', True)
    csort  = kwargs.pop('csort', True)
    rdendro_kwarg = kwargs.pop('rdendro_kwarg', {})
    cdendro_kwarg = kwargs.pop('cdendro_kwarg', {})
    #ploting args
    frame      = kwargs.pop('frame', True)
    colorbar   = kwargs.pop('colorbar', True)
    kwargs.setdefault('cmap','jet')
    kwargs.setdefault('interpolation', 'nearest')
    kwargs.setdefault('aspect', 'auto') 
    kwargs.setdefault('origin','lower')
    #label args
    plot_rlabels = kwargs.pop('plot_rlabels', True)
    plot_clabels = kwargs.pop('plot_clabels', True)
    rnbins = kwargs.pop('rnbins', 49)
    cnbins = kwargs.pop('cnbins', 49)
    rlabels = kwargs.pop('rlabels', None)
    clabels = kwargs.pop('clabels', None)
    rfontsize = kwargs.pop('rfontsize', 'small') 
    cfontsize = kwargs.pop('cfontsize', 'small') 
    xlabel     = kwargs.pop('xlabel', '')
    ylabel     = kwargs.pop('ylabel', '')
    cbfontsize = kwargs.pop('cbfontsize', 'small')
    cblabel   = kwargs.pop('cblabel', '')
    #color strips
    cstrip = _parse_strip(kwargs.pop('cstrip', None))
    rstrip = _parse_strip(kwargs.pop('rstrip', None))
    cstrip_kwargs = kwargs.pop('cstrip_kwargs', {})
    rstrip_kwargs = kwargs.pop('rstrip_kwargs', {})
    #general
    figsize   = kwargs.pop('figsize', (8,8))
    file = kwargs.pop('file',None)
    show = kwargs.pop('show',True)
    #interactive args
    interactive = kwargs.pop('interactive', True)
    interactive_kwargs = kwargs.pop('interactive_kwargs', {})
    cinteractive_kwargs = kwargs.pop('cinteractive_kwargs', {'fonstsize':4})
    rinteractive_kwargs = kwargs.pop('rinteractive_kwargs', {'fonstsize':4})
    for ikwargs in (interactive_kwargs,cinteractive_kwargs, rinteractive_kwargs):
        ikwargs.setdefault('write', True)
        ikwargs.setdefault('draw', True)
        ikwargs.setdefault('title', False) 
    rannotes = kwargs.pop('rannotes', rlabels)
    cannotes = kwargs.pop('cannotes', clabels)
    
    
    axes = {} # axes objects generated to be returned
    fig  = pl.figure(figsize=figsize)
    n, m = np.shape(matrix)
    
    rlw_given  = False
    clw_given  = False
    cblw_given = False
    rlabel_width  = 0
    clabel_width  = 0
    cblabel_width = 0
    if 'rlabel_width' in kwargs:
        rlabel_width = kwargs.pop('rlabel_width', 0)
        rlw_given = True
    if 'clabel_width' in kwargs:
        clabel_width = kwargs.pop('clabel_width', 0)
        clw_given = True
    if 'cblabel_width' in kwargs:
        cblabel_width = kwargs.pop('cblabel_width', 0)
        cblw_given = True

    ## set subfigure spacing & locations
    edge_gap     = kwargs.pop('edge_gap', 0.02)
    dendro_gap   = kwargs.pop('dendro_gap', 0.005)
    strip_gap    = kwargs.pop('strip_gap', 0.015)
    cbar_gap     = kwargs.pop('cbar_gap', 0.01)
    dendro_width = kwargs.pop('dendro_width', 0.15)
    cbar_width   = kwargs.pop('cbar_width', 0.02)
    strip_width  = kwargs.pop('strip_width', 0.01)
    if not colorbar: 
        cbar_width      = 0
        cblabel_width = 0
    if cstrip is not None: 
        cstrip_width = strip_width
        cstrip_gap   = strip_gap
    else:      
        cstrip_width = 0
        cstrip_gap   = 0
    if rstrip is not None: 
        rstrip_width = strip_width
        rstrip_gap   = strip_gap
    else:      
        rstrip_width = 0
        rstrip_gap   = 0
    
    if csort: 
        cdendro_width = dendro_width
        cdendro_gap   = dendro_gap
    else:
        cdendro_width = 0
        cdendro_gap   = 0
    if rsort: 
        rdendro_width = dendro_width
        rdendro_gap   = dendro_gap
    else:
        rdendro_width = 0
        rdendro_gap   = 0

    data_width  = (1- 2*edge_gap -
                   rdendro_width - rdendro_gap -
                   rstrip_width - rstrip_gap - 
                   rlabel_width - 
                   cbar_gap - cbar_width - cblabel_width)
    data_height  = (1 - 2*edge_gap -
                   cdendro_width - cdendro_gap -
                   cstrip_width - cstrip_gap -
                   clabel_width)

    ## Compute and plot row dendrogram over on the left.    
    drow_left   = edge_gap
    drow_bottom = edge_gap
    drow_width  = rdendro_width
    drow_height = data_height
    if rsort:        
        drow_width  = dendro_width
        rdendro_pos = [drow_left,drow_bottom,drow_width,drow_height]    
        rdendro_ax  = fig.add_axes(rdendro_pos, frame_on=False)
        rdendro_ax.set_axis_off()
        rlog = kwargs.pop('rlog', False)
        rdendro_kwarg.setdefault('log',rlog)
        rdendro_kwarg.setdefault('orientation','right')
        Zrow = make_dendrogram(matrix, rdendro_ax, dist_mat,
                               rmetric, **rdendro_kwarg)
        rindex  = Zrow['leaves']
        yextent = rdendro_ax.get_ylim()[1]
    else:
        rdendro_ax = None
        rindex     = kwargs.get('rorder', arange(n))
        yextent    = 10*n 
    axes['rdendro'] = rdendro_ax

    ## Compute and plot col dendrogram up top.
    dcol_left   = (edge_gap + rdendro_width + rdendro_gap +
                   rstrip_width + rstrip_gap + 
                   rlabel_width) 
    dcol_bottom = 1 - edge_gap - cdendro_width
    dcol_height = cdendro_width 
    dcol_width  = data_width
    if csort:        
        cdendro_pos = [dcol_left,dcol_bottom,dcol_width,dcol_height]
        cdendro_ax = fig.add_axes(cdendro_pos,frame_on=False)
        cdendro_ax.set_axis_off()
        clog = kwargs.pop('clog', False)
        cdendro_kwarg.setdefault('log',clog)
        cdendro_kwarg.setdefault('orientation','top')
        Zcol = make_dendrogram(matrix.transpose(), cdendro_ax, dist_mat, 
                               cmetric, **cdendro_kwarg)
        xlim = cdendro_ax.get_xlim()
        xextent = xlim[1]
        cindex = Zcol['leaves'] 
    else:
        dcol_height = 0
        cindex      = kwargs.get('corder', arange(m))
        cdendro_ax = None
        xextent = 10*m
    axes['cdendro'] = cdendro_ax
        
    ## Plot sorted data matrix matrix.
    mat_left   = dcol_left 
    mat_bottom = drow_bottom
    mat_width  = data_width
    mat_height = data_height
    mat_pos = [mat_left,mat_bottom,mat_width,mat_height]
    matrix_ax = fig.add_axes(mat_pos,
            sharex = cdendro_ax,
            sharey = rdendro_ax)
    
    plot_log   = kwargs.pop('plot_log', False)
    if plot_log: matrix = log10(matrix)
    mat = matrix[rindex,:]
    mat = mat[:,cindex]
    extent=(0, xextent, 0, yextent)
    kwargs.setdefault('extent', extent)
    im = matrix_ax.matshow(mat,  **kwargs)
    
    ## Plot column color strip
    if cstrip is not None:
        cstrip_left   = mat_left 
        cstrip_bottom = dcol_bottom - cdendro_gap - cstrip_width
        cstrip_pos    = [cstrip_left,cstrip_bottom,mat_width,cstrip_width]
        cstrip_ax = fig.add_axes(cstrip_pos, frame_on=False,
                                sharex = matrix_ax)
        cstrip_ax.set_axis_off()
        cstrip_kwargs.setdefault('cmap', 'Spectral')
        cstrip_kwargs.setdefault('origin', 'lower')
        extent=(0, xextent, 0, 0.5*yextent)
        cstrip_kwargs.setdefault('extent', extent)
        cstrip_sotred = cstrip[cindex]
        cstrip_ax.matshow([cstrip_sotred], **cstrip_kwargs)
    else:
        cstrip_ax = None
    axes['cstrip'] = cstrip_ax
    
    ## Plot row color strip
    if rstrip is not None:
        rstrip_left   = drow_left + drow_width + rdendro_gap
        rstrip_bottom = drow_bottom
        rstrip_pos    = [rstrip_left,rstrip_bottom,rstrip_width,data_height]
        rstrip_ax = fig.add_axes(rstrip_pos, frame_on=False,
                                sharey = matrix_ax)
        rstrip_ax.set_axis_off()
        rstrip_kwargs.setdefault('cmap', 'Spectral')
        rstrip_kwargs.setdefault('origin', 'lower')
        extent=(0, 0.5*xextent, 0, yextent)
        rstrip_kwargs.setdefault('extent', extent)
        rstrip_sotred = rstrip[rindex]
        rstrip_ax.matshow(np.transpose([rstrip_sotred]), **rstrip_kwargs)
    else:
        rstrip_ax = None
    axes['rstrip'] = rstrip_ax
    
    ## set ticks
    rlabels_sorted = [rlabels[i] for i in rindex]
    clabels_sorted = [clabels[i] for i in cindex]
    rLabels = matrix_ax.set_yticklabels(rlabels_sorted)
    cLabels = matrix_ax.set_xticklabels(clabels_sorted)
    
#    xlocator = mtk.IndexLocator(10, 5)
#    ylocator = mtk.IndexLocator(10, 5)
#    xlocator.MAXTICKS = 1e6
#    ylocator.MAXTICKS = 1e6
    
    if plot_rlabels: 
        rvisible = True
        ylim = matrix_ax.get_ylim()
        ylocs = arange(ylim[0]+5,ylim[1]+5,10)
        ylocator = FixedDynamicLocator(ylocs, nbins=rnbins)
        plt.setp(matrix_ax.get_yticklabels(), visible=rvisible,
            fontstretch='ultra-condensed', fontsize=rfontsize)
    else:            
        rvisible = False
        ylocator = mtk.NullLocator()
    if plot_clabels: 
        cvisible = True
        xlim = matrix_ax.get_xlim()
        xlocs = arange(xlim[0]+5,xlim[1]+5,10)
        xlocator = FixedDynamicLocator(xlocs, nbins=cnbins)
        plt.setp(matrix_ax.get_xticklabels(), visible=cvisible, rotation='90',
            fontstretch='ultra-condensed', fontsize=cfontsize)
    else:            
        cvisible = False
        xlocator = mtk.NullLocator()
    matrix_ax.yaxis.set_major_locator(ylocator)
    matrix_ax.xaxis.set_major_locator(xlocator)
    
    ## plot colorbar.
    if colorbar:
        cbar_left   = mat_left + mat_width + cbar_gap
        cbar_bottom = mat_bottom
        cbar_height = data_height 
        cbar_ax = fig.add_axes([cbar_left,cbar_bottom,cbar_width,cbar_height])
        axes['cbar'] = cbar_ax
        cb = pl.colorbar(im, cax=cbar_ax)
        plt.setp(cbar_ax.get_yticklabels(),
                 fontstretch='ultra-condensed', fontsize=cbfontsize)
        cb.set_label(cblabel, fontsize=cbfontsize)
        # adjust axes location based on cbar label size
        if not cblw_given:
            fig.canvas.draw()
            cbLabels  = cbar_ax.get_yticklabels()
            cbwidths   = get_label_sizes(fig, cbLabels, 'y')
            cbwidthmax = np.max(cbwidths)
            shrink_ax(matrix_ax,right=cbwidthmax)
            shrink_ax(cbar_ax, right=cbwidthmax, left=-cbwidthmax)
            if csort: 
                shrink_ax(cdendro_ax, right=cbwidthmax)
            if cstrip is not None: 
                shrink_ax(cstrip_ax, right=cbwidthmax)
    
    ## adjust axes location based on row/col label size
    fig.canvas.draw()
    if not rlw_given and plot_rlabels:
        rwidths   = get_label_sizes(fig, rLabels, 'y')
        rwidthmax = np.max(rwidths)
        shrink_ax(matrix_ax,left=rwidthmax)
        if csort: 
            shrink_ax(cdendro_ax,left=rwidthmax)
        if cstrip is not None: 
            shrink_ax(cstrip_ax,left=rwidthmax)
    if not clw_given and plot_clabels:
        cwidths = get_label_sizes(fig, cLabels, 'x')
        cwidthmax = np.max(cwidths)
        shrink_ax(matrix_ax,top=cwidthmax)
        if rsort: 
            shrink_ax(rdendro_ax,top=cwidthmax)
        if rstrip is not None:
            shrink_ax(rstrip_ax,top=cwidthmax)
        if colorbar: 
            shrink_ax(cbar_ax, top=cwidthmax)

    fig.canvas.draw()
    if file is not None: fig.savefig(file, bbox_inches='tight')

    if interactive:
        from interactive.annotators import HeatmapAnnotator
        rannotes_sorted = map(lambda i:rannotes[i], rindex)
        cannotes_sorted = map(lambda i:cannotes[i], cindex)
        HeatmapAnnotator(arange(5,10*n,10), arange(5,10*m,10), 
                         rannotes=rannotes_sorted, cannotes=cannotes_sorted, 
                         axis=matrix_ax,
                         **interactive_kwargs)
        if cstrip is not None:
            HeatmapAnnotator([25], arange(5,10*m,10), 
                             cannotes=cstrip_sotred, 
                             axis=cstrip_ax,
                             ytol=1,
                             **cinteractive_kwargs)
        if rstrip is not None:
            HeatmapAnnotator(arange(5,10*n,10), [37.5], 
                         rannotes=rstrip_sotred, 
                         axis=rstrip_ax,
                         xtol=1,
                         **rinteractive_kwargs)
    
    
    if show: pl.show()

    return mat, rlabels_sorted, clabels_sorted, axes


def plot_heatmap(smat, **kwargs):
    '''
    Plot heatmap of self, sorted by heirarchical clustering with given distance metric
    '''            
    matrix, row_labels, col_labels = smat.to_matrix()
    kwargs.setdefault('plot_rlabels', False)
    kwargs.setdefault('plot_clabels', False)
    kwargs.setdefault('rlabels', row_labels)
    kwargs.setdefault('clabels', col_labels)
    cstrip = kwargs.pop('cstrip', None)
    if isinstance(cstrip, str): cstrip = smat.get_meta('c')[cstrip]
    kwargs['cstrip'] = cstrip
    rstrip = kwargs.pop('rstrip', None)
    if isinstance(rstrip, str): rstrip = smat.get_meta('r')[rstrip]
    kwargs['rstrip'] = rstrip
    return clustered_heatmap(matrix, **kwargs)

def test_plot_heatmap():
    from survey.metaFrame import MetaDataFrame
    from survey import DataFrame
    rows = ['r2', 'r0', 'r1']
    cols = ['c0', 'c1']
    metac = DataFrame([['sample1','big'],['sample0','small']], index = ['c1','c0'], columns = ['name', 'size'])
    metar = DataFrame([['otu0',5],['otu2',10],['otu1',10]], index = ['r0','r2','r1'], columns = ['name', 'IQ'])
    mat = np.array([ [2., 1], [1, 3], [10, 15] ])
    df = MetaDataFrame(mat, index=rows, columns=cols, meta_cols = metac, meta_rows=metar)
    plot_heatmap(df, 
                 rstrip='IQ', cstrip='size',
                 rsort=True, plot_rlabels=True, 
                 csort=False, plot_clabels=True,
                 cmap = 'hot', 
                 rstrip_kwargs = {'cmap':'Accent'}, cstrip_kwargs = {'cmap':'Reds'},
                 interactive_kwargs = {'text_kwargs' :{'color':'w','fontsize':15}},
                 )

def test_clustered_heatmap():
    import scipy
    n = 1000
    m = 15
    x = scipy.rand(n,m)
    row_inds = [1,3,5,7]
    col_inds = [0,2,4,6]
    x[row_inds,:] *= 5
    x[:,col_inds] *= 5
    metric='euclidean'
    
#    cstrip = np.zeros(m)
#    cstrip[col_inds] = 1
    cstrip = array(['a']*m)
    cstrip[1:4] = 'b'
    cstrip[4:8] = 'c'
    
    rstrip = np.zeros(n)
    rstrip[row_inds] = 1
    
    rlabels = map(lambda i: '' + str(i), range(n))
    clabels = map(lambda i: 'abcefghij' +str(i), range(m))
    clustered_heatmap(x, rlabels=rlabels, clabels=clabels, show=True,
                cmap='jet', colorbar=True,
                csort=False, rsort=True,
                plot_clabels=True, plot_rlabels=True,
#                rlabel_width=0.0,
#                clabel_width=0.05,
                cbfontsize=10,
#                strip_width=0.05,
                cstrip=cstrip, rstrip=rstrip)


if __name__ == '__main__':
    test_clustered_heatmap()
#    test_plot_heatmap()
                
                
    
