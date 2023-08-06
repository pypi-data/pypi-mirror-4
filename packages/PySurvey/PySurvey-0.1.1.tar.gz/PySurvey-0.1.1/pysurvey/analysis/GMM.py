'''
Created on Oct 24, 2011

@author: jonathanfriedman

Cluster samples using a Gaussian Mixture Model.
Uses the scikits.learn package
Largely based on:
http://scikit-learn.sourceforge.net/auto_examples/mixture/plot_gmm.html#example-mixture-plot-gmm-py
'''
import itertools
import pylab as pl
import numpy as np
import matplotlib as mpl


from scipy import linalg
from sklearn import mixture


def plot_GMM(X, n_components, **kwargs):
    # GMM kwargs
    kwargs.setdefault('covariance_type', 'full')
    # plot kwargs
    colors = kwargs.pop('colors',['r', 'g', 'b', 'c', 'm'])
    marker = kwargs.pop('marker', 'o')
    s = kwargs.pop('s', 5)
    alpha = kwargs.pop('alpha', .5)
    # label kwargs
    labels = kwargs.pop('sample_labels', None)
    if labels is not None:
        nl = len(labels)
        nx = len(X[:,0])
        if nl != nx:
            print 'Number of labels (%d) != number of samples (%d). Ignoring labels.' %(nl,nx)
            labels = None 
    xoff = kwargs.pop('xoff', 0.01)
    yoff = kwargs.pop('yoff', 0.01)
    fs = kwargs.pop('fs', 10)
    # output kwargs
    show = kwargs.pop('show',True)
    file = kwargs.pop('file',None)
        
    gmm = mixture.GMM(n_components, **kwargs)
    gmm.fit(X)
    Y_ = gmm.predict(X) #cluster assignments
    
    colors = kwargs.get('colors',['g', 'r', 'b', 'c', 'm'])
    color_iter = itertools.cycle (colors)
    splot = pl.subplot(1, 1, 1)
    for i, (mean, covar, color) in enumerate(zip(gmm.means_, gmm.covars_,
                                             color_iter)):
        v, w = linalg.eigh(covar)
        u = w[0] / linalg.norm(w[0])
        pl.scatter(X[Y_== i, 0], X[Y_== i, 1], s=s, marker=marker, color=color)
    
        # Plot an ellipse to show the Gaussian component
        angle = np.arctan(u[1]/u[0])
        angle = 180 * angle / np.pi # convert to degrees
        ell = mpl.patches.Ellipse(mean, 2*v[0], 2*v[1], 180 + angle, color=color)
        ell.set_clip_box(splot.bbox)
        ell.set_alpha(alpha)
        splot.add_artist(ell)
    if labels is not None:
        dx = np.diff(pl.xlim())*xoff
        dy = np.diff(pl.ylim())*yoff
        for i, l in enumerate(labels):
            x,y = X[i,:]
            splot.text(x+dx,y+dy,l,
#                       transform=ax.transAxes,
                       fontsize=fs )
    if file is not None: pl.savefig(file)
    if show: pl.show()
    return gmm, splot


def test_plot_GMM():
    from numpy.random.mtrand import multivariate_normal
    # Number of samples per component
    n_samples = 20
    
    # Generate random sample, two components
    np.random.seed(0)
    C1 = 1*np.array([[2., 0.0], [0, 2]])
    C2 = 1*np.array([[.1, -0.1], [1.7, .4]])
    m1 = np.array([0,0])
    m2 = np.array([-6,3])
    X = np.r_[multivariate_normal(m1, C1, n_samples),
              multivariate_normal(m2, C2, n_samples)]
#    X = np.random.rand(100,5)
    gmm, splot = plot_GMM(X, 2, alpha=0.5, marker='s', s=5, show=False,
                          sample_labels=[str(i) for i in xrange(2*n_samples)])
    splot.grid('on')
    pl.show()


if __name__ == '__main__':
    test_plot_GMM()