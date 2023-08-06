'''
Created on Jun 11, 2010

@author: jonathanfriedman
'''

from Bio.Cluster import distancematrix
import numpy as np

def PI_matrix(x,R=1, m=1 ,h=1 ,dist_metric = 'e', prediction_metric = 'e', section_starts = []):
    '''
    Calculate the predictability improvements between all pairs of series in x.
    x = [list of np arrays]
    '''
    if prediction_metric is None: prediction_metric = dist_metric
    
    n = len(x)
    PI_mat = np.zeros((n,n))
    for i in range(n):
        print 'series %d out of %d' %(i,n)
        for j in range(n):
            if i == j: continue
            x1 = x[i]
            x2 = x[j]
            PI,MSE_x,MSE_xy = predictability_improvment(x1,x2,R,m,h,dist_metric, prediction_metric, section_starts = section_starts)
            PI_mat[i,j] = PI
    return PI_mat
    

def predictability_improvment(x,y,R,m,h,dist_metric = 'e', prediction_metric = None, section_starts =[]):
    '''
    Inputs:
        x,y = [np array] time-series. must be same length
        R = [int] number of closest neighbors to use for prediction
        m = [int] embedding dimension (length of time-series segment to use for distance computation)
        h = [int] time lag (lag from value to be predicted)
        dist_metric = [str] distance metric. Same inputs as in 'distancematrix' function
    '''
    if prediction_metric is None: prediction_metric = dist_metric
    
    N = len(x) - m - h      # number of segments to compare
    error_x  = np.zeros(N)  # prediction error based on x series alone
    error_xy = np.zeros(N)  # prediction error based on both x & y series
    for seg_ind in range(N):
        seg_start = seg_ind
        seg_end   = seg_ind + m
        
        ## skip segments that span observations from two experiments
        if len(section_starts) > 1:
            big = np.where(section_starts > seg_start)
            if len(np.where(section_starts[big] < seg_end + h)[0]): continue
        
        dist_close_x,ind_close_x = get_close_segments(x, seg_ind, R, m, h, y = None, dist_metric = dist_metric, section_starts = section_starts)
        error_x[seg_ind] = prediction_error(x, R, m, h, seg_ind, ind_close_x, metric = prediction_metric)
        
        dist_close_xy,ind_close_xy = get_close_segments(x, seg_ind, R, m, h, y = y, dist_metric = dist_metric, section_starts = section_starts)
        error_xy[seg_ind] = prediction_error(x, R, m, h, seg_ind, ind_close_xy, metric = prediction_metric)
        
    MSE_x  = (error_x**2).mean()
    MSE_xy = (error_xy**2).mean()
    PI     = (MSE_x - MSE_xy)/(MSE_x + MSE_xy)
    return PI,MSE_x,MSE_xy
 
 
    
def get_close_segments(x,seg_ind,R,m,h,y=None, dist_metric = 'e', section_starts = []):
    '''
    Inputs:
    x,y = [np array] time-series. must be same value
    R = [int] number of closest neighbors to use for prediction
    m = [int] embedding dimension (length of time-series segment to use for distance computation)
    h = [int] time lag (lag from value to be predicted)
    dist_metric = [str] distance metric. Same inputs as in 'distancematrix' function
    '''    
    ## get base segment
    base_segment = x[seg_ind:seg_ind+m]  # base segment to compute distances to
    if y is not None: base_segment_y = y[seg_ind:seg_ind+m]
    ## Find closest segments in x
    dist_close    = 10**5 * np.ones(R)      # closest distances 
    ind_close     = np.zeros(R)             # index of closest segments (start position) 
    max_dist      = dist_close.max()        # maximal distance to close segments
    max_ind       = dist_close.argmax()     # index of most distant segment id close segments
    N             = len(x) - m - h          # number of segments to compare
    for i in range(N):
        if i == seg_ind: continue           # skip the base segment
        seg_start = i
        seg_end   = i+m
        
        ## skip segments that span observations from two experiments
        if len(section_starts) > 1:
            big = np.where(section_starts > seg_start)
            if len(np.where(section_starts[big] < seg_end + h)[0]): continue
        
        segment = x[seg_start:seg_end]
        dist =  distancematrix(np.array([base_segment,segment]),dist= dist_metric)[1]
        if y is not None:                   # if y series is also given, distance is average of x distance and y distance
           segment_y = y[i:i+m]
           dist_y =  distancematrix(np.array([base_segment_y,segment_y]),dist= dist_metric)[1]
           dist   =  np.mean([dist,dist_y])
        if dist < max_dist:  # if found segment that's closer than the most distance on the close list, replace with closer segment
            dist_close[max_ind] = dist 
            ind_close[max_ind]  = i
            max_dist            = dist_close.max()
            max_ind             = dist_close.argmax()
    return dist_close,ind_close

        
def prediction_error(x,R,m,h,seg_ind,close_ind,metric):
    '''
    Calculate prediction error given base segment and closest segments
    '''
    ## get base segment
    base_segment = x[seg_ind:seg_ind+m]  # base segment to compute distances to
    if metric =='e':
        true_prediction = x[seg_ind+h]          # The value to be predicted by close-by segments
    elif metric =='s':
#        print base_segment
#        print x[seg_ind+m+h]
#        print np.append( base_segment,x[seg_ind+m+h] )
        true_prediction = np.append( base_segment,x[seg_ind+m+h] ).argsort()[-1]
    
    predictions = np.zeros(R) 
    for j,ind in enumerate(close_ind):
        if metric =='e':
            predictions[j] = x[ind+h]
        elif metric =='s':
            segment       = x[ind:ind+m]
            predictions[j] = np.append( segment,x[ind+m+h] ).argsort()[-1]  
    
    error = true_prediction - predictions.mean()
    return error

         
#dist_metric = 'e'
#prediction_metric = 'e'
#                
##x = np.array(range(100))
#x = np.random.normal(0,1,100) 
##y = np.random.randint(0,99,100)
#y = np.append(x[1:],0)
#R = 10
#m = 1
#h = 1
#mse_x,mse_xy = predictability_improvment(x,y,R,m,h,dist_metric, prediction_metric)  
#print mse_x,mse_xy         
#
#print predictability_improvment(y,x,R,m,h,dist_metric, prediction_metric)     