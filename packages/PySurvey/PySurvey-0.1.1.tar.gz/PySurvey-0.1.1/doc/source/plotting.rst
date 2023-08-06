.. _plotting:

.. currentmodule:: survey


.. ipython:: python
   :suppress:

   import numpy as np
   import survey
   from survey.SurveyMatrix import SurveyMatrix as SM
   from numpy import shape, log, where
   from pylab import *
   np.set_printoptions(precision=4, suppress=True)

********
Plotting
********

Plotting is done using `matplotlib <http://matplotlib.sourceforge.net/>`__ and `matplotlibX <https://bitbucket.org/yonatanf/matplotlibx/overview>`__, which need to be installed to enable plotting. See the documentation of these packages for more detailed information. 

The following examples will use data from a 16S survey of mystic lake:

.. ipython:: python

   file = '../demo/data/mystic_filtered.pick'
   counts = SM.fromPickle(file)
   #normalize
   fracs = counts.normalize()


Sorted Heatmaps
---------------

Heatmaps are clustered and sorted using the UPGMA algorithm.

.. ipython:: python
   
   @savefig sorted_heatmap.png width=4.5in
   out = fracs.plot_heatmap()


``plot_heatmap`` takes many optional keyword arguments. Some of the important ones are:

- ``row_metric``/``col_metric`` - [str] the distance metric used to cluster rows/col. Supported metrics are identical to those detailed in :ref:`tutorial.dist` (default='euclidean'). 
- ``sort_rows``/``sort_cols`` - [bool] whether to sort rows/cols (default=True). 
- ``plot_log`` - [bool] plot values of a log scale (default=True).
- ``cmap`` - [str] colormap. See supported colormaps `here <http://www.scipy.org/Cookbook/Matplotlib/Show_colormaps>`__.

.. ipython:: python
   
   @savefig sorted_heatmap_log.png width=4.5in
   out = fracs.plot_heatmap(plot_log=True, sort_cols=False, 
                            row_metric='JS', cmap='hot')


Labeling Heatmaps
^^^^^^^^^^^^^^^^^

``plot_heatmap`` has additional keyword arguments for adding ticks and axis labels. 
However, often there are many rows/cols and it is impossible to add reasonably sized tick labels.
For interactive work, clicking on a heatmap displays the row/col label on the heatmap.
Some relevant keywords are:  

- ``plot_row_labels``/``plot_col_labels`` - [bool] show the tick labels of rows/cols. 
- ``row_fontsize``/``col_fontsize`` - [float] size of tick labels (default=12).
- ``row_label_width``/``col_label_width`` - [float] width of margin for tick labels (default=0.03). 
- ``xlabel``\``ylabel`` - [str] labels for x/y axis.
- ``fontsize`` - [float] size of axes labels (default=18). 

.. ipython:: python
   
   @savefig sorted_heatmap_labeled.png width=4.5in
   out = fracs.plot_heatmap(plot_log=True, plot_row_labels=True,
			    row_label_width=0.06, col_label_width=0, 
			    xlabel='OTUs')

.. note::

   The width of tick labels needs to be adjusted manually, depending on the length of the labels and the font size.
   This is really annoying, so if you know how to automate this do tell.


Stacked Plots
-------------

Stacked plot are useful for plotting relatively few OTUs when the samples have some order.
In this example, we first sort the samples by the water depth:  

.. ipython:: python

   # add depth metadata
   depth = [float(id[1:]) for id in counts.index]
   counts.metar['depth'] = depth
   # sort by depth
   counts_sorted = counts.sort_by_meta(axis='rows',column='depth')
   counts_sorted.index

Now we only keep the 5 most abundant OTUs:

.. ipython:: python

   fracs5 = counts_sorted.normalize().keep(5)

Finally, make a stacked plot:

.. ipython:: python

   @savefig stacked.png width=4.5in
   fracs5.stacked_plot(labelx=True, legend=True, ylabel='Fraction')



Line Plots
----------

Line plots show a line for each column.

.. ipython:: python

   @savefig lineplot.png width=4.5in
   fracs5.plot_cols(ylog=True, ylabel='Fraction', labelx=True, lw=3)



