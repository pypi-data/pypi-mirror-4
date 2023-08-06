'''
Created on Jul 14, 2011

@author: jonathanfriedman
'''

import pylab

from numpy import abs, array, asarray, cumsum, nonzero, arange, random, shape
from PlotClicker import PlotClicker


class BaseAnnotator(PlotClicker):
    """
    Toggle draw of coordinates and annotation with click.
    """
    def __init__(self, xdata, ydata,  **kwargs):
        PlotClicker.__init__(self, xdata, ydata, **kwargs)
        self.drawnAnnotations = {}
        self.write = kwargs.get('write',True)
        self.draw  = kwargs.get('draw',False)
        self.title = kwargs.get('title',True)
        text_kwargs = kwargs.get('text_kwargs',{})
        text_kwargs.setdefault('ha','center')   
        self.text_kwargs = text_kwargs   
         
class Annotator(BaseAnnotator):
    """
    Toggle draw of coordinates and annotation with click.
    """   
    def __init__(self, xdata, ydata, annotes,  **kwargs):
        BaseAnnotator.__init__(self, xdata, ydata, **kwargs)
        self.annotes = annotes

    def _act(self, clickX, clickY):
        closest = self._closest2event(clickX, clickY)
        i,x,y,d = closest
        if abs(x - clickX) < self.xtol and abs(y - clickY) < self.ytol:
            annote = self.make_annote(i,x,y)
            self._annotate(x, y, annote)
        else:
            if self.title: 
                pylab.title('Not a data point.')
                pylab.draw()
    
        
    def _annotate(self, x, y, annote):
        ''' Draw the annotation on the plot and/or write it to the screen.'''
        axis    = self.axis
        if self.write: print annote
        if self.title: 
            pylab.title(annote)
            pylab.draw()
        if self.draw:
            if (x, y) in self.drawnAnnotations:
                markers = self.drawnAnnotations[(x, y)]
                for m in markers:
                    m.set_visible(not m.get_visible())
                self.axis.figure.canvas.draw()
            else:
                t = axis.text(x, y, annote, **self.text_kwargs)
                m = axis.scatter([x], [y], marker='d', c='r', zorder=100)
                self.drawnAnnotations[(x, y)] = (t, m)
                self.axis.figure.canvas.draw()
    
               
    def make_annote(self, i, x, y):
        a       = self.annotes[i]
        annote  = "(%3.2f, %3.2f) - %s" % (x, y, a)
        return annote  
    

class XYAnnotator(BaseAnnotator):
    """
    Toggle draw of coordinates and annotation with click.
    """
    def __init__(self, xdata, ydata, xannotes=None, yannotes=None,  **kwargs):
        BaseAnnotator.__init__(self, xdata, ydata, **kwargs)
        self.xdata = asarray(xdata)
        self.ydata = asarray(ydata)
        self.xannotes = xannotes
        self.yannotes = yannotes
  
    
    def _closest2event(self, clickX, clickY, axis):
        ''' Get the index and data point that's closest to the mouse event.'''
        if axis=='x':
            click = clickX
            data = self.xdata
        elif axis=='y':
            click = clickY
            data = self.ydata            
        dist = abs(data-click)
        i = dist.argmin()
        return i, data[i], dist[i]       
    
    def _act(self, clickX, clickY):
        out = self.make_annote(clickX, clickY)
        if out is not None:
            x, y, annote = out 
            self._annotate(x, y, annote)
        else:
            if self.title: 
                pylab.title('Not a data point.')
                pylab.draw()
        
    def _annotate(self, x, y, annote):
        ''' Draw the annotation on the plot and/or write it to the screen.'''
        axis    = self.axis
        if self.write: print annote
        if self.title: 
            pylab.title(annote)
            pylab.draw()
        if self.draw:
            if (x, y) in self.drawnAnnotations:
                markers = self.drawnAnnotations[(x, y)]
                for m in markers:
                    m.set_visible(not m.get_visible())
                self.axis.figure.canvas.draw()
            else:
                t = axis.text(x, y, annote, **self.text_kwargs)
                m = axis.scatter([x], [y], marker='d', c='r', zorder=100)
                self.drawnAnnotations[(x, y)] = (t, m)
                self.axis.figure.canvas.draw()
    
    def make_annote(self, clickX, clickY):
        '''
        Find the annotations for click coordinates
        '''
        print clickX, clickY
        annote = ''
        ## get x annotation
        i,x,d = self._closest2event(clickX, clickY, 'x')
        if abs(x - clickX) < self.xtol:
            if self.xannotes is not None: xannote = str(self.xannotes[i])
        else: return None
        ## get y annotation
        i,y,d = self._closest2event(clickX, clickY, 'y')
        if abs(y - clickY) < self.ytol:
            if self.yannotes is not None: yannote  = self.yannotes[i]
        else: return None
        ## make annotation str
        if self.xannotes is not None:
            annote += xannote
        if self.yannotes is not None:
            if annote: annote += ' ; '
            annote +=  str(yannote)
        return x, y, annote 

class MultibarAnnotator(XYAnnotator):
    '''
    Object for annotating multibar plots.
    '''

    def __init__(self, xdata, ydata, xannotes=None, yannotes=None, style='stacked', **kwargs):
        '''
        Constructor
        '''
        XYAnnotator.__init__(self, xdata, ydata, xannotes, yannotes, **kwargs)
        self.axis.autoscale(enable = False)
        self.style = style
        
    def make_annote(self, clickX, clickY):
        '''
        Find the annotations for click coordinates
        '''
        style   = self.style
        yannote = None
        xannote = None
        if style == 'stacked':
            ## get x annotation 
            (i,x,d) = self._closest2event(clickX, clickY, axis = 'x')
            if abs(x - clickX) < self.xtol:
                xannote  = self.xannotes[i]
            ## get y annotation
            ycum = cumsum(self.ydata[i])
            if clickY > ycum[-1] + self.ytol: pass # clicked way above top bar
            else:
                if clickY > ycum[-1]: j = len(ycum) - 1  # clicked just above top bar
                else:                 j = nonzero(ycum - clickY > 0)[0][0]           
                if j > 0: y = ycum[j-1] + (ycum[j] - ycum[j-1])/2.
                else:     y = ycum[j]/2.            
                yannote  = self.yannotes[j]
        elif style == 'grouped': raise ValueError, 'Grouped style not yet supported'
        else: raise ValueError( 'Unknown style %s' %style) 
        if xannote is not None and yannote is not None:
            annote = xannote + ';  ' + yannote
            return x, y, annote   
        else: 
            return None
         
    

class StackedAnnotator(MultibarAnnotator):
        
    def __init__(self, xdata, ydata, xannotes=None, yannotes=None, style='stacked', **kwargs):
        '''
        Constructor
        '''
        
        MultibarAnnotator.__init__(self, xdata, ydata, xannotes, yannotes, style=style, **kwargs)
        self.ydata = self.ydata.T
        self.data  = zip(self.xdata, self.ydata)


class HeatmapAnnotator(XYAnnotator):
    
    def __init__(self, rlocs, clocs, rannotes=None, cannotes=None, origin='upper', **kwargs):
        '''
        Constructor
        '''
        if rannotes is not None:  
            if origin is 'lower': 
                rannotes = rannotes[::-1]
        XYAnnotator.__init__(self, clocs, rlocs, cannotes, rannotes, **kwargs)
        self.axis.autoscale(enable=False)
          
#
#def test_Annotator():
#    x = range(10)
#    y = range(10)
#    annotes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
#    pylab.plot(x,y)
#    pylab.xlim(0,5)
#    Annotator(x, y, annotes,
#              text_kwargs = {'color':'DarkRed','fontsize':15},
#              draw = True)
#
#
#def test_HeatmapAnnotator():
#    data = array([ [0,1,2], [3,4,5], [6,7,8], [9,10,11] ])
#    rannotes = ['A','B','C','D']
#    cannotes = ['X','Y','Z']
#    pylab.matshow(data, interpolation = 'nearest', aspect='auto', origin='lower')
#    HeatmapAnnotator(arange(4), arange(3), 
#                     rannotes=rannotes, cannotes=cannotes,
#                     text_kwargs = {'color':'DarkRed','fontsize':15}, 
#                     draw=True, origin='lower')
#
#def test_XYAnnotator():
#    data = array([ [0,1,2], [3,4,5], [6,7,8], [9,10,11] ])
#    yannotes = ['A','B','C','D']
#    xannotes = ['X','Y','Z']
#    pylab.matshow(data, interpolation = 'nearest', aspect='auto', origin='lower')
#    XYAnnotator(arange(3), arange(4), 
#                xannotes=xannotes, yannotes=yannotes,
#                text_kwargs = {'color':'DarkRed','fontsize':15}, 
#                draw=True, origin='lower')
#
#    
#def testMultibarAnnotator():
#    from Bars import multibar 
#    x = arange(4)
#    y = random.rand(4,3)
#    multibar(x,y,width = 0.5, alpha = .9,  cmap = 'Spectral', align = 'center')
#    xlabels = ['A','B','C','D']
#    ylabels = ['X','Y','Z']
#    pylab.xticks(x, xlabels) 
#    MultibarAnnotator(x, y, xannotes=xlabels, yannotes=ylabels,
#                      text_kwargs = {'color':'DarkRed','fontsize':15}, 
#                      draw = True)
#
#def testStackedAnnotator():
#    from stacked_plot import stacked_plot 
#    n = 6
#    x = arange(n)
#    y = random.rand(4,n)
#    labels = ['A','B','C','D']
#    stacked_plot(x,y,  cmap = 'Spectral', linewidth = 0, alpha = .7, fill_alpha = .7, labels = labels)    
#    xlabels = ['sample%d' %i for i in xrange(n)]
#    ylabels = ['A','B','C','D']
#    StackedAnnotator(x, y, xannotes=xlabels, yannotes=ylabels,
#                     text_kwargs = {'color':'DarkRed','fontsize':15}, 
#                     draw = True)

    
if __name__ == '__main__':
    pass
#    test_Annotator()
#    test_XYAnnotator()
#    test_HeatmapAnnotator()
#    testMultibarAnnotator()
#    testStackedAnnotator()
#    pylab.show()
    
    
    
    