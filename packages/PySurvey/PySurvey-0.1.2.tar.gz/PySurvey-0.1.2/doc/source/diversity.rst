.. _diversity:

.. currentmodule:: pysurvey


.. ipython:: python
   :suppress:

   import numpy as np
   import pysurvey as ps
   from pandas import DataFrame as DF
   from numpy import shape, log, where
   np.set_printoptions(precision=4, suppress=True)


*********
Diversity
*********

Various measures of (alpha) diversity can be computed using the :func:`~sample_diversity` method.

Supported diversity indices are:

- ``Hill_n``      - The effective number of components (Hill number) of order n
- ``Richness``    - The number of components present in sample. Sames as Hill_0.
- ``Shannon``     - Shannon entropy. Same as Reyni_1.
- ``Renyi_n``     - Reyni enropy of order n. Same as log(Hill_n). Reyni_1 is the Shannon entropy.
- ``Simpson``     - Simpson's index of diversity. Same as 1/Hill_2.
- ``Simpson_Inv`` - The inverse of simpson's index. Same as Hill_2.

.. ipython:: python	

   counts = DF([[0, 1, 2], 
                [3, 4, 5],
                [6, 7, 8]],
               index=['sample_1', 'sample_2', 'sample_3'],
               columns=['otu_1', 'otu_2', 'otu_3'])

   ps.sample_diversity(counts, indices=['Richness', 'Hill_0'])
   ps.sample_diversity(counts,indices=['Shannon', 'Renyi_1'])


The keyword argument ``methods`` determines the methods used to estimate the diversity indices.
By default it is set to the maximum likelihood estimator ('ML'). Other supported values are ``chao1`` and ``ACE``, which can be used for richness estimation. 

.. ipython:: python	

   ps.sample_diversity(counts,
                       indices=['Richness', 'Richness', 'Richness'], 
                       methods=['ML','chao1','ACE']) 
