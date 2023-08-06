'''
Created on Jun 14, 2010

@author: jonathanfriedman
'''
import numpy as np
from survey2.util.R_utilities import c_means

class Information():
    ''' Class of information theory methods'''
    
    def __init__(self,obs =None,alphabet = None,obs_cond = None, pmf_method = 'shrink', shared_alph = False):
        '''
        obs      = [list of np array] list of observation vectors. All vectors must be same length.
        obs_cond = [list of np array] list of observation vectors to be conditioned on. All vectors must be same length.  
        alphabet = [list of np array / list] alphabet over which pmf is estimated.
        method   = [string] estimation method. Valid methods are:
                        ML     - maximum likelihood estimate (simple counting). Works when n >> p (many observations over small alphabet).
                        shrink - Method proposed by Hausser & Strimmer (2009).  Works for  p << n (few observations over large alphabet).
        '''
        self.obs         = obs
        self.obs_cond    = obs_cond
        self.pmf_method  = pmf_method
        self.alphabet    = alphabet
        self.shared_alph = shared_alph
    
    def __repr__(self): return repr(self.data)
    
        
    def _parse_input(self,obs = [0], alphabet = None, method = None, shared_alph = None):
        ## IO parse
        if alphabet    is None: alphabet    = self.alphabet
        if shared_alph is None: shared_alph = self.shared_alph
        if method      is None: method      = self.pmf_method
        
        if type(obs[0]) is int: x = map(lambda i: self.obs[i], obs )
        else:                   x = obs
        if shared_alph: 
            aleph    = map(lambda i: alphabet[0], range(len(x)) )
            alphabet = aleph
            
#        # Check that all elements of x are in alphabet
#        for xi, alphi in zip(x, alphabet):
#            if not set(xi).issubset(set(alphi)): raise IOError('All elements of x must be in Alphabet')
        
        # Check that estimation method is in list of valid methods
        methods = ['shrink', 'ML', 'cmeans_ML','cmeans_shrink']
        if method not in methods: raise IOError('%s is not valid method' %method)
        return x, alphabet, method, shared_alph
    
        
    def estimate_pmf(self,obs = [0],alphabet = None, method = None, shared_alph = None, k = None, r = None):
        '''
        Estimate pmf over alphabet from observations x.  
        Only for discrete distributions. Continues values must be discretized before estimation!
        Inputs:
            obs            = [int]      index of self.x list to be used as observations. Or,  
                           = [np array] observation vector. All elements must be included in alphabet. 
            k              = [int] number of clusters for fuzzy c-means clustering (method is cmeans_shrink or cmeans_ML).   
            r              = [int] fuzziness coefficient for fuzzy c-means clustering.
        Outputs:
            pmf      = [np array] estimated pmf over alphabet (in corresponding order).
        '''
        ## IO parse
        x, alphabet, method, shared_alph = self._parse_input(obs, alphabet, method, shared_alph)
        
        ## Set up
        q   = len(x)                                         # number of observation series
        n   = float(len(x[0]))                               # number of observations
        if method == 'cmeans_ML' or method =='cmeans_shrink': # if using fuzzy clustering set alphabet to be 0:k
            alphabet = map(lambda i: np.arange(k), range(q))
        p    = np.array( map(lambda elt:len(elt), alphabet) ) # alphabet size
        pmf  = np.zeros(p, float)                             # init pmf
        
        ## Compute pmf
        if method == 'ML':
            for i in range(int(n)):
                alpha_ind = [list(np.where(alphabet[j] == x[j][i])[0]) for j in range(q)]
                pmf[tuple(alpha_ind)] += 1
            pmf = pmf/n
        elif method == 'cmeans_ML':
            from itertools import product
            from c_means_clustering import c_means
            # do fuzzy c-means clustering and get membership matrix for each dimension
            membership = map(lambda series: c_means(series,k,r), x)
            #update pmf counts for each observation
            for i in range(int(n)): # for each time point
                for states in product(range(k), repeat = q): # for each combination of clusters 
                    membership_temp = map(lambda j: membership[j][i,states[j]], range(q))
                    pmf[states] += np.product( membership_temp )
            pmf = pmf/n
        elif method == 'shrink' or method == 'cmeans_shrink':
            if method =='shrink' : method_temp = 'ML'
            else:                  method_temp = 'cmeans_ML'
            tk        = 1.0/p.prod()
            pmf_ML    = self.estimate_pmf(x,alphabet, method = method_temp, shared_alph = shared_alph, k=k, r=r)
            var_ML    = pmf_ML * (1 - pmf_ML)/(n-1)
            reg_const = var_ML.sum() / ( (tk - pmf_ML)**2 ).sum()
            if  reg_const > 1: reg_const = 1
            pmf       = reg_const * tk  +  (1 - reg_const) * pmf_ML
            
        return pmf
    
    
    def MI(self,obs = [0],alphabet = None, method = None, shared_alph = None, k = None, r = None):
        '''
        Calculate MI for all pairs of observations
        '''
        ## IO parse
        x, alphabet, method, shared_alph = self._parse_input(obs, alphabet, method, shared_alph)        
        
        ## set up
        q      = len(x)                                         # number of observation series
        n      = float(len(x[0]))                               # number of observations
        if method == 'cmeans_ML' or method =='cmeans_shrink': # if using fuzzy clustering set alphabet to be 0:k
            alphabet = map(lambda i: np.arange(k), range(q))
        p      = np.array( map(lambda elt:len(elt), alphabet) ) # alphabet size
        MI_mat = np.zeros((q,q)) # init MI matrix
        VI_mat = np.zeros((q,q)) # init variation of information matrix
        CC_mat = np.zeros((q,q)) # init coef of constraint matrix                  
        
        ## Calculate MI between all pairs
        for i in range(q):
            for j in range(i,q):
                pmf   = self.estimate_pmf([x[i],x[j] ], [alphabet[i], alphabet[j] ], method, shared_alph, k=k, r=r) # joint distribution
                pmf[np.where(pmf <=0)] = 1e-10
                
                pmf_x = pmf.sum(axis = 1) # marginal pmf, summing columns
                pmf_y = pmf.sum(axis = 0) # marginal pmf, summing rows
                pmf_x_mesh = np.tile(pmf_x, (len(alphabet[j]),1)).transpose()
                pmf_y_mesh = np.tile(pmf_y, (len(alphabet[i]),1))
                
                ## mutual info
                MI_temp     = ( pmf * np.log( pmf/pmf_x_mesh/pmf_y_mesh ) ).sum()
                MI_mat[i,j] = MI_temp
                MI_mat[j,i] = MI_temp
                
                ## coef of constraint
                H_x  = -(pmf_x * np.log(pmf_x)).sum() # entropy of x
                H_y  = -(pmf_y * np.log(pmf_y)).sum() # entropy of y
                C_xy = MI_temp/H_y 
                C_yx = MI_temp/H_x
                CC_mat[i,j] = C_yx # how much y constrains x
                CC_mat[j,i] = C_xy # how much x constrains y
                
                ## variation of info
                H_xy = -(pmf * np.log(pmf)).sum() # joint entropy of x & y
                VI_temp     = (H_xy - MI_temp)/H_xy
                VI_mat[i,j] = VI_temp
                VI_mat[j,i] = VI_temp
                
        return MI_mat, VI_mat, CC_mat
    
    
    def transfer_entropy(self,obs = [0],alphabet = None, method = None, shared_alph = None, k = None, r = None):
        '''
        Calculate transfer entropy for all pairs of observations
        '''
        ## IO parse
        x, alphabet, method, shared_alph = self._parse_input(obs, alphabet, method, shared_alph) 
        
        ## set up
        q      = len(x)                                         # number of observation series
        n      = float(len(x[0]))                               # number of observations
        if method == 'cmeans_ML' or method =='cmeans_shrink': # if using fuzzy clustering set alphabet to be 0:k
            alphabet = map(lambda i: np.arange(k), range(q))
        p      = np.array( map(lambda elt:len(elt), alphabet) ) # alphabet size
        TE_mat = np.zeros((q,q))                                # init TE matrix
        
        ## Calculate TE between all pairs
        for i in range(q):
            for j in range(q):
                pmf    = self.estimate_pmf([x[i][1:], x[i][:-1] ,x[j][:-1] ], [alphabet[i],alphabet[i], alphabet[j] ], method, shared_alph, k=k, r=r) # p(xt+1,xt,yt)         
                pmf_x  = self.estimate_pmf([x[i]], [alphabet[i]], method, shared_alph, k=k, r=r)                               # p(xt)
                pmf_xy = self.estimate_pmf([x[i],x[j] ], [alphabet[i], alphabet[j] ], method, shared_alph, k=k, r=r)           # p(xt,yt)
                pmf_xx = self.estimate_pmf([x[i][1:], x[i][:-1] ], [alphabet[i], alphabet[i] ], method, shared_alph, k=k, r=r) # p(xt+1,xt)
                pmf[np.where(pmf <=0)]       = 1e-20
                pmf_x[np.where(pmf_x <=0)]   = 1e-20
                pmf_xx[np.where(pmf_xx <=0)] = 1e-20
                pmf_xy[np.where(pmf_xy <=0)] = 1e-20
                
#                TE_temp = 0.0
#                for nxt1 in range(len(alphabet[i]) ):
#                    for nxt in range(len(alphabet[i]) ):
#                        for nyt in range(len(alphabet[j]) ):
#                            TE_temp += pmf[nxt1,nxt,nyt] * np.log( pmf[nxt1,nxt,nyt]  * pmf_x[nxt] / pmf_xx[nxt1,nxt] / pmf_xy[nxt,nyt] )
                                
                pmf_x_mesh_temp  = np.tile(pmf_x, (len(alphabet[j]),1)).transpose()
                pmf_x_mesh       = np.array(map(lambda i: pmf_x_mesh_temp, range(len(alphabet[i])) ))
                pmf_xx_mesh_temp = np.array(map(lambda i: pmf_xx, range(len(alphabet[j])) ))
                pmf_xx_mesh      = pmf_xx_mesh_temp.swapaxes(0,1).swapaxes(1,2)
                pmf_xx_mesh2      = pmf_xx_mesh_temp.swapaxes(1,2)
                pmf_xy_mesh      = np.array(map(lambda i: pmf_xy, range(len(alphabet[i])) ))                                
                TE_temp     = ( pmf * np.log( pmf * pmf_x_mesh / pmf_xx_mesh / pmf_xy_mesh ) ).sum()
                TE_mat[i,j] = TE_temp
        return TE_mat
    
    
    def pred_improve(self, x, R=1, m=1 ,h=1 ,dist_metric = 'e', prediction_metric = 'e'):
        '''
        Calculate the predictability improvements between all pairs of series in x.
        Inputs:
            x = [list of np arrays] time-series. must be same length
            R = [int] number of closest neighbors to use for prediction
            m = [int] embedding dimension (length of time-series segment to use for distance computation)
            h = [int] time lag (lag from value to be predicted)
            dist_metric = [str] distance metric. Same inputs as in 'distancematrix' function
        '''
        from predImprove import PI_matrix
        PI_mat = PI_matrix(x, R,m,h,dist_metric, prediction_metric)
        return PI_mat


def test():
    from TimeSeriesAnalysis import Generate_TS
    import matplotlib.pyplot as plt
    import warnings; warnings.filterwarnings('ignore')
                    
    n = 50
    c_vec = np.linspace(0,.99,10)
    
    MI_expected = 0.5 *((1+c_vec)*np.log(1+c_vec) + (1-c_vec)*np.log(1-c_vec))
    TE_expected = 0.5 * c_vec * ((1+c_vec)*np.log(1+c_vec) - (1-c_vec)*np.log(1-c_vec)) - 0.5 *(1+c_vec**2)*np.log(1+c_vec**2)
    
    alphabet1 = np.arange(2)
    alphabet2 = np.arange(2)
    alphabet  = [alphabet1, alphabet2]
    method    = 'cmeans_ML'
    shared_alph = True
    MI = np.array([])
    TExy = np.array([])
    TEyx = np.array([])
    PIxy = np.array([])
    PIyx = np.array([])
    k = 2
    r = 2
    for c in c_vec:
        x1,x2 = Generate_TS.TE_test_series(n,c) 
        x = [x1,x2]
        prob = Information(x,alphabet, pmf_method = method, shared_alph = shared_alph)
        MI   = np.append(MI, prob.MI(x, k=k, r=r)[0][0,1])
        TE    = prob.transfer_entropy(x, k=k, r=r)
        TExy  = np.append(TExy, TE[1,0])
        TEyx  = np.append(TEyx, TE[0,1])
        PI    = prob.pred_improve(x)
        PIxy  = np.append(PIxy, PI[1,0])
        PIyx  = np.append(PIyx, PI[0,1])

        
    fig = plt.figure()
    ax  = fig.add_subplot(111)
    h = ax.plot(c_vec,MI_expected,c_vec,MI)
    legend_s = ['MI_theory','MI_sim']
    fig.legend(h,legend_s)
#    plt.show()
    
    fig = plt.figure()
    ax  = fig.add_subplot(111)
    h = ax.plot(c_vec,TE_expected,c_vec,TExy,c_vec,TEyx)
    legend_s = ['TE_theory','TExy_sim', 'TEyx_sim']
    fig.legend(h,legend_s)
    
    fig = plt.figure()
    ax  = fig.add_subplot(111)
    h = ax.plot(c_vec,PIxy,c_vec,PIyx)
    legend_s = ['PIxy_sim', 'PIyx_sim']
    fig.legend(h,legend_s)
    plt.show()    
    

if __name__ == '__main__':   
    import matplotlib.pyplot as plt
    x1 = np.array([1,1,0,0,0,0,1])
    x2 = np.array([1,0,1,0,1,1,1])
    info   = Information()
    print info.MI([x1,x2], method = 'ML', alphabet = [[0,1]], shared_alph = True)

    
#    ## Compare to R entropy library
#    import rpy2.robjects as ro
#    from rpy2.robjects.packages import importr
#    import rpy2.robjects.numpy2ri
#    
#    rent = importr('entropy')
#    r = ro.r
#    
#    print rent.mi_shrink(counts_ML)
#    
    
