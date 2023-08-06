.. _basics:

.. currentmodule:: survey2


.. ipython:: python
   :suppress:

   import numpy as np
   import survey2
   from numpy import shape, log, where
   np.set_printoptions(precision=4, suppress=True)

********
Basics
********

This section demonstrates the basics of working with :mod:`survey2` and shows how to perform some common tasks.
To access :mod:`survey2`, you'll need to import it to your namespace:

.. ipython:: python

   from survey2 import *

.. note::
	
    To use :mod:`survey2` on Beagle you'll need to preload some modules. 
    A shell script is supplied to do so automatically and start an ipython session:
    ``/home/yonatanf/alm_lib/mipython.sh``.
    If you use this script the above imports are done automatically.
    


survey2Matrix Basics
-------------------

:class:`survey2Matrix` is :mod:`survey2`'s main data structure.
It is a labeled 2D ndarray, i.e. a numpy ndarray with named rows and columns.

The numerical data can be manipulated just like a regular ndarray:

.. ipython:: python

   x = SM([[0.,1],[2,3],[4,5]], columns=['OTU1','OTU2'], 
          index=['sample'+str(i) for i in xrange(3)])
   x
   x+10
   x*2
   log(x)
   x.sum(axis=1)

The rows and columns labels allow for easier indexing:  

.. ipython:: python

   x['OTU1']
   x.xs('sample1')
   x['OTU2']['sample2']

For more detailed information on manipulating and indexing see the `pandas <http://pandas.sourceforge.net/index.html>`__ documentation (specifically the :class:`DataFrame` section).   


Loading/Saving
--------------

Data can be parsed from a tab delimited plain text file:

.. ipython:: python

   file = '../demo/data/fake_data.counts'
   counts = SM.fromTxt(file)
   counts

Loaded data can be exported to a text file, or pickled:

.. ipython:: python
	
   file = '../demo/data/fake_data_out.counts'
   counts.toTxt(file)
   file = '../demo/data/fake_data.pick'
   counts.toPickle(file)
   
Previously pickled data can be loaded directly: 

.. ipython:: python
	
   file = '../demo/data/fake_data.pick'
   SM.fromPickle(file)


.. warning::
	
    :mod:`survey2` assumes that rows correspond to samples and columns to components (e.g. OTUs), and may fail, or produce nonsensical results if this convention is not upheld. This is not automatic verified when data is imported, as I could not come up with a smart way of doing that. 


Normalizing
-----------

Component fractions can be estimated from counts data using the ``normalize`` and ``to_fractions`` methods.
``normalize`` simply divides each rows's values by their sum:

.. ipython:: python
	
   counts.normalize()

``to_fractions`` supports several normalization methods, selected using the ``method`` keyword:

- ``normalize``: same as the ``normalize`` method.
- ``pseudo``: add pseudo counts to all values (default 1), and normalize. 
- ``dirichlet``: randomly draw from posterior Dirichlet distribution with uniform prior.  

.. ipython:: python
	
   counts.to_fractions(method='normalize')
   counts.to_fractions(method='pseudo')
   counts.to_fractions(method='pseudo', p_counts=10)
   counts.to_fractions(method='dirichlet')
   counts.to_fractions(method='dirichlet')


Filtering
----------

Named rows/cols can be removed using the ``remove_rows``/``remove_cols`` methods.


.. ipython:: python
	
   counts.remove_rows(['sample_1'])
   counts.remove_cols(['otu_2'])

Removing rows/cols whose values correspond to some filtering criteria is done using the ``filter_by_vals`` method. ``filter_by_vals`` has the following predefined filters:

- ``min_sum``: the minimal sum of values in col/row to be kept. 
- ``min_avg``: the minimal average value of col/row to be kept. 
- ``min_present``: the minimal number of values>0 in col/row to be kept. 
 
.. ipython:: python
	
   counts.filter_by_vals(min_sum=7)
   counts.filter_by_vals(min_avg=6, axis='rows')

Additionally, user-defined filter functions can be used:

.. ipython:: python
	
   # filter rows/cols that have no values=3 
   f = lambda z: len(where(z==3)[0])==0
   counts.filter_by_vals(funcs=[f], axis='rows')
   # combine filters
   counts.filter_by_vals(min_sum=13, funcs=[f], axis='rows')


.. _tutorial.dist:

Distance Matrices
------------------

All pairwise distance between rows/cols can be computed using the ``dist_mat`` method:

::

    survey2Matrix.dist_mat(self, metric='euclidean', axis=0)

Supported metrics include:

- All the metrics supported by `scipy.spatial.distance.pdist <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html#scipy.spatial.distance.pdist>`__.

- ``JS`` - Jensen-Shannon divergence. Information theoretic measure of distance between distributions (or any sets of numbers who's sum is 1). Gives each taxa a weight proportional to its relative abundance.

- ``JSsqrt`` - the square-root of Jensen-Shannon divergence. Upholds the triangular inequality, and is therefore a true metric.

- ``Morisita`` - the Morisita-Horn dissimilarity index. Gives more weight to more abundant taxa. 


.. ipython:: python	

   counts.dist_mat(metric='jaccard', axis='cols')
   counts.normalize().dist_mat(metric='JS')



Sample Diversity
----------------

Various measures of (alpha) diversity can be computed using the ``sample_diversity`` method (which wraps around the ``sample_diversity`` function of the :doc:`diversity` module).

::

    survey2Matrix.sample_diversity(self, indices='Hill_1', **kwargs)


Supported indices are:

- ``Hill_n``      - The effective number of components (Hill number) of order n
- ``Richness``    - The number of components present in sample. Sames as Hill_0.
- ``Shannon``     - Shannon entropy. Same as Reyni_1.
- ``Renyi_n``     - Reyni enropy of order n. Same as log(Hill_n). Reyni_1 is the Shannon entropy.
- ``Simpson``     - Simpson's index of diversity. Same as 1/Hill_2.
- ``Simpson_Inv`` - The inverse of simpson's index. Same as Hill_2.

.. ipython:: python	

   counts.sample_diversity(indices=['Richness', 'Hill_0'])
   counts.sample_diversity(indices=['Shannon', 'Renyi_1'])


The keyword argument ``methods`` determines the methods used to estimate the diversity indices.
By default it is set to the maximum likelihood estimator ('ML'). Other supported values are ``chao1`` and ``ACE``, which can be used for richness estimation. 

.. ipython:: python	

   counts.sample_diversity(indices=['Richness', 'Richness', 'Richness'], 
                           methods=['ML','chao1','ACE']) 
