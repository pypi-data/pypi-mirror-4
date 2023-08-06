'''
Created on Jun 14, 2010

@author: jonathanfriedman
'''

import cPickle as pickle
import matplotlib.pyplot as plt
import networkx as nx
import scipy.stats as stats
import numpy as np

from copy import deepcopy
from networkx import Graph, DiGraph
from pandas import DataFrame as DF

def make_network(frame, cutoff=None, **kwargs):
    ## check that row and column labels are identical
    err_msg = 'Frame must have the same labels for rows and columns'
    np.testing.assert_array_equal(frame.index, frame.columns, err_msg)
    ## check if square matrix
    err_msg = 'Frame must be symmetric'
    np.testing.assert_array_equal(frame, frame.T, err_msg)

    G = Graph()
    G.add_nodes_from(frame.index)
    if cutoff is not None:
        add_edges(G, frame, cutoff, **kwargs)
    return G

def add_edges(G, frame, cutoff, method='larger', abs_val=True, nodes=None):
    '''
    Add edges to network using specified method.

    method [str]: method used to obtain statistic
    '''
    from itertools import combinations, product
    ## check that row and column labels are identical
    ## check if square matrix
    ids = G.nodes_iter()
    
    # if node is given iterate only over pairs containing that node
    if nodes is not None:
        if not hasattr(nodes, '__iter__'):
            nodes = (nodes,) 
        pairs = product(ids, nodes)
    else:
        pairs = combinations(ids,2)
                   
    ## go over all pairs
    method = method.strip().lower()
    if method not in ('larger', 'smaller'):
        raise ValueError, 'Unsupported method "%s"' %method
    for pair in pairs:
        p1,p2  = pair
        weight = frame[p1][p2]
        sign   = np.sign(weight)
        if abs_val:
            stat = np.abs(weight)
        else:
            stat = weight
        add = False
        if method=='larger' and stat >= cutoff:
            add = True
        elif method=='smaller' and stat <= cutoff:
            add = True
        if add:
            G.add_edge(p1, p2, weight=weight, sign=sign)
                
#def make_network(abunds, algo, **kwargs):
#    '''
#    Make network object from abundance time-series.
#    Inputs:
#        abunds = [MultiAbundanceTS] object with all OTU abundance time-series.
#        algo   = [str] algorithm to compute interaction support. 
#                 Valid inputs: 
#                     Tau  = kendall tau correlation coefficient
#                     MI   = Mutual information
#                     TE   = transfer entropy
#                     PI   = predictability improvement
#                     SVAR = sparse vector autoregression
#    '''
#    if algo  == 'Tau':
#        norm_tot     = kwargs.get('norm_tot', False)
#        noisy_counts = kwargs.get('noisy_counts', False)
#        lag          = kwargs.get('lag', 0)
#        tau, pval = abunds.kendall(lag = lag, norm_tot = norm_tot, noisy_counts = noisy_counts)
#        tau_mat   = PairMatrix(tau,  abunds.keys())
#        pval_mat  = PairMatrix(pval, abunds.keys())
#        if lag: net = OTUnetworkDi(abunds = abunds, matrix = tau_mat, p_vals = {'direct':pval_mat}, algo = algo, lag = lag)
#        else:   net = OTUnetwork(  abunds = abunds, matrix = tau_mat, p_vals = {'direct':pval_mat}, algo = algo, lag = 0)
#    
#    elif algo == 'PI':
#        R      = kwargs.get('R', 2)
#        PI     = abunds.pred_imporve(R = R)
#        PI_mat = PairMatrix(PI,  abunds.keys())
#        net    = OTUnetworkDi(abunds = abunds, matrix = PI_mat, algo = algo)
#    
#    elif algo == 'SVAR':
#        LV  = kwargs.get('LV', False)
#        ids, b, b0, cv_errors = abunds.SVAR_all(1, LV = LV)
#        b_mat = PairMatrix(b, ids)
#        net   = OTUnetworkDi(abunds = abunds, matrix = b_mat, algo = algo)
#        
#    elif algo == 'MI':
#        method = kwargs.get('method', 'cmeans_ML')
#        k      = kwargs.get('k', 3)
#        r      = kwargs.get('r', 2) 
#        MI      = abunds.MI(method = method, k=k, r =r)
#        MI_mat  = PairMatrix(MI,  abunds.keys())
#        net = OTUnetwork(abunds = abunds, matrix = MI_mat, algo = algo)
#    
#    elif algo == 'TE':
#        method = kwargs.get('method', 'cmeans_ML')
#        k      = kwargs.get('k', 3)
#        r      = kwargs.get('r', 2)  
#        TE      = abunds.transfer_entropy(k=k, method = method)
#        TE_mat  = PairMatrix(TE,  abunds.keys())
#        net = OTUnetwork(abunds = abunds, matrix = TE_mat, algo = algo)
#    return net
        

def remove_edges(G):
    '''
    Remove all edges from graph
    '''
    G.remove_edges_from(G.edges())
    pass

def remove_disc_nodes(G):
    '''
    Remove all nodes that have no edges.
    Return new instance.
    '''
    from copy import deepcopy
    G_reduced = G.copy()
    degree    = G.degree()
    nodes     = degree.keys()
    remove    = filter(lambda node: degree[node]==0, nodes)
    G_reduced.remove_nodes_from(remove)
    return G_reduced

def community_detection(G, **kwargs):
    '''
    Do community detection on network.
    Return list of lists representing the nodes in each community.
    
    Online doc: http://igraph.sourceforge.net/doc/python/index.html
    '''
    import igraph
    algo  = kwargs.get('algo','modularity') # algorithm to be used for community detection
    ## convert to iGraph
    file = 'temp.gml'
    nx.write_gml(G,file)
    iG = igraph.read(file)
    ## detect community
    if algo is 'modularity': comm = iG.community_fastgreedy(weights = 'weight')
    elif algo is 'walk': 
        steps  = kwargs.get('steps',4)
        comm = iG.community_walktrap(weights = 'weight', steps = steps)
#    elif algo is 'spinglass': 
#        gamma  = kwargs.get('gamma',1)
#        comm = iG.community_spinglass(weights = 'weight', gamma = gamma)
    m  = np.array(comm.membership)
    ## convert membership to list of lists, and make membership dict
    partitions   = []
    membership_d = {}
    for i in range(m.max()+1):
        members = np.where(m ==i)[0]
        member_ids = map(lambda j: iG.vs[int(j)].attributes()['label']  ,members)
        partitions.append(member_ids)
        for id in member_ids: membership_d[id] = i
    return partitions, membership_d
    
def component_net(G, components, **kwargs):
    '''
    Make a new network where each node represents all nodes of G in a given component.
    Interaction matrix is the average interaction between all pairs in components.  
    '''
    from itertools import combinations, product
    
    linkage   = kwargs.get('linkage','avg')
    statistic = kwargs.get('statistic','matrix')
    method    = kwargs.get('method','abs_larger')
    
    if   statistic == 'p_vals': stat_mat = G.p_vals[method]
    elif statistic == 'q_vals': stat_mat = G.q_vals[method] 
    elif statistic == 'matrix': stat_mat = G.matrix 
    
    n = len(components)
    ## make component interactions
    mat = np.zeros((n,n))
    for pair in combinations(range(n),2):
        c1, c2 = pair
        nodes1 = components[c1]
        nodes2 = components[c2]
        vals   = np.array( map( lambda p: stat_mat[p[0]][p[1]], product(nodes1,nodes2) ) )
        if linkage is 'avg': c_inter = vals.mean()
        elif linkage is 'max': 
            abs_v   = np.abs( vals )
            c_inter = vals[abs_v.argmax()]
        mat[c1,c2] = c_inter
        mat[c2,c1] = mat[c1,c2]
    ## get within component interactions
    for c,nodes in enumerate(components):
         vals   = np.array( map( lambda p: stat_mat[p[0]][p[1]], combinations(nodes,2) ) )
         if linkage is 'avg': c_inter = vals.mean()
         elif linkage is 'max': 
            abs_v   = np.abs( vals )
            c_inter = vals[abs_v.argmax()]
         mat[c,c] = c_inter
    mat_md = MatrixDictionary()
    labels = map(lambda i: 'comp_' + str(i), range(n))
    mat_md.from_matrix(mat, labels, labels) 
    comp_net = OTUnetwork(node_ids = mat_md.row_labels(), matrix = mat_md, algo = G.algo)
    return comp_net



def compute_pvals(G, method='local_p', approx_norm=True, two_tailed=True):
    '''
    Compute p-values using specified method.
    method [str]:
        local_p     : calculate p-value from raw and column, assuming values are normally distributed. 
                      The test statistic -[log(p_row) - log(p_col)] has an Erlang distribution with shape (k) = 2, and scale (theta) = 1. 
        global_p    : calculate from all matrix, assuming values are normally distributed
    approx_norm [bool]: approximate distribution of similarity matrix elements as normal.
    '''
    matrix = G.matrix.matrix
    ids    = G.matrix.ids
    n      = matrix.shape[0] # num ts in network
    
    p_vals_mat = np.zeros((n,n))
    # calculate mean and std of all rows and cols
    if method == 'local_p':
        row_mean = np.zeros(n)
        row_std  = np.zeros(n)
        col_mean = np.zeros(n)
        col_std  = np.zeros(n)
        for i in range(n): 
            row = np.delete(matrix[i,:], i) 
            col = np.delete(matrix[:,i], i)    
            row_mean[i] = row.mean()
            row_std[i]  = row.std()
            col_mean[i] = col.mean()
            col_std[i]  = col.std()
            
    # calculate empirical distribution of all matrix, excluding the diagonal values 
    if method == 'global_p':
        vals = G.matrix.flatten()
        if approx_norm:
            global_mean = vals.mean()
            global_std  = vals.std()
        else: kde_pdf     = stats.gaussian_kde(vals)
        
    ## go over all pairs
    for i in range(n):
        for j in range(0,n):
            if i ==3 and j==37:
                pass
            if i == j:
                p_vals_mat[i,j]  = 1 
                continue

            if method == 'local_p':
                if approx_norm:
                    row = np.delete(matrix[i,:], np.where(matrix[i,:] == 1.5) )
                    col = np.delete(matrix[:,j], np.where(matrix[:,j] == 1.5) )
                    if len(row) < 2 or len(col) < 2: 
                        p_vals_mat[i,j] = 1.5
                        continue
                    p_row = stats.norm(row_mean[i], row_std[i]).sf(matrix[i,j])
                    p_col = stats.norm(col_mean[j], col_std[j]).sf(matrix[i,j])
                else:
                    kde_pdf_row = stats.gaussian_kde(row)
                    kde_pdf_col = stats.gaussian_kde(col)
                    p_row       = 1 - kde_pdf_row.integrate_box_1d(-1, matrix[i,j])
                    p_col       = 1 - kde_pdf_col.integrate_box_1d(-1, matrix[i,j])
                    if matrix[i,j] < 0:  # check for extreme negative values (for dissimilarity matrices with negative values)
                        p_row = 1 - p_row
                        p_col = 1 - p_col
                if not min(p_row,p_col): statistic = - np.log(p_row) - np.log(p_col)
                else:                    statistic = - np.log(p_row) - np.log(p_col)
                p_vals_mat[i,j] = stats.gamma(2).sf(statistic)
            
            elif method == 'global_p':
                if approx_norm: 
                    p = stats.norm(global_mean, global_std).sf(matrix[i,j])
                    if matrix[i,j] < 0: p = 1 - p # check for extreme negative values (for dissimilarity matrices with negative values)
                    if two_tailed:      p = 2*p
                else: 
                    if matrix[i,j] < 0:  p = kde_pdf.integrate_box_1d(-100, matrix[i,j])
                    else:                p = kde_pdf.integrate_box_1d(matrix[i,j], 100)
                p_vals_mat[i,j] = p
    p_vals_mat[p_vals_mat>1] = 1.0            
    p_vals = PairMatrix(p_vals_mat, ids)
    G.p_vals[method] = p_vals
    return p_vals
        
def compute_qvals(G, method='direct'):
    '''
    Compute q-values corresponding to p-values obtained using specified 'method'.
    '''
    from survey2.util.R_utilities import R_qvalues
    p_vals = G.p_vals[method]
    n      = p_vals.matrix.shape[0]
    
    p_vals_flat = p_vals.flatten()    
    q_vals_flat = R_qvalues(p_vals_flat)
    q_vals_mat  = p_vals.unflatten(q_vals_flat)
    q_vals      = DF(q_vals_mat, p_vals.ids, p_vals.ids) 
    G.q_vals[method] = q_vals
    return q_vals


def add_component_membership(net, membership):
    '''
    Add membership attribute to each node.
    '''
    for node in net.nodes_iter(): net.node[node]['component'] = membership[node]
    
def add_labels(net):
    '''
    Add node labels with shortened lineages
    '''
    for node in net.nodes_iter(): 
        net.node[node]['label'] = node.split('_')[1] + '_' + lineage_short(net.node[node]['lineage'])

def overlap(net1,net2):
    '''
    Return the overlap between two networks.
    '''
    edges1 = net1.edges()
    edges2 = net2.edges()
    shared = filter(lambda e: e in edges2, edges1) # all shared edges
    agree  = filter(lambda e: net1[e[0]][e[1]]['sign'] == net2[e[0]][e[1]]['sign'], shared) # same sign edges
    print filter(lambda e: e not in edges2, edges1) # all shared edges
    n1       = len(edges1)
    n2       = len(edges2)
    n_shared = len(shared)
    n_agree  = len(agree)
    return n1,n2,n_shared,n_agree

def confusion_mat(net1,net2, sign=True, matched=True, **kwargs):
    '''
    Return the confusion matrix between two networks.
    If matched, networks must have the same set of nodes. 
    Otherwise missing nodes are added with no connections.
    Categories are +,0,- , rows are categories in net1, cols are in net2.
    '''
    from DataStructures.MyDataMatrix import MyDataMatrix as DM
    from itertools import combinations
    nodes1  = net1.nodes()
    nodes2  = net2.nodes()
    s1 = set(nodes1)
    s2 = set(nodes2)
    nodes_all = s1.union(s2)
    if not matched:
        net1.add_nodes_from(nodes_all)
        net2.add_nodes_from(nodes_all)
    else:
        if s1 != s2: 
            raise ValueError('Networks must have exactly the same set of nodes')
    
    edges1 = net1.edges()
    edges2 = net2.edges()   
    if sign: 
        categories = ['P+','N','P-']
    else:    
        categories = ['P','N']
    k = len(categories)
    confuse = DM(np.zeros( (k,k) ), index=categories, columns=categories)
    for pair in combinations(nodes_all,2):
        n1,n2 = pair
        if net1.has_edge(*pair):
            if sign: 
                if net1[n1][n2]['sign'] > 0: row = 'P+'
                else:                        row = 'P-'
            else:
                row = 'P'     
        else:                            row = 'N'
        if net2.has_edge(*pair):
            if sign:
                if net2[n1][n2]['sign'] > 0: col = 'P+'
                else:                        col = 'P-'
            else:
                col = 'P'  
        else:                            col = 'N'
        confuse[col][row] += 1
    
#    score_mat = kwargs.get('score_mat', np.array([ [0.0,1,1],[1,0,1],[1,1,0] ]))
#    score     = np.sum( score_mat * confuse.values )
    return confuse


def distance(net1,net2):
    '''
    Return the distance between two matched nets ( i.e., networks that have the same set of nodes).
    Distance is the average euclidean distance between the edge weights.
    '''
    nodes1 = net1.nodes()
    nodes2 = net2.nodes()
    if set(nodes1) != set(nodes2): raise ValueError('Networks must have exactly the same set of nodes')
    adj1 = nx.to_numpy_matrix(net1, nodes1, dtype = float) # adjacency matrix of network 1
    adj2 = nx.to_numpy_matrix(net2, nodes1, dtype = float) # adjacency matrix of network 2 with same order as of net1
    k    = len(nodes1)
    dist = np.sum( np.abs(adj1-adj2) )
    dist /= k*(k-1)
    return dist
    

def add_cluster_edges(G, num_clusters, dist = 'e' ):
    '''
    Add edges between all nodes belonging to the same cluster.
    '''
    from itertools import combinations
    abunds = G.abunds
    for clust in range(num_clusters):
        clust_abunds = abunds.filter_by_cluster([clust], dist)
        ids          = clust_abunds.keys()
        for pair in combinations(ids,2): G.add_edge(pair[0], pair[1], weight= 1 )           


def lineage_short(lineage, style='HMP', depth_max=1):
    '''
    Return a str of the most resolved taxonomic unit of lineage.
    '''
    fields = lineage.split(';')
    lin    = ''
    depth  = 0
    if style is 'HMP':
        for tax in fields[-2::-1]:
            try: float(tax)
            except:
                if not tax.startswith('unclassified'):
#                    tax.split('(')[0]
                    lin    = tax + ';' + lin
                    depth += 1
            if depth == depth_max:
                return lin
    elif style is 'Knight':
        assigned = filter(lambda field: field[-1] != '_' ,fields)
        return assigned[-1][3:]
    return lin #if didn't reach maximal depth
        

def plot_network(net, **kwargs):
    '''
    '''
    if 'ax' in kwargs:
        ax = kwargs['ax']
    else:
        plt.figure(facecolor='w', edgecolor='k')
        ax = plt.gca()
    
    G = deepcopy(net)
    
    ## input params
    show       = kwargs.get('show',True)
    lable_flag = kwargs.get('lable_flag',True)
    show_lin   = kwargs.get('show_lin',False)
    node_size  = kwargs.get('node_size',100)
    edge_width = kwargs.get('edge_width', 2)
    node_shape = kwargs.get('node_shape','o')
    color_by   = kwargs.get('color_by','given')
    node_cmap  = kwargs.get('node_cmap','Paired')
    node_vmax  = kwargs.get('node_vmax', 1.)
    node_vmin  = kwargs.get('node_vmin', 0.)
    node_alpha = kwargs.get('node_alpha', .9)
    file       = kwargs.get('file',None)
    remove_disconnected = kwargs.get('remove_disconnected',False)
    
    ## remove disconnected nodes
    if remove_disconnected: G = remove_disc_nodes(G)
    
    ## set node sizes
    if 'node_sizes' in kwargs:
        d         = kwargs['node_sizes']
        node_size = [d[node] for node in G.nodes()]
        if kwargs.get('scale_sizes', True):
            max_node_size = kwargs.get('max_node_size', 500)
            node_size = max_node_size/(1-np.log2(node_size))   
    
#    ## create net with only positive weights
#    G_pos = deepcopy(G)
#    for (u,v,d) in G_pos.edges(data=True):
#        if d['weight'] < 0: d['weight'] = -d['weight']
        
    ## node layout
    if 'pos' in kwargs: # user inputed node position 
        pos = kwargs['pos']
    else: 
        layout = kwargs.get('layout','graphviz') # type of graph layout to use. ('graphviz' | 'spring')
        prog   = kwargs.get('prog','fdp')          # layout program to be used if layout is graphviz. ('neato' | 'fdp' |...)
        iter   = kwargs.get('iter',30)             # number of iteations to use if layout is spring
        if layout is 'spring':
            pos  = kwargs.get('pos',nx.spring_layout(G.to_undirected(),iterations = iter))
        elif layout is 'graphviz':
#            pos = nx.pygraphviz_layout(G, prog = prog, args = '-Gmaxiter=5') # pass additional parameters to graphviz. G indicates that this is a Graph attributes. 
            pos = nx.pygraphviz_layout(G, prog = prog)
        elif layout is 'circular':
            pos = nx.drawing.layout.circular_layout(G)
    ## plot nodes
    if color_by == 'component':   
        C = nx.connected_component_subgraphs(G.to_undirected()) # color nodes the same in each connected subgraph
        for i,g in enumerate(C):
            c   = [np.random.random()]*nx.number_of_nodes(g) # random color...
            nodes = nx.draw_networkx_nodes(g,
                 pos,
                 node_size   = node_size,
                 node_shape  = node_shape,
                 node_color  = c,
                 cmap        = node_cmap,
                 vmin        = node_vmin,
                 vmax        = node_vmax,
                 with_labels = False,
                 alpha       = node_alpha,
                 ax          = ax,
                 linewidths  = 0
                 )
            plot_edges(g, pos, ax, edge_width)
            
    elif color_by in set(['degree','self_edge','given','community', 'phyla']): 
        if color_by is 'degree':   
            c = [float(G.degree(v)) for v in G] # color by degree dist.
        elif color_by is 'self_edge':
            c = [G.matrix[node][node] for node in G.nodes()] 
        elif color_by is 'given': 
            c = kwargs.get('node_color','LightSlateGray')
        elif color_by is 'community':
            m = kwargs['membership']
            m_max = np.max(m.values())
            c = []
            for id in G.nodes():
                if id in m: c.append(float(m[id])) 
                else:       c.append(float(m_max+1)) 
        elif color_by is 'phyla':
            c_dict = kwargs['node_color']
            c = [c_dict[node] for node in G.nodes() ]
        nodes = nx.draw_networkx_nodes(G,
             pos,
             node_size   = node_size,
             node_shape  = node_shape,
             node_color  = c,
             cmap        = node_cmap,
             vmin        = node_vmin,
             vmax        = node_vmax,
             with_labels = False,
             alpha       = node_alpha,
             ax          = ax,
             linewidths  = 0
             )
        plot_edges(G, pos, ax, edge_width)
    
     
    pos_vals = pos.values()
    x_pos =  map(lambda p: p[0], pos_vals)
    y_pos =  map(lambda p: p[1], pos_vals)
    xmax  = np.max(x_pos)
    xmin  = np.min(x_pos)
    ymax  = np.max(y_pos)
    ymin  = np.min(y_pos)
    xdiff = (xmax-xmin)
    ydiff = (ymax-ymin)
    if xdiff == 0: xdiff = 1
    if lable_flag:
        xfactor  = kwargs.get('xfactor',.03)
        yfactor  = kwargs.get('yfactor',.03)  
        xoffset  = kwargs.get('xoffset', xdiff*xfactor)
        yoffset  = kwargs.get('yoffset', ydiff*yfactor)
        plot_labels(G, pos, xoffset, yoffset, ax, show_lin = show_lin)
        
    ## set figure limits 
    plt.xlim(xmin = xmin - xdiff*.1, xmax = xmax + xdiff*.15 )
    plt.ylim(ymin = ymin - ydiff*.075, ymax = ymax + ydiff*.075 )    
#    plt.xlim(xmin = xmin - xdiff*.0, xmax = xmax + xdiff*.0 )
#    plt.ylim(ymin = ymin - ydiff*.00, ymax = ymax + ydiff*.00 )   
#    plt.axes().set_aspect('equal', 'datalim')      

    plt.axis('off')  # turn off figure axis
    set_axis = kwargs.get('set_axis','tight')
    plt.axis(set_axis)
#    plt.sci(nodes)
#    plt.colorbar() 
    if file: plt.savefig(file, bbox_inches = 'tight')
    if show: plt.show() 
    
    
def plot_edges(G, pos, ax, w):
    ## draw edges
    # get edges with positive and negative relations
#    e_pos=[(u,v) for (u,v,d) in G.edges(data=True) if 1-d['weight'] > 0]
#    e_neg=[(u,v) for (u,v,d) in G.edges(data=True) if 1-d['weight'] <=0]
    e_pos=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] > 0]
    e_neg=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] <=0]
    e_pos_colors = map(lambda e:1-G[e[0]][e[1]]['weight'] ,e_pos) 
    e_neg_colors = map(lambda e:1-G[e[0]][e[1]]['weight'] ,e_neg)
    e_pos_colors = 'g'
    e_neg_colors = 'r'
    
#    nx.draw_networkx_edges(G, pos, edgelist=e_pos, alpha = .7, width=2,edge_color = e_pos_colors, style='solid')
#    nx.draw_networkx_edges(G, pos, edgelist=e_neg, alpha = .7, width=2,edge_color = e_neg_colors, style='solid')
    cmap_pos = plt.cm.Greens
    cmap_neg = plt.cm.Reds
    edge_vmin_pos = 0
    edge_vmax_pos = 1
    edge_vmin_neg = edge_vmin_pos
    edge_vmax_neg = edge_vmax_pos
    a = 0.8
    style_def='solid'
    for e in e_pos:
#        c = 1-G[e[0]][e[1]]['weight']
        c = G[e[0]][e[1]]['weight']
        style = G[e[0]][e[1]].get('style', style_def) 
        nx.draw_networkx_edges(G, pos, edgelist=[e], alpha = a, width=w, edge_color = [c], style=style, 
                               edge_cmap = cmap_pos, edge_vmin= edge_vmin_pos, edge_vmax = edge_vmax_pos, ax = ax)
    for e in e_neg:
#        c = G[e[0]][e[1]]['weight']-1
        c = -G[e[0]][e[1]]['weight']
        style = G[e[0]][e[1]].get('style', style_def) 
        nx.draw_networkx_edges(G, pos, edgelist= [e], alpha = a, width=w,edge_color = [c], style=style,
                               edge_cmap = cmap_neg, edge_vmin= edge_vmin_neg, edge_vmax = edge_vmax_neg, ax = ax)


def plot_labels(G, pos, xoffset, yoffset, ax, show_lin = True):
    ## draw labels
    labels    = {}
    label_pos = {}
    for node, p in pos.items():
        if show_lin: labels[node] = node.split('_')[-1] + '_' + lineage_short(G.node[node]['lineage'])
        else:        
            try:    labels[node] = node.strip('\'').strip('\"')
            except: labels[node] = node
        label_pos[node] = np.array([p[0] + xoffset, p[1] + yoffset])
    nx.draw_networkx_labels(G, label_pos, labels = labels, font_size=8, font_weight='normal', ax = ax)
    



def plot_degree_dist(G, logx = False, logy = True):
    plt.figure()
    degree_sequence=sorted(nx.degree(G).values(),reverse=True) # degree sequence
    #print "Degree sequence", degree_sequence
    dmax=max(degree_sequence)
    
    if logx and logy: plt.loglog(degree_sequence,'b-',marker='o')
    elif logy:        plt.semilogy(degree_sequence,'b-',marker='o')
    elif logx:        plt.semilogx(degree_sequence,'b-',marker='o')
    else:             plt.plot(degree_sequence,'b-',marker='o')
    plt.title("Degree rank plot")
    plt.ylabel("degree")
    plt.xlabel("rank")



def interaction_vs_phylo_dist(G,num_bins = 10, n_pseudo=0, norm = False, plot = True, log = False, ms = 10, alpha = 0.7, file = None, show = False, filter = None):
    '''
    Get the number/probability of interaction as a function of phylogenetic distance.
    '''
    stat_inter, phylo_dist_inter = stat_vs_phlyo_dist(G,plot = False, ms = ms, alpha = alpha, file = None, show = False, filter = filter)
    stat_all, phylo_dist_all     = stat_vs_phlyo_dist(G,plot = False, ms = ms, alpha = alpha, file = None, show = False, filter = None)
    
    ## get interaction counts per distance
    if log: 
        phylo_dist_inter = np.log10(phylo_dist_inter)
        phylo_dist_all   = np.log10(phylo_dist_all)
    n_all, bins   = np.histogram(phylo_dist_all, bins = num_bins)
    n_inter, bins = np.histogram(phylo_dist_inter, bins = num_bins)
    bin_centers   = bins[:-1] + np.diff(bins)/2
    
    ## estimate probability of interaction from counts
    n_all_float = np.array(n_all, float)
    n_all_pseudo   = n_all_float + n_pseudo
    n_inter_pseudo = n_inter + n_pseudo 
    p_inter        = n_inter_pseudo/n_all_pseudo         
    
    ## plot
    if plot:
        fig = plt.figure()
        ax  = fig.add_subplot(111)
        if norm:
            h      = ax.plot(bin_centers,p_inter,'--o', lw = 2, ms = ms, alpha = alpha)
            ylabel = 'Probability of relation'  
        else:
            h1     = ax.plot(bin_centers,n_inter,'--o', lw = 2, ms = ms, alpha = alpha)
            h2     = ax.plot(bin_centers,n_all,  '--o', lw = 2, ms = ms, alpha = alpha)     
            ylabel = 'Number of Pairs'
            plt.legend([h1,h2],['Interacting', 'All']) 
        if log: plt.xlabel('log10 (Genetic dist)')
        else:   plt.xlabel('Genetic dist')       
        plt.ylabel(ylabel)
        
        if file: plt.savefig(file)
        if show: plt.show()
    return p_inter, bin_centers


def conditional_stat_dist(G, statistic = 'matrix', num_bins = 10, plot = True, log = False, file = None, show = False, sig_filter = None):
    stats_all, dist = stat_vs_phlyo_dist(G,statistic = statistic, plot = False, file = None, show = False, filter = sig_filter)
    
    ## get interaction counts per distance
    if log: dist = np.log10(dist)
    n, bins      = np.histogram(dist, bins = num_bins)
    bin_centers  = bins[:-1] + np.diff(bins)/2
    
    ## get stat as function of dist
    stats_cond = []
    num_points = len(dist)
    for i in range(len(bins)-1):
        min = bins[i] 
        max = bins[i+1]
        inds = filter(lambda z: min<=dist[z] and dist[z]<max, range(num_points))
        stats_cond.append(stats_all[inds])
        
    kde_2d(dist,stats_all)
    
    
#    ## estimate stat pdf as a function of dist
#    stat_pdfs  = []
#    point_list = []
#    kde = True
#    if kde:
#        points = np.linspace(-1,1,100)
#        for s in stats_cond:
#            kde_pdf = stats.gaussian_kde(s)
#            pdf     = kde_pdf.evaluate(points)
##            adjust = 1
##            points, pdf = kder(s, adjust)
#            stat_pdfs.append(pdf)
#            point_list.append(points)
#    else:
#        for s in stats_cond:
#            pdf, bins    = np.histogram(s, bins = 10, normed = True, range=(-1,1))
#            stat_pdfs.append(pdf)
#        points = bins[:-1] + np.diff(bins)/2
#    
#    ## plot
#    if plot:
#        fig = plt.figure()
#        ax  = fig.add_subplot(111)
#        h = []
#        for pdf,points in zip(stat_pdfs, point_list):
#            h_temp = ax.plot(points,pdf,'-', lw = 2)
#            h.append(h_temp) 
#        plt.xlabel('Tau')    
#        plt.ylabel('pdf')
#        plt.legend(h,map(lambda x: '%.2f' %x, bin_centers))
#        
#        if file: plt.savefig(file)
#        if show: plt.show()
#    return bin_centers, stat_pdfs
        
         
    
def stat_vs_phlyo_dist(G, dist_mat, plot = True, log = False, statistic = 'p_vals', method = 'direct', ms = 10, alpha = 0.7, file = None, show = False, filter = None):
    '''
    filter['stat'] = [str] statistic to filter by ('matrix' | 'matrix_abs' | 'p_vals' | 'q_vals')
    filter['min'] = [float] min stat
    filter['max'] = [float] max stat
    '''
    from itertools import combinations
    import scipy.stats as stats
    if   statistic == 'p_vals': stat_mat = G.p_vals[method]
    elif statistic == 'q_vals': stat_mat = G.q_vals[method]
    elif statistic == 'matrix': stat_mat = G.matrix
    ## get list of all id pairs
    ids      = stat_mat.ids   # otu ids
    pair_ids = []
    for pair in combinations(ids,2):
        pair_ids.append(pair)
    
    phylo_dist = dist_mat.vals_by_keys(pair_ids)   ## get phylogenetic distances
    stat       = stat_mat.vals_by_keys(pair_ids)   ## get corresponding stats
    
    ## Remove stat values outside range defined by stat_min & stat_max
    if filter is not None:
        filter_method = filter['method']
        if   filter['stat'] == 'p_vals': filter_mat = G.p_vals[filter_method]
        elif filter['stat'] == 'q_vals': filter_mat = G.q_vals[filter_method]
        elif filter['stat'] in set(['matrix', 'matrix_abs' ]): filter_mat = G.matrix
        
        filter_stat = filter_mat.vals_by_pair_ids(pair_ids)
        if filter['stat'] == 'matrix_abs': filter_stat = np.abs(filter_stat)
        
        del_inds = np.array([])
        if 'min' in filter: del_inds = np.r_[del_inds, np.where(filter_stat < filter['min'])[0]]
        if 'max' in filter: del_inds = np.r_[del_inds, np.where(filter_stat > filter['max'])[0]]
        stat       = np.delete(stat,       del_inds)
        phylo_dist = np.delete(phylo_dist, del_inds)
    
    print len(stat)
    if len(stat) < 3: return  ## exist function if less than 3 pairs pass filter
    
    if log: stat = np.log10(stat)
    phylo_dist   = np.log10(phylo_dist)
    
    ## plot
    if plot:
#        ### scatter plot of stat vs dist
#        fig = plt.figure()
#        ax  = fig.add_subplot(111)
#        h   = ax.plot(np.log10(phylo_dist),stat,'o', ms = ms, alpha = alpha)
#        ## add box with kendall tau and statistical support
#        tau, pval = stats.kendalltau(phylo_dist, stat)
#        stats_str = 'Tau = %.2f \n p_val = %.1e' %(tau,pval)
#        if stats_str:
#            xmin, xmax = plt.xlim()
#            ymin, ymax = plt.ylim()
#            ax.annotate(stats_str, xy=(xmin + 0.05*xmax, ymax - 0.1*abs(ymax) ),  xycoords='data',
#                        xytext=(0,0), textcoords='offset points',
#                        size=10,
#                        bbox=dict(boxstyle="round", fc=(1.0, 0.7, 0.7), ec=(1., .5, .5))
#                        ) 
        kde_2d(phylo_dist,stat)    
        plt.xlabel('log10 (Genetic dist)')
        if statistic == 'matrix': ylabel = G.algo
        else:                     ylabel = statistic + ' ' + G.algo 
        if log: ylabel = 'log10 (' + ylabel +')'              
        plt.ylabel(ylabel) 
        if file: plt.savefig(file)
        if show: plt.show()
    return stat, phylo_dist



def stat_vs_dist(G, dist_mat, **kwargs):
    from matplotlib import rc
    rc('text', usetex=True)

    from itertools import combinations
    from utilities.smoothing import exp_smooth
     
    statistic = kwargs.get('statistic', 'matrix')
    method    = kwargs.get('method', 'direct')
    if   statistic == 'p_vals': stat_mat = G.p_vals[method]
    elif statistic == 'q_vals': stat_mat = G.q_vals[method]
    elif statistic == 'matrix': stat_mat = G.matrix
    
    ## get dist and stat of all pairs
    ids        = stat_mat.row_labels()   # otu ids
    n          = len(ids)
    n_pairs    = n*(n-1)/2.0
    phylo_dist = np.zeros(n_pairs)
    stat       = np.zeros(n_pairs)
    for i,pair in enumerate(combinations(ids,2)):
        p1,p2         = pair
        phylo_dist[i] = dist_mat[p1][p2]
        stat[i]       = stat_mat[p1][p2]
    
    ## sort 
    x    = np.array(sorted(phylo_dist))
    inds = phylo_dist.argsort()
    y    = stat[inds]
    
    ## Get smooth curves
    a = kwargs.get('a',100)
    xnew,ynew = exp_smooth(x,y, a= a, pad = 'none')
    xabs,yabs = exp_smooth(x,abs(y), a= a, pad = 'none')
    
    ## plot
    plot = kwargs.get('plot', True)
    if plot:
        lw       = kwargs.get('lw', 3)
        fs       = kwargs.get('fs', 18)
        fig      = plt.figure()
        h        = plt.plot(np.log10(x),y,'o')
        h_smooth = plt.plot(np.log10(xnew),ynew,'-', lw=lw)
        h_abs    = plt.plot(np.log10(xabs),yabs,'--', lw=lw)
        plt.legend([h,h_smooth,h_abs],['data','avg','abs avg'])
        plt.xlabel('log10 (Genetic dist)', fontsize = fs)
        if statistic == 'matrix': ylabel = G.algo
        else:                     ylabel = statistic + ' ' + G.algo              
        ylabel = 'Correlation'
        plt.ylabel(ylabel, fontsize = fs) 
        plt.ylim([-1,1])
        plt.xlim([-2.0,.5])
        plt.grid()

        
        file = kwargs.get('file', False)
        if file: plt.savefig(file)
        
        show = kwargs.get('show', True)
        if show: plt.show()
    return x,y, xnew,ynew, xabs,yabs


def plot_pairs(G, lag = 0, method = 'direct', scatter = False, base_file = None, norm_tot = True, norm = True, show = False, max_pairs = 20):
    '''
    '''
    file = None
    pairs = sorted(G.edges(), key = lambda pair: G.p_vals[method].matrix[G.ids.index(pair[1]),G.ids.index(pair[0])] )   #G.p_vals[pair[0]][pair[1]]['weight'] )
    for i,pair in enumerate(pairs):
        if i == max_pairs: break
        if base_file: 
            if scatter: file = base_file + '_pair_scatter_' +str(i) + '.pdf'
            else:       file = base_file + '_pair_' +str(i) + '.pdf'
        if lag: driver_flags = [1,0]
        else:   driver_flags = [0,0]
        
        row = G.ids.index(pair[1])
        col = G.ids.index(pair[0])
        sim = G.matrix.matrix[row,col]
        algo      = G.algo
        stats_str = algo + '_ %.2f' %sim
        if method in G.p_vals:
            p_val = G.p_vals[method].matrix[row,col] 
            stats_str += '\n p_val = %.1e' %p_val
        if method in G.q_vals:
            q_val = G.q_vals[method].matrix[row,col] 
            stats_str += '\n q_val = %.1e' %q_val
        
        if scatter: G.abunds.plot_vs_other(otu_ids = pair, driver_flags = driver_flags, lag = lag, file = file, norm_tot = norm_tot, norm = norm, show = False, stats_str = stats_str)
        else:       G.abunds.plot(otu_ids = pair, driver_flags = driver_flags, lag = lag, file = file, norm = norm, show = False, stats_str = stats_str)
    if show and len(pairs) : plt.show()
    


def write_components(net, components, file):
    import csv
    f = open(file,'wb')
    ## write header
    header = ['Component', 'OTU id', 'lineage']
    csvWriter = csv.writer(f)
    writer    = csvWriter.writerow
    writer(header)
    for i,c in enumerate(components):
        writer([''])
        for otu in c:
            line = ['Comp_' +str(i), otu, net.node[otu]['lineage'] ]
            writer(line)
#    ## write otus in components
#    n_comp = map(lambda comp: len(comp),components)
#    n_max  = (np.array(n_comp)).max()
#    for i in range(n_max):
#        line = []
#        for comp in components:
#            if len(comp) > i: line.append(comp[i])
#            else:             line.append('') 
#        writer(line)
    f.close()
            


def write_edges(G, file, csv_flag = True, by_component = True, dist = None, write_lin = True):
    '''
    Write all edges to file.
    Inputs:
        G        = [OTUnet] networks whose edges are to be written.
        file     = [str] name of output file.
        csv_flag = [bool] write to csv format or not.
        dist     = [MatrixDictionary] phylogenetic distances between all nodes. distances will be written if given. 
    '''
    import csv
    f = open(file,'wb')
    ## write header
    if write_lin: header = '\t'.join(['Weight','From_OTU', 'To_OTU', 'From_lineage', 'To_lineage', 'From_lineage_short', 'To_lineage_short']) +'\n'
    else:         header = '\t'.join(['Weight','From_OTU', 'To_OTU']) +'\n'
    if dist is not None: header.append('\t'+'phylo_dist')
    if by_component: header = 'Component' +'\t' + header
    if csv_flag:
        csvWriter = csv.writer(f)
        writer = csvWriter.writerow
        writer(header.split('\t'))
    else:
        writer = f.write 
        writer(header)
    if by_component:
        C = nx.connected_component_subgraphs(G.to_undirected()) # color nodes the same in each connected subgraph
        for i,g in enumerate(C):
            if csv_flag: writer([''])
            else:        writer('\n') 
            edges = g.edges()
            sorted_edges = sorted(edges, key = lambda e: abs(G.edge[e[0]][e[1]]['weight']), reverse=True )
            for e in sorted_edges:
                node_from = e[0]
                node_to   = e[1]
                if node_from == node_to: continue
                weight = G.edge[node_from][node_to]['weight']
                lin1 = G.node[node_from]['lineage']
                lin2 = G.node[node_to]['lineage']
                lin1_short = lineage_short(lin1, depth_max = 2)
                lin2_short = lineage_short(lin2, depth_max = 2) 
                line   = '\t'.join([str(i+1),'%.2f' %weight, str(node_from), str(node_to), lin1, lin2 ]) + '\n' 
                if dist is not None: 
                    line = line[:-2] + '\t' + '%.1e' %dist[node_from][node_to] + '\n' 
                if csv_flag: writer(line.split('\t'))
                else:        writer(line)          
    else:        
        edges = G.edges()
        sorted_edges = sorted(edges, key = lambda e: abs(G.edge[e[0]][e[1]]['weight']), reverse=True )
        for e in sorted_edges:
            node_from = e[0]
            node_to   = e[1]
            if node_from == node_to: continue
            weight = G.edge[node_from][node_to]['weight']
            if dist is not None: 
                line = '\t'.join(['%.1e' %weight, str(node_from), str(node_to), G.node[node_from]['OTU_id'], G.node[node_to]['OTU_id'], G.node[node_from]['lineage'], G.node[node_to]['lineage'],'%.1e' %dist[node_from][node_to] ]) + '\n' 
            else:
                t = G.node[node_from]
                if write_lin:
                    lin1 = G.node[node_from]['lineage']
                    lin2 = G.node[node_to]['lineage']
                    lin1_short = lineage_short(lin1, depth_max = 2)
                    lin2_short = lineage_short(lin2, depth_max = 2) 
                    line = '\t'.join(['%.2f' %weight, str(node_from), str(node_to), lin1, lin2, lin1_short, lin2_short ]) + '\n'
                else:         line = '\t'.join(['%.2f' %weight, str(node_from), str(node_to) ]) + '\n'
            if csv_flag: writer(line.split('\t'))
            else:        writer(line) 
    f.close()    


def write_pajek(G,file):
    '''
    Write network in pajek format
    '''
    G = remove_disc_nodes(G)
    nx.write_pajek(G, file) ## write to pajek
    ## add '/r' to end of each line for windows compatibility
    f = open(file,'r')
    lines = f.readlines()
    f.close()
    new_lines = map(lambda line:line + '\r' , lines)
    f = open(file,'w')
    f.writelines(new_lines)
    f.close()
    

def kde_2d(m1,m2): 
    from pylab import plot, figure, imshow, xlabel, ylabel, cm, show
    from scipy import stats, mgrid, c_, reshape, random, rot90

    xmin = m1.min()
    xmax = m1.max()
    ymin = m2.min()
    ymax = m2.max()

    xmin = -2.5
    xmax = .5
    ymin = -0.80
    ymax = 1

    # Perform a kernel density estimator on the results
    X, Y = mgrid[xmin:xmax:100j, ymin:ymax:100j]
    positions = c_[X.ravel(), Y.ravel()]
    values = c_[m1, m2]
    kernel = stats.kde.gaussian_kde(values.T)
    Z = reshape(kernel(positions.T).T, X.T.shape)

    figure()
    imshow(     rot90(Z),
                cmap=cm.gist_earth_r,
                extent=[xmin, xmax, ymin, ymax])
    plot(m1, m2, 'o',  markersize=1.5)
#    plot(m1, m2, 'mx', markersize=.5)
    plt.xlim(xmin,xmax)
    plt.ylim(ymin,ymax)
    plt.axes().set_aspect('auto', 'box')
    return kernel
    

def test_confusion():
    from HMPStructures.HMPmatrix import HMP_matrix
    k = 3
    node_ids = [str(i) for i in xrange(k)]
    mat1      = np.eye(k)
    mat1[0,1] = -1
    mat1[1,0] = -1
    m1 = HMP_matrix()
    m1.from_matrix(mat1, node_ids, node_ids)
    
    mat2      = np.eye(k)
    mat2[2,1] = 1
    mat2[1,2] = 1
    m2 = HMP_matrix()
    m2.from_matrix(mat2, node_ids, node_ids)
    
    net1 = OTUnetwork(node_ids = node_ids, matrix = m1)
    net2 = OTUnetwork(node_ids = node_ids, matrix = m2)
    add_edges(net1, cutoff = 0.5, statistic = 'matrix', method = 'abs_larger')
    add_edges(net2, cutoff = 0.5, statistic = 'matrix', method = 'abs_larger')
    print confusion_mat(net1,net2)

def test_add_edges():
    from DataStructures.MyDataMatrix import MyDataMatrix as DM
    vals = np.array([[0,1,0],
                     [1,0,1],
                     [0,1,0]])
    ids = ['aa','bb','cc']
    matrix = DM(vals, index=ids, columns=ids)
    net = OTUnetwork(matrix)
    add_edges(net, node='bb')
    print net.edges()
    
    
    
if __name__ == '__main__':
    from DataStructures.MyDataMatrix import MyDataMatrix as DM
    path = '/Users/jonathanfriedman/Documents/Alm/enterotype/correlations/'
    file = 'SparCC_with_pseudo_xiter_0_minpresent_3.pick'
    cSparCC_f = DM.fromPickle(path+file)
    file = 'Spearman_no_pseudo_minpresent_3.pick'
    cSpear_f = DM.fromPickle(path+file)
    netSparCC_f = OTUnetwork(cSparCC_f)
    netSpear_f = OTUnetwork(cSpear_f)
    
    taxons = ['Bacteroides', 'Ruminococcus', 'Prevotella']
    taxon = taxons[0]
    add_edges(netSparCC_f, node=taxon, cutoff=0.4)
    add_edges(netSpear_f, node=taxon, cutoff=0.4)
    netSpear_ff = remove_disc_nodes(netSpear_f)
    netSparCC_ff = remove_disc_nodes(netSparCC_f)
    add_edges(netSpear_ff, cutoff=0.4)
    add_edges(netSparCC_ff, cutoff=0.4)
    confuse = confusion_mat(netSparCC_ff, netSpear_ff, matched=False, sign=False)
    print confuse
#    plot_network(netSpear_ff,show=False, remove_disconnected=True)
#    plot_network(netSparCC_ff, remove_disconnected=True)

    
 
 
 

   
       