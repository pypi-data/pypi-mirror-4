.. _basics:

.. currentmodule:: pysurvey


.. ipython:: python
   :suppress:

   import numpy as np
   import pysurvey, os
   from numpy import shape, log, where
   np.set_printoptions(precision=4, suppress=True)


*******
Basics
*******

This section demonstrates the basics of working with :mod:`pysurvey` and shows how to perform some common tasks.
Since :mod:`pysurvey` makes extensive use  of the `pandas package <http://pandas.sourceforge.net/index.html>`__, users should familiarize themselves with it. In particular pandas' :class:`DataFrame` is the basic object that most `survey` methods operate on. 
The following section gives a very brief introduction to :class:`DataFrame`.
The detailed documentation, is available at: http://pandas.pydata.org/pandas-docs/stable/index.html .


Intro to :class:`DataFrame`
---------------------------

:class:`DataFrame` is :mod:`pysurvey`'s main data structure.
It is a labeled 2D ndarray, i.e. a numpy ndarray with named rows and columns.

The numerical data can be manipulated just like a regular ndarray:

.. ipython:: python

   from pandas import DataFrame as DF	
   x = DF([[0.,1],[2,3],[4,5]], columns=['OTU1','OTU2'], 
          index=['sample'+str(i) for i in xrange(3)])
   x
   x+10
   x*2
   log(x)

The rows and columns labels allow for easy, intuitive indexing:  

.. ipython:: python

   x['OTU1']
   x.xs('sample1')
   x['OTU2']['sample2']

For more detailed information on manipulating and indexing see the `pandas <http://pandas.sourceforge.net/index.html>`__ documentation (specifically the :class:`DataFrame` section).   


Data convention 
---------------

Most :mod:`pysurvey` functions operate on a matrix containing counts or fractions of a set of components over a set of samples. 
The standard convention is to have rows correspond to samples and columns to components (e.g. OTUs). :mod:`pysurvey` assumes that this convention is met. If it is not upheld, some functions may fail, or produce nonsensical results. This is *not* automatically verified when data is imported. 


Axes naming
------------

In :mod:`numpy`, :mod:`pandas`, and :mod:`pysurvey` axes labeled numerically from 0.
In a 2D array/frame, the axis=0 corresponds to rows, and axis=1 corresponds to columns. 
Though this convention is pretty straightforward, operating on the right axis (rows/columns) can be surprisingly confusing.
This confusion stems from the fact that operating on an axis can either mean "on each element of the axis" or "along each element of the axis". The latter logic is the one implemented in :mod:`numpy` and, largely, in :mod:`pandas`. 
For example,

.. ipython:: python

   x.sum(axis=1)   

gives the sum *along* each column, thus yielding the sum of each row.

In :mod:`pandas` and, more commonly, in :mod:`pysurvey` the alternative logic is preferred and operations are conducted on each element of the specified axis.
For example,

.. ipython:: python
   
   import pysurvey as ps
   ps.normalize(x ,axis=1)

normalized each column such that it sums to 1. 
In :mod:`pandas` and :mod:`pysurvey`, a function's docstring will usually explicitly say how the ``axis`` parameter is implemented. 

