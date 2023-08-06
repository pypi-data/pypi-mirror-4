'''
Created on Jul 8, 2011

@author: jonathanfriedman
Methods for making figures look that much lovelier.
'''

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patheffects
import numpy as np



class EndArrow(mpl.patheffects._Base):
    """
    A matplotlib patheffect to add arrows at the end of a path.
    Based on:
    http://stackoverflow.com/questions/4694478/center-origin-in-matplotlib
    """
    def __init__(self, headwidth=5, headheight=5, facecolor=(0,0,0), **kwargs):
        super(mpl.patheffects._Base, self).__init__()
        self.width, self.height = headwidth, headheight
        self._gc_args = kwargs
        self.facecolor = facecolor

        self.trans = mpl.transforms.Affine2D()

        self.arrowpath = mpl.path.Path(
                np.array([[-0.5, -0.2], [0.0, 0.0], [0.5, -0.2], 
                          [0.0, 1.0], [-0.5, -0.2]]),
                np.array([1, 2, 2, 2, 79]))

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        scalex = renderer.points_to_pixels(self.width)
        scaley = renderer.points_to_pixels(self.height)

        x0, y0 = tpath.vertices[-1]
        dx, dy = tpath.vertices[-1] - tpath.vertices[-2]
        azi =  np.arctan2(dy, dx) - np.pi / 2.0 
        trans = affine + self.trans.clear(
                ).scale(scalex, scaley
                ).rotate(azi
                ).translate(x0, y0)

        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)
        self._update_gc(gc0, self._gc_args)

        if self.facecolor is None:
            color = rgbFace
        else:
            color = self.facecolor

        renderer.draw_path(gc0, self.arrowpath, trans, color)
        renderer.draw_path(gc, tpath, affine, rgbFace)
        gc0.restore()


def half_frame(ax=None):
    '''
    Remove the top and right parts of a figure frame.
    '''
    if ax is None:
        ax = plt.gca()    
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

def bar_style(ax=None, **kwargs):
    '''
    Remove all part of the frame other than the buttom one
    and add horizontal grid lines 
    '''
    if ax is None:
        ax = plt.gca()
    ## make grid
    kwargs.setdefault('which','major')
    kwargs.setdefault('ls','solid')
    kwargs.setdefault('lw',0.3)
    kwargs.setdefault('color','gray')
    ax.yaxis.grid(True, **kwargs)  
    ## remove spines
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('none')
    
    

def polish_legend(ax=None, fontsize=16, linewidth=1.5):
    '''
    Remove frame from legend and make font bigger
    '''
    if ax is None:
        ax = plt.gca()
    leg = ax.get_legend()
    ltext  = leg.get_texts()
    llines = leg.get_lines()
    plt.setp(ltext, fontsize = fontsize)
    plt.setp(llines, linewidth = linewidth)
    leg.draw_frame(False) 


def spine_placement(ax=None, xloc='center', yloc='center', arrows=False):
    """
    Move the spines of given "ax" to given location.
    Draw only one x spine and one y spine.
    Based on:
    http://matplotlib.sourceforge.net/examples/pylab_examples/spine_placement_demo.html
    http://stackoverflow.com/questions/4694478/center-origin-in-matplotlib
    """
    if ax is None:
        ax = plt.gca()

    # Set the axis's spines to be centered at the given point
    # (Setting all 4 spines so that the tick marks go in both directions)
    ax.spines['left'].set_position(xloc)
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_position(yloc)
    ax.spines['top'].set_color('none')
    ax.spines['left'].set_smart_bounds(True)
    ax.spines['bottom'].set_smart_bounds(True)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    
    # Draw an arrow at the end of the spines
    if arrows:
        ax.spines['left'].set_path_effects([EndArrow()])
        ax.spines['bottom'].set_path_effects([EndArrow()])


def graph_paper_grid(ax=None):
    '''
    Add a 'graph paper' like grid to given ax.
    Based on:
    http://stackoverflow.com/questions/4694478/center-origin-in-matplotlib
    '''
    if ax is None:
        ax = plt.gca()

    # On both the x and y axes...
    for axis in [ax.xaxis, ax.yaxis]:
        # Turn on minor and major gridlines and ticks
        axis.set_ticks_position('both')
        axis.grid(True, 'major', ls='solid', lw=0.5, color='gray')
        axis.grid(True, 'minor', ls='solid', lw=0.1, color='gray')
        axis.set_minor_locator(mpl.ticker.AutoMinorLocator())



def test_spine_placement():
    fig = plt.figure()
    x = np.linspace(0,2*np.pi,100)
    y = 2*np.sin(x)
    ax = fig.add_subplot(1,1,1)
    ax.plot(x,y)
    spine_placement(arrows=True)
    graph_paper_grid()
    plt.show()



if __name__ == '__main__':
    test_spine_placement()
    
    
    