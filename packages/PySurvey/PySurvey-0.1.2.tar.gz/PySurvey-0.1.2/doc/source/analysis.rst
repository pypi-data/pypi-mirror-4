.. _analysis:

.. currentmodule:: pysurvey


.. ipython:: python
   :suppress:

   import numpy as np
   import pysurvey as ps
   from pandas import DataFrame as DF
   from numpy import shape, log, where, nan
   np.set_printoptions(precision=4, suppress=True)


**************
Analysis tools
**************

Normalizing
-----------

Component fractions can be estimated from counts data using the :func:`~normalize` and :func:`~to_fractions` methods.
``normalize`` simply divides each rows's values by their sum:

.. ipython:: python

   counts = DF([[0, 1, 2], 
                [3, 4, 5],
                [6, 7, 8]],
               index=['sample_1', 'sample_2', 'sample_3'],
               columns=['otu_1', 'otu_2', 'otu_3'])
	
   ps. normalize(counts)

``to_fractions`` supports several normalization methods, selected using the ``method`` keyword:

- ``normalize``: same as the ``normalize`` method.
- ``pseudo``: add pseudo counts to all values (default 1), and normalize. 
- ``dirichlet``: randomly draw from posterior Dirichlet distribution with uniform prior.  

.. ipython:: python
	
   ps.to_fractions(counts,method='normalize')
   ps.to_fractions(counts,method='pseudo')
   ps.to_fractions(counts,method='pseudo', p_counts=10)
   ps.to_fractions(counts,method='normalize')
   ps.to_fractions(counts,method='dirichlet')
   ps.to_fractions(counts,method='dirichlet')   


.. _dist:

Distance Matrices
------------------

Pairwise distance between rows/cols are computed using the :func:`~dist_mat` method. This method supports all the metrics supported by `scipy.spatial.distance.pdist <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html#scipy.spatial.distance.pdist>`__, 
as well as several custom metrics:

- ``JS`` - Jensen-Shannon divergence. Information theoretic measure of distance between distributions (or any sets of numbers who's sum is 1). Gives each taxa a weight proportional to its relative abundance.

- ``JSsqrt`` - the square-root of Jensen-Shannon divergence. Upholds the triangular inequality, and is therefore a true metric.

- ``Morisita`` - the Morisita-Horn dissimilarity index. Gives more weight to more abundant taxa. 


.. ipython:: python	

   ps.dist_mat(counts,metric='jaccard', axis='cols')
   fracs = ps.normalize(counts)
   ps.dist_mat(fracs, metric='JS')


