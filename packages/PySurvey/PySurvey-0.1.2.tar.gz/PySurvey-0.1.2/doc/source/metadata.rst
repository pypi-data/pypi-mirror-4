.. _metadata:

.. currentmodule:: pysurvey


.. ipython:: python
   :suppress:

   import numpy as np
   import pysurvey as ps
   from pandas import DataFrame as DF
   from numpy import shape, log, where, nan
   np.set_printoptions(precision=4, suppress=True)


********
Metadata
********

Metadata is any data related to the components or samples in addition to the abundance information. For example, sample metadata may include the sampling location, sampling date, etc'. For the case where component are OTUs, metadata may include their aerobic requirements, metabolic capabilities, etc'. 

In :mod:`pysurvey` metadata should be stored in a :class:`DataFrame` whose columns are the metadata categories and rows are the samples/components. The metadata frame may contain more or less samples/components then the abundance frame. However only samples/components whose labels correspond *exactly* to the abundance frame labels are used when manipulating the abundance frame.

.. note::
   The metadata frame should always have the objects (samples/components) to which the metadata refers as rows, regardless of their corresponding axis in the abundance frame.
   


Working with metadata
----------------------

To demonstrate metadata operations, let's first create an abundance frame, and corresponding metadata:

.. ipython:: python

   samples = ('sample1', 'sample2', 'sample3', 'sample4')
   otus = ('otu1', 'otu2', 'otu3')
   
   # OTU metadata
   metao = DF([[nan,'big',True],
               ['Entero','small',False],
               ['Blautia','tiny', nan]], 
              columns=['name', 'size','aerobic'],
              index=otus)
   print(metao)
   
   # sample metadata
   metas = DF([[nan,20],
               ['subject2',50],
               ['subject1',35]], 
              columns=['name', 'age'],
              index=samples[:-1])
   print(metas)
   
   # abundance data 
   counts = DF([[2., nan,1], 
                [1, 3, 2],
                [10, 15,3],
                [0,0,1]],
               index=samples,
               columns=otus)
   print(counts)


Note that some metadata is missing. For example, there is no metadata for sample4, and the name of otu1 is unknown. 

Dropping elements with missing metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Row/columns that are missing meta data can be removed using the :func:`~pysurvey.drop_missing_meta` function:

.. ipython:: python

   # drop samples with any missing metadata
   ps.drop_missing_meta(counts, metas, axis='r')
   
   # drop OTUs with any missing metadata
   ps.drop_missing_meta(counts, metao) 

   # drop OTUs with missing name
   ps.drop_missing_meta(counts, metao, labels='name')


Filtering by metadata
~~~~~~~~~~~~~~~~~~~~~~

More generally, the abundance frame can be filtered according to the metadata values using the :func:`~pysurvey.filter_by_meta` function:

.. ipython:: python

   ps.filter_by_meta(counts, metao, ('size','==','big'))
   ps.filter_by_meta(counts, metas, ('age','<',40), axis='r')
   
By default, ``filter_by_meta`` removes element with missing metadata. 
This behavior is controlled using the ``filter_missing`` argument:

.. ipython:: python

   ps.filter_by_meta(counts, metao, ('aerobic','==',True))
   ps.filter_by_meta(counts, metao, ('aerobic','==',True), filter_missing=False)


Sorting by metadata
~~~~~~~~~~~~~~~~~~~

the abundance frame can be sorting according to the metadata values using the :func:`~pysurvey.sort_by_meta` function:

.. ipython:: python

   ps.sort_by_meta(counts,metas,axis='r',columns='age')

