.. _plotting:

.. currentmodule:: pysurvey


.. ipython:: python
   :suppress:

   import numpy as np
   import pysurvey as ps
   from pandas import DataFrame as DF
   from numpy import shape, log, where
   from pylab import *
   np.set_printoptions(precision=4, suppress=True)
   close('all')

********
Plotting
********

While ``pandas`` offers several `plotting methods <http://pandas.pydata.org/pandas-docs/dev/visualization.html>`__, some useful types of graphs are not yet implemented. ``pysurvey`` extends ``pandas``' plotting repertoire by adding the ability to plot (sorted) heatmaps and stacked plots.

The following examples will use data from a 16S survey of mystic lake:

.. ipython:: python

   datafile = '../demo/data/mystic.counts'
   counts = ps.read_txt(datafile)
   # drop control samples and duplicates
   counts = counts.drop(['MEB', 'MSB', 'M8.2', 'M3.2'])
   # keep only the 10 most abundant OTUs
   counts_top = ps.keep(counts,20, axis='c') 
   # normalize
   fracs = ps.normalize(counts_top)


Sorted Heatmaps
---------------

Heatmaps are clustered and sorted using the UPGMA algorithm.

.. ipython:: python
   
   @savefig sorted_heatmap.png width=4.5in
   out = ps.plot_heatmap(fracs)


``plot_heatmap`` takes many optional keyword arguments. Some of the important ones are:

- ``rmetric``|``cmetric`` - [str] the distance metric used to cluster rows/col. Supported metrics are identical to those detailed in :ref:`analysis<dist>` (default='euclidean'). 
- ``rsort``|``csort`` - [bool] whether to sort rows/cols (default=True). 
- ``plot_log`` - [bool] plot values of a log scale (default=True).
- ``cmap`` - [str] colormap. See supported colormaps `here <http://www.scipy.org/Cookbook/Matplotlib/Show_colormaps>`__.

.. ipython:: python
   
   @savefig sorted_heatmap_log.png width=4.5in
   out = ps.plot_heatmap(fracs ,plot_log=True, csort=False, 
                         rmetric='JS', cmap='hot')


Labeling Heatmaps
^^^^^^^^^^^^^^^^^

``plot_heatmap`` has additional keyword arguments for adding ticks and axis labels. 
However, often there are many rows/cols and it is impossible to add reasonably sized tick labels.
For interactive work, clicking on a heatmap displays the row/col label on the heatmap.
Some relevant keywords are:  

- ``plot_rlabels``|``plot_clabels`` - [bool] show the tick labels of rows/cols. 
- ``rfontsize``|``cfontsize`` - [float] size of tick labels (default=12).
- ``rlabel_width``\``clabel_width`` - [float] width of margin for tick labels (default=0.03). 
- ``xlabel``|``ylabel`` - [str] labels for x/y axis.
- ``fontsize`` - [float] size of axes labels (default=18). 

.. ipython:: python
   
   @savefig sorted_heatmap_labeled.png width=4.5in
   out = ps.plot_heatmap(fracs, plot_log=True, 
			 plot_rlabels=True,
			 clabel_width=0, 
			 xlabel='OTUs')

.. note::

   ``pysurvey`` attempts to automatically determine the width of tick labels.
   However, sometimes the labels overlap with the dendrogram. In such cases, the ``rlabel_width``|``clabel_width``
   arguments can be used to adjust these widths manually.


Color strips
^^^^^^^^^^^^

``plot_heatmap`` can show row/col metadata as an additional color strip.
The contents of the color strips are controlled through the ``cstrip``/``rstrip`` arguments, and their properties are set 
using the ``cstrip_kwargs``/``rstrip_kwargs`` arguments.

.. ipython:: python
   
   # create metadata
   depth = [float(id[1:]) for id in fracs.index]
   metar = DF(depth, index= fracs.index, columns=['depth'])
   metar['zone'] = 'a'
   metar['zone'][metar['depth']>10] = 'b'

   @savefig sorted_heatmap_rstrip.png width=4.5in
   out = ps.plot_heatmap(fracs, plot_log=True, 
                         plot_rlabels=True, 
                         rstrip=metar['zone'], 
                         rstrip_kwargs = {'cmap':'Accent'})

Stacked Plots
-------------

Stacked plot are useful for plotting relatively few OTUs when the samples have some order.
In this example, we first sort the samples by the water depth:  

.. ipython:: python

   # sort by depth
   fracs_sorted = ps.sort_by_meta(fracs, metar, axis='rows',columns='depth')
   fracs_sorted.index


Drawing a stacked plot:

.. ipython:: python

   @savefig stacked.png width=4.5in
   ps.stacked_plot(fracs_sorted, labelx=True, ylabel='Fraction')


