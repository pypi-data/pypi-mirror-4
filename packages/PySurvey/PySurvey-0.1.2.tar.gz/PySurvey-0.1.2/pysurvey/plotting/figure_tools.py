'''
Created on Nov 28, 2009

@author: jonathanfriedman
'''
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms


def on_draw(event):
    '''
    Change the figure bounding box to fit y-labels length
    '''
    bboxes = []
    global ytickNames
    global fig
    for label in ytickNames:
        bbox = label.get_window_extent()
        # the figure transform goes from relative coords->pixels and we
        # want the inverse of that
        bboxi = bbox.inverse_transformed(fig.transFigure)
        bboxes.append(bboxi)

    # this is the bbox that bounds all the bboxes, again in relative
    # figure coords
    bbox = mtransforms.Bbox.union(bboxes)
    if fig.subplotpars.left < bbox.width:
        # we need to move it over
        fig.subplots_adjust(left=1.1*bbox.width) # pad a little
        fig.canvas.draw()
    return False


def format_ticks(ax, label_size  = 12, tick_length = 5, tick_width  = 2, xaxis = True, yaxis = True):
    '''
    Make tick marks and labels larger.
    '''
    if xaxis:
        for label in ax.xaxis.get_ticklabels(): label.set_fontsize(label_size)    
        for line  in ax.xaxis.get_ticklines(): 
            line.set_markersize(tick_length)
            line.set_markeredgewidth(tick_width)
    if yaxis:
        for label in ax.yaxis.get_ticklabels(): label.set_fontsize(label_size)
        for line  in ax.yaxis.get_ticklines(): 
            line.set_markersize(tick_length)
            line.set_markeredgewidth(tick_width)


def format_corrcoef_ticks(fig_loc,ax, labels,label_size  = 12, tick_length = 5, tick_width  = 2 ):
    '''
    Format ticks for correlation plot
    '''
    global ytickNames
    global fig
    fig = fig_loc
    tick_locs = np.arange(len(labels))+0.5
    plt.setp(ax,xticks = tick_locs)
    plt.setp(ax,yticks = tick_locs)
    xtickNames = plt.setp(ax, xticklabels=labels)
    ytickNames = plt.setp(ax, yticklabels=labels)
    plt.setp(xtickNames, rotation= 'vertical')
#    plt.setp(ytickNames, rotation=45)
    format_ticks(ax)
#    fig.canvas.mpl_connect('draw_event',on_draw)
#    


def format_legend(leg, **kwargs):
    '''
    Set legend properties (e.g. bounding box).
    leg can  be obtained by 'leg = ax.get_legend()'.
    '''
    fontsize   = kwargs.get('fontsize', 16)
    linewidth  = kwargs.get('linewidth', 1.5)
    draw_frame = kwargs.get('draw_frame', False)
    ltext  = leg.get_texts()
    llines = leg.get_lines()
    plt.setp(ltext, fontsize= fontsize)
    plt.setp(llines, linewidth = linewidth)
    leg.draw_frame(draw_frame) 
    
    
def remove_top_right_axes(ax):
    '''
    Remove the top and right axes and their tick marks.
    '''
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
        
    