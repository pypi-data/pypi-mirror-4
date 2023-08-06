.. _filter:

.. currentmodule:: pysurvey


.. ipython:: python
   :suppress:

   import numpy as np
   import pysurvey as ps
   from pandas import DataFrame as DF
   from numpy import shape, log, where
   np.set_printoptions(precision=4, suppress=True)


*********
Filtering
*********

Filtering by labels
-------------------

Named rows/cols can be removed using pandas' ``drop`` method:

.. ipython:: python

   counts = DF([[0, 1, 2], 
                [3, 4, 5],
                [6, 7, 8]],
               index=['sample_1', 'sample_2', 'sample_3'],
               columns=['otu_1', 'otu_2', 'otu_3'])

   counts.drop(['sample_1'], axis=0)
   counts.drop(['otu_2'], axis=1)


Filtering by values
-------------------

Removing rows/cols whose values correspond to some filtering criteria is done using the :func:`filter_by_vals` method. ``filter_by_vals`` accepts a :class:`DataFrame` and some filtering criteria and keeps only the rows/cols that *pass* these criteria.

Making filtering criteria
~~~~~~~~~~~~~~~~~~~~~~~~~

Each criterion can be either a callable that operates on a :mod:`pandas` :class:`Series` and returns a boolean or a list/tuple consisting of 3 elements:

1. actor = A callable that extracts the quantity of interest from a :class:`Series`.

2. comperator = A callable that compares the actor output to the given value and returns a boolean 

3. value = the value used by the comperator.

For example, the following keeps only elements whose sum is > 10:
 
.. ipython:: python
   
   a = lambda x: x.sum()
   c = lambda v1,v2: v1>v2
   v = 10
   criterion = (a,c,v) 	
   
   ps.filter_by_vals(counts, criterion)
   ps.filter_by_vals(counts, criterion, axis='rows')

Named actors/comperators
~~~~~~~~~~~~~~~~~~~~~~~~~

To make filtering criteria less cumbersome and more readable, several common actors and comperators have been predefined. Each one of these actors/comperators has been assigned a reserved string "name". When ``filter_by_vals`` encounters a string corresponding to the reserved name, it will replace it by the appropriate function.
For example, since 'sum' and '>' are reserved names, the filter of the previous example now simplifies to: 
 
.. ipython:: python
	
   ps.filter_by_vals(counts, ('sum','>',10))


Named actors:

- sum
- average | avg | mean
- median | med
- variance | var
- standard-deviation | std
- minimum | min
- maximum | max
- presence | presence : gives the number of values > 0 in Series.


Named comperators:

- = | ==
- != | -=
- > 
- <
- >=
- <=
- in | contains

The input actor can also be a non-reserved string. 
In this case the string is used as a label, and the actor will retrieve the value of that label from each :class:`Series`.

.. ipython:: python

   c1 = ('sample_2','>=',4)	
   ps.filter_by_vals(counts, c1)
 

Combining filters
~~~~~~~~~~~~~~~~~~

Data can be filtered according to multiple criteria simultaneously: 

.. ipython:: python
   
   c2 = ('presence','<',3)	
   ps.filter_by_vals(counts, c2)
   ps.filter_by_vals(counts, (c1,c2))

The default behavior is to require all filtering criteria to be met.
This behavior can be changed via the ``how`` argument:

.. ipython:: python
   
   # keep columns that pass either c1 or c2
   ps.filter_by_vals(counts, (c1,c2), how='any')
   



