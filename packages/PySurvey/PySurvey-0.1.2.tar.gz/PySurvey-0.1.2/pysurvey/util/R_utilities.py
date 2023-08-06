'''
Created on Aug 8, 2010

@author: jonathanfriedman

TODO: make a general Rwrapper decorator 
'''

import numpy as np
import rpy2.robjects as ro
from rpy2.robjects.packages import importr  # needed for loading R packages
from rpy2.robjects.numpy2ri import numpy2ri
ro.conversion.py2ri = numpy2ri # allows R functions to accept numpy arrays
from numpy import array

def fisher_test(counts):
    '''
    Returns the 2 sided p-value from a fisher exact test.
    Counts is a np array representing the counts in the contingency table.
    Online doc: http://www.astrostatistics.psu.edu/datasets/R/html/stats/html/fisher.test.html
    '''
    rstats = importr('stats')
    ans    = rstats.fisher_test(counts)
    p_val  = np.array(ans.rx2('p.value') )
    return p_val



def is_pd(mat):
    '''
    Check if matrix is positive definite.
    Return bool
    Online doc: http://www.uni-leipzig.de/~strimmer/lab/software/corpcor/html/rank.condition.html
    '''
    corpcor = importr('corpcor')
    flag    =  str(corpcor.is_positive_definite(mat)[0]) 
    if flag is 'False': return False
    else:             return True


def make_pd(mat, package = 'matrix', corr = False, **kwargs):
    '''
    computes the nearest positive definite of a real symmetric matrix, using the algorithm of NJ Higham (1988, Linear Algebra Appl. 103:103-118). 
    Online doc: http://www.uni-leipzig.de/~strimmer/lab/software/corpcor/html/rank.condition.html
                http://stat.ethz.ch/R-manual/R-devel/library/Matrix/html/nearPD.html
    '''
    if package is 'corpcor':
        corpcor = importr('corpcor')
        mat_pd  = np.array( corpcor.make_positive_definite(mat) )
    elif package is 'matrix':
        Rmat = importr('Matrix')
        pd   = np.array(Rmat.nearPD(mat, corr = corr))[0]
        x    = np.array( pd.do_slot('x') )
        mat_pd = x.reshape(mat.shape)
    return mat_pd
    
     
#def test_pd():
#    x = np.array([[ 1,  0.9,  -0.9],
#                  [ 0.9,  1,  0.9],
#                  [ -0.9,  0.9,  1]])
#    print is_pd(x)
#    print make_pd(x, corr = True)

    

def pcor(mat):
    '''
    Compute the partial correlation matrix of data matrix.
    '''
    corpcor = importr('corpcor')
    print corpcor.pcor_shrink(mat)
    

def var_shrink(data):
    '''
    Estimate variance of data using James-Stein shrinkage toward the median variance (of all variables).
    In data, rows are observations and cols are variables.
    Online doc: http://strimmerlab.org/software/corpcor/html/cov.shrink.html
    '''
    corpcor = importr('corpcor')
    var = np.array( corpcor.var_shrink(data) )
    return var

#def test_var_shrink():
#    from numpy.random.mtrand import multivariate_normal as mvn
#    m   = np.array([10, 1 , 0.1] + [1]*5)
#    cov = np.diag([10, 1 , 0.1] + [1]*5)
#    n   = 10
#    x = mvn(m,cov,n)
#    print np.var(x, axis = 0, ddof=1 )
#    print var_shrink(x)


def c_means(data,k,r = 2, metric = 'euclidean', maxit = 1e4, diss = False):
    '''
    Do fuzzy c-means clustering using R function 'fanny' from the 'cluster' library.
    Rows are observations (to be clusters), and cols are variables.
    k = number of clusters.
    r = fuzziness exponent. Less fuzzy as r -> 1.
    maxit = maximum number of iterations
        
    Online documentation: http://stat.ethz.ch/R-manual/R-devel/library/cluster/html/fanny.html
    '''
    import scipy.cluster.hierarchy as sch
#    ro.r('options(warn=-1)') # suppress R warnings (tends to raise warning if didn't converge in maxitr)
    rclust = importr('cluster')
    
    ## create distance matrix
    if diss: D = data
    else:
        D = sch.distance.pdist(data, metric = metric) # row distance matrix
        D = sch.distance.squareform(D)
    
    ## do clustering
    ans = rclust.fanny(D,k, diss = True, memb_exp = r, maxit = maxit)
    membership = np.array(ans.rx2('membership') )
    
    ## get hard membership assignment
    membership_hard = np.array(ans.rx2('clustering') )
    
    ## get some statistics regarding the solution
    coeff           = np.array(ans.rx2('coeff') )
    k_crisp         = np.array(ans.rx2('k.crisp') )
    silinfo         = ans.rx2('silinfo')
    avg_width       = np.array(silinfo.rx2('avg.width') )
    clust_avg_width = np.array(silinfo.rx2('clus.avg.widths') )
    stats           = {'coeff': coeff, 'k_crisp' :k_crisp, 'avg_width': avg_width, 'clust_avg_width': clust_avg_width}
    
    return membership, membership_hard, stats


def dirichlet_estimate(data):
    '''
    Estimate the parameters of a dirichlet distribution from observed data.
    Inputs:
        data = [array] rows are realizations, cols are categories.
                       values are probability of category in given realization.
                       value must be in [0,1), and rows sum to 1.
    Online doc: http://rss.acs.unt.edu/Rdoc/library/VGAM/html/dirichlet.html
    '''
    r = ro.r
    vgam = importr('VGAM')
    r.assign('y',data)
#    c_mat = 
#    r.assign('c_mat',c_mat)
    fit = r('fit = vglm(y ~ 1, dirichlet, trace = FALSE, crit="c")')
    a  = np.array(vgam.Coef(fit))   # inferred dirichlet params
    ll = np.array(r.logLik(fit)) # log-lokelihood
    return a,ll


def betbino_estimate(data):
    '''
    Estimate the parameters of a beta-binomial distribution.
    Inputs:
    data = [array] rows are realizations, cols are categories (success and fail).
                   values are counts (or probability?) of category in given realization.
    '''
    r = ro.r
    vgam = importr('VGAM')
    r.assign('y',data)
    fit = r('fit = vglm(y ~ 1, betabinomial, trace = FALSE)')
    a  = np.array(vgam.Coef(fit))   # inferred params
    ll = np.array(r.logLik(fit)) # log-lokelihood
    return a,ll



def pbetabin(k, N, a,b):
    '''
    CDF of beta binomial.
    Online doc: http://rss.acs.unt.edu/Rdoc/library/VGAM/html/betabinUC.html
    '''
    vgam = importr('VGAM')
    if isinstance(k, (int,float)): k = np.array([k]) 
    if isinstance(N, (int,float)): N = np.array([N]) 
    if not len(k) == len(N):
        raise ValueError, 'k and N must be of same length!'
    F = []
    for ki,Ni in zip(k,N):    
        F += list(vgam.pbetabin_ab(ki, Ni, a,b))
    return np.array(F)



def dbetabin(k, N, a,b):
    '''
    PMF of beta binomial.
    '''
    vgam = importr('VGAM')
    if isinstance(k, (int,float)): k = np.array([k]) 
    if isinstance(N, (int,float)): N = np.array([N]) 
    if not len(k) == len(N):
        raise ValueError, 'k and N must be of same length!'
    F = []
    for ki,Ni in zip(k,N):    
        F += list(vgam.dbetabin_ab(ki, Ni, a,b))
    return np.array(F)


def rbetabin(n, N, a, b):
    '''
    rvs from betabinomial
    '''
    vgam = importr('VGAM')
    rvs    = vgam.rbetabin_ab(n, N, a,b)
    return np.array(rvs)


def dirmulti_estimate(data):
    '''
    Estimate the parameters of a dirichlet-multinomial distribution.
    Inputs:
    data = [array] rows are realizations, cols are categories.
                   values are counts (or probability?) of category in given realization.
    
    Note that the parameterization of the distribution in this package is not the standard one.
    The parameters used are pi_i (i = 1:k-1) and phi, where pi_i is the expected value of x_i, and phi is the 'intracluster correlation'.
    Relation of fitted parameters to 'standard' dirichlet parameters:
    pi_i  = a_i/a0
    phi = 1/(a0+1)
    
    Online doc: http://rss.acs.unt.edu/Rdoc/library/VGAM/html/dirmultinomial.html
    '''
    from numpy import exp
    r    = ro.r
    vgam = importr('VGAM')  # import r package
    r.assign('y',data)      # import the data to the r console
    fit = r('fit = vglm(y ~ 1, dirmultinomial(parallel= TRUE, zero=NULL), trace = TRUE)') # do the fit
    ## import fitted params from R
    logit_phi = np.array( r('coef(fit)') )[-1]
    pi         = np.array(vgam.fitted(fit))[0,:]
    phi = exp(logit_phi)/(1+exp(logit_phi))
    ## convert fitted params to 'standard' dirichlet params 
    a0  = (1-phi)/phi
    a   = pi*a0 
    ll = np.array(r.logLik(fit)) # log-lokelihood
    return a,ll


def multinomial_estimate(data):
    '''
    Estimate the parameters of a multinomial distribution.
    Inputs:
    data = [array] rows are realizations, cols are categories.
                   values are counts (or probability?) of category in given realization.
    Online doc: http://rss.acs.unt.edu/Rdoc/library/VGAM/html/multinomial.html
    '''
    r = ro.r
    vgam = importr('VGAM')
    r.assign('y',data)
    fit = r('fit = vglm(y ~ 1, multinomial, trace = FALSE)')
    a  = np.array(vgam.fitted(fit))[0,:]   # inferred params
    ll = np.array(r.logLik(fit)) # log-lokelihood
    return a,ll


def mvn_rv(mu,sigma, n):
    '''
    Generate n samples from a multivariate normal with mean mu and covariance matrix sigma.
    '''
    r_mvn = importr('mvtnorm')
    samples = r_mvn.rmvnorm(n, mu,sigma)
    return np.array(samples)


def logitnorm_pdf(x,mu,sigma):
    '''
    Get the pdf of a logitnormal distribution with parameters mu & sigma, evaluated at points x.
    ''' 
    r_logitnorm = importr('logitnorm')
    pdf = r_logitnorm.dlogitnorm(x, mu,sigma)
    return np.array(pdf)   


def kder(x, adjust = 1):
    '''
    Kernel density estimation.
    Online doc: http://sekhon.berkeley.edu/stats/html/density.html
    '''
    r_stat = importr('stats')
    kde    = r_stat.density(x, adjust = adjust)
    points = np.array( kde.rx2('x') )
    pdf    = np.array( kde.rx2('y') )
    return points, pdf
 

def qqplot(y, x, show = True):
    '''
    Make a Quantile-Quantile plot of two datasets, or dataset against samples from theoretical distribution
    Online doc: http://sekhon.berkeley.edu/stats/html/qqnorm.html
    '''
    import matplotlib.pyplot as plt
    r      = ro.r
    r_stat = importr('stats')
    r.assign('x',x) 
    r.assign('y',y) 
    qx,qy  = array(r('qqplot(y, x, plot.it = FALSE)'))
    if show:
        plt.figure()
        plt.plot(qx,qy,'o')
        plt.plot(plt.xlim(),plt.xlim(),'--') ## add strait line
        plt.show()
    return qx,qy


def qqnorm(y, show = True):
    '''
    Make a Quantile-Quantile plot of a data set against the best fitting normal distribution.
    Online doc: http://sekhon.berkeley.edu/stats/html/qqnorm.html
    '''
    import matplotlib.pyplot as plt
    r      = ro.r
    r_stat = importr('stats')
    r.assign('y',y)
    qx,qy  = array(r('qqnorm(y, plot.it = FALSE)'))
    if show:
        plt.figure()
        plt.plot(qx,qy,'o')
#        plt.plot(plt.xlim(),plt.xlim(),'--') ## add strait line
        plt.show()
    return qx,qy
    

    


def R_qvalues(p_vals):
    qlib = importr('qvalue')
    ans = qlib.qvalue(p_vals)
    q_vals = np.array(ans.rx2('qvalues') )
    return q_vals


def fdrtool(vals, **kwargs):       
    fdrtool = importr('fdrtool')
    kwargs.setdefault('statistic', 'pvalue')
    kwargs.setdefault('plot', False)
#    r_pvals = ro.FloatVector(p_sort)
    vals = np.asarray(vals)
    Rvals = ro.FloatVector(vals)
    ans = fdrtool.fdrtool(Rvals, **kwargs)
    qvals = np.array(ans.rx2('qval') )
    pvals = np.array(ans.rx2('pval') )
#    print pvals
#    print qvals
    return pvals,qvals 



def entropy(x, method = 'shrink'):
    '''
    Use the R entropy package to calculate the entropy of observations x using given method.
    Return the entropy value. 
    Valid methods: "ML", "MM", "Jeffreys", "Laplace", "SG", "minimax", "CS", "NSB", "shrink".
    Online Doc: http://strimmerlab.org/software/entropy/ 
    '''
    rentropy = importr('entropy')
    H        = np.array(rentropy.entropy(x, method = method))
#    p_val  = np.array(ans.rx2('p.value') )
    return H


#def test_entropy():
#    x  = np.array([4, 2, 3, 2, 1, 1,0,100])
#    print entropy(x, 'CS')
#
#def test_dirichlet_estimate():
#    from numpy.random.mtrand import dirichlet
#    n = 1e3
#    a = [1,2,1]
#    data = dirichlet(a,int(n))    
#    print dirichlet_estimate(data)
#
#def test_betbino_estimate():
#    from numpy.random.mtrand import dirichlet, multinomial
#    r = ro.r
#    vgam = importr('VGAM')
#    n = int(2e2)
#    a = np.array([2]*2)
#    N = [10000] * n
#    probs = dirichlet(a,n)
#    data  = np.zeros((n,len(a)))
#    for i in range(n): data[i,:] =  multinomial(N[i],probs[i,:])  
##    x1 = np.array( r('rbetabin(n=100, size=100, prob=.5, rho=.2)') )
##    x2 = 100 - x1
##    data = np.c_[x1,x2]
#    (t ,ll) = dirmulti_estimate(data)
#    print t
#    
#def test_mvn_sample():
#    import pylab
#    k = 3
#    n = 1000
#    mu    = np.array([1]*k)
#    sigma = np.diag([1.0]*k)
#    sigma[1:3,0] = 0.7
#    sigma[0,1:3] = 0.7
#    sigma[1,2] =-0.7
#    sigma[2,1] =-0.7
#    print sigma
##    samples =  mvn_sample(mu,sigma,n)
##    c = np.corrcoef(samples, rowvar = 0)
##    print c
#    
#def test_logitnorm():
#    import pylab
#    x = np.linspace(0,1,10000)
#    mu    = 1
#    sigma = 2
#    pdf =  logitnorm_pdf(x,mu,sigma)
#    pylab.plot(x,pdf)
#    pylab.show()
#     
#def test_fdrtool():
#    p = np.random.rand(100)
#    p.sort()
#    print p
#    fdrtool(p, statistic='correlation')
#    
if __name__ == '__main__':
    pass
    
#    a = 1
#    b = 1
#    N = 100
#    k = np.array([1,2,3]) 
#    k = np.arange(11)
#    f= pbetabin(k, N, a,b)
#    print f
#    print f.sum()
    
#    print rbetabin(1, N, a,b)
    
#    test_logitnorm()
    
#    m = 0.5
#    r = 0.7
#    a1 = m*(1/r -1)
#    a2 = (1-m)*(1/r -1)
#    print a1,a2
#    n  = 1000
#    x1 = np.random.rand(n)
#    x2 = -5*x1 + np.random.rand(n)
#    x3 = np.random.rand(n)
#    x4 = np.random.rand(n)
#    x = np.array([x1,x2,x3,x4]).transpose()
#    x_sum = np.array([x.sum(axis = 1)]).transpose()
#    y = x/x_sum
#    pcor(y)
#    c = np.corrcoef(y.transpose())
#    print c
#    print c.sum()
#    print np.corrcoef(x.transpose())

    
    
    