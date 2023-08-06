'''
Created on Jul 20, 2011

@author: jonathanfriedman
'''
#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from survey2 import *
from numpy import log, log10


# <demo> --- stop ---
#-----------------------------------------------------------------------------
# The Data Structure and basic utilities (Small fake dataset)
#-----------------------------------------------------------------------------

# read data without lineage info
file = 'data/fake_data.counts'
counts_fake = read_txt(file)
print counts_fake, '\n'

# <demo> --- stop ---
# read data with lineage info
file = 'data/fake_data_lin.counts'
counts_fake, lins = read_txt(file)
print lins, '\n'

# <demo> --- stop ---
##### indexing
print counts_fake['otu_1'], '\n'
print counts_fake.xs('sample_1'), '\n'

# <demo> --- stop ---
##### basic operations
print counts_fake + 10, '\n'
print counts_fake * 2, '\n'
print log(counts_fake), '\n'
print counts_fake.sum(axis=1), '\n'

# <demo> --- stop ---
#-----------------------------------------------------------------------------
## General Exploratory Data Analysis 
## Using real data (Mystic lake), done in real time
#-----------------------------------------------------------------------------

#load counts
file = 'data/mystic.counts'
counts = read_txt(file)
counts = counts.drop(['MSB','MEB','M3.2','M8.2']) # remove controls & duplicates
print counts.shape

# <demo> --- stop ---
# total number of reads per sample
tot = counts.sum(axis=1)
tot.sort()
print tot[:10] 

# <demo> --- stop ---
#plot unsorted heatmap
fracs = normalize(counts)
plot_heatmap(fracs,csort=False, plot_log=True,
                   plot_rlabels=True, rlabel_width=0.06, 
                   file='figs/mystic_frac_heatmap_log.pdf')

# <demo> --- stop ---
#filter taxa
counts_f = filter_by_vals(counts, ('avg','>', 1e-3), axis='cols', norm=True)
print counts_f.shape, '\n'

# <demo> --- stop ---
#plot sorted heatmap
fracs_f = normalize(counts_f)
plot_heatmap(fracs_f, plot_log=True,
             plot_rlabels=True,
             file='figs/mystic_frac_filtered_heatmap_log.pdf')

# <demo> --- stop ---
# plot dist heatmap
D = dist_mat(fracs_f, axis='rows', metric='JSsqrt')
plot_heatmap(D, dist_mat=True,
             plot_rlabels=True, plot_clabels=True,
             file='figs/mystic_sample_dist_JSsqrt.pdf')

# <demo> --- stop ---
# Dimension reduction and GMM
out = GMM_plot(D,n_components=4, 
               file = 'figs/mystic_genera_PCoA_JSsqrt_GMM.pdf')
membership_hard, gmm, points, eigs = out
print membership_hard, '\n'

# <demo> --- stop ---
# Heatmaps with color strips
plot_heatmap(D, dist_mat=True,
             plot_rlabels=True, plot_clabels=True,
             rstrip=membership_hard, strip_width=0.02,
             file='figs/mystic_sample_dist_JSsqrt_colorstrips.pdf')

# <demo> --- stop ---
##### working with metadata
# make metadata (this will typically be loaded from file)
depth = [float(id[1:]) for id in counts_f.index]
metar = DF(depth, columns=['depth'], index=counts_f.index)

# sort by depth
counts_sorted = sort_by_meta(counts_f,metar,axis='rows',columns='depth')
print counts_sorted.index, '\n'

# <demo> --- stop ---
##### grouping taxa
#load lineages
file = 'data/mystic.lins'
lins = Lineages.from_txt(file, format='rdp')
lins_f = lins.filter(counts_f.columns) 

# group taxa
phyla  = group_taxa(counts_sorted, lins_f, 'p')
genera = group_taxa(counts_sorted, lins_f,'g')
print phyla.shape, '\n'
print genera.shape, '\n'
print phyla.columns, '\n'

# <demo> --- stop ---
# Keeping and stack plots
phyla_fracs     = normalize(phyla)
phyla_fracs_top = keep(phyla_fracs, 5, 'avg', axis='c')
stacked_plot(phyla_fracs_top, legend=True, 
             xlabel='Sample', ylabel='Fraction', labelx=True,
             file='figs/mystic_phyla_top_5.pdf')

# <demo> --- stop ---
genera_fracs     = normalize(genera)
genera_fracs_top = keep(genera_fracs, 20, 'avg', axis='c')
stacked_plot(genera_fracs_top, 
             xlabel='Sample', ylabel='Fraction', labelx=True, 
             file='figs/mystic_genera_top_20.pdf')

# <demo> --- stop ---
# Find discriminating OTUs
shallow = filter_by_meta(genera_fracs, metar, ('_depth','<=',10), axis=0)
deep    = filter_by_meta(genera_fracs, metar, ('_depth','>',10), axis=0)
discriminating = discriminating_components(shallow, deep)
print discriminating[:5]

# <demo> --- stop ---
# correlation network
top_genera = genera_fracs_top.columns
cor, cov   = basis_corr(genera.reindex(columns=top_genera),iter=5)

import networkx as nx
from survey2.sandbox import network_methods as nm
net = nm.make_network(cor, 0.9)
nm.plot_network(net, node_sizes=genera_fracs_top.mean(), scale_sizes=True,
                  remove_disconnected=True, layout='spring',
                  file='figs/mystic_genera_top_20_spearman_net.pdf')
nx.write_gml(net,'out/mystic_genera_top_20_spearman_net.gml')


# <demo> --- stop ---
#-----------------------------------------------------------------------------
## Ecological theory (Saliva data from the HMP)
#-----------------------------------------------------------------------------
file = 'data/hmp_Saliva.counts'
counts = read_txt(file, T=False)
fracs  = normalize(counts)
print counts.shape

# <demo> --- stop ---
#### Alpha diversity
# Richness
dive = sample_diversity(counts, 
                        indices=['richness','richness'], 
                        methods=['ML','Chao1'])
plot_cols(dive, xlabel='Sample', ylabel= 'Diversity',
               file='figs/hmp_Saliva_richness.pdf')

# <demo> --- stop ---
# Dependence of sequencing depth
dive = sample_diversity(counts, indices = ['richness','shannon','simpson'])
dive['N reads'] = counts.sum(axis=1)
plot_cols(log10(dive), xlabel='Sample', ylabel= 'Diversity',
          file='figs/hmp_Saliva_diversity_log.pdf')

# <demo> --- stop ---
# abundance vs. incidence
plot_incidence_abunance(fracs, frac_log=False,
                        file = 'figs/hmp_Saliva_abundance_vs_presence.pdf')

# <demo> --- stop ---
## Fitting taxa distribution
#from survey2.component_dist.component_dist import MarginalDist
#file = 'data/hmp_Saliva_genera.counts.pick'
#genera = DF.load(file)
#fit = MarginalDist(genera, component='g.Prevotella')
#fit.estimate_params('Neutral', 'beta', [1,1])
#fit.estimate_params('Simplex RW', 'logitnorm', [0,1])
#fit.plot_fit(file = 'figs/hmp_Saliva_Prevotella_pdf.pdf')


# <demo> --- stop ---
## Additional features (implement/under development):
#    - Dimension reduction: PCoA, PCA, NMDS
#    - c-means clustering
#    - Mutual Information
#
#    - Rarefaction
#    - Beta Diversity
#    - Rank abundance
#    - Relative Species abundance RSA, with Preston binning.


 # <demo> --- stop ---
if __name__ == '__main__':
    pass
#    # <demo> --- stop ---
#    # rank abundance
#    ra = fracs.plot_rank_abundance(file='figs/rank_abundance.pdf')

## <demo> --- stop ---
## fuzzy clustering
#metric1 = 'euclidean'
#metric2 = 'JS'
#r = 1.01
#k = arange(2,6)
#sil_widths1, membership, membership_hard, stats_best = genera_fracs.fuzzy_clustering(k, r=r, metric=metric1)
#sil_widths2, membership, membership_hard, stats_best = genera_fracs.fuzzy_clustering(k, r=r, metric=metric2)
#sil_widths1.join(sil_widths2).bar_plot(style='grouped', legend=True,
#                                       xlabel='# clusters', ylabel='<silhouette>',
#                                       file='figs/mystic_genera_fuzzy_clustering_sil_widths.pdf' )
#print membership_hard
