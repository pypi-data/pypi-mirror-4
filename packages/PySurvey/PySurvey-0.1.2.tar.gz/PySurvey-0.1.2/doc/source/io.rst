.. _io:

.. currentmodule:: pysurvey


.. ipython:: python
   :suppress:

   import numpy as np
   import pysurvey, os
   from numpy import shape, log, where
   np.set_printoptions(precision=4, suppress=True)


***
IO
***

:mod:`pandas` offers IO tools for several formats.
See: http://pandas.pydata.org/pandas-docs/dev/io.html   

:mod:`pysurvey` augments these tools with 2 functions :func:`~pysurvey.read_txt` and :func:`~pysurvey.write_txt` used to read/write delimited text files that
may contain taxonomic information. Such files are commonly used in 16S surveys.  

.. _read_txt:

Reading text files
------------------

By default, :mod:`pysurvey` assumes that rows correspond to samples and columns to components.
Text files containing genomic survey data often have the reverse situation, since the number of components is typically much larger than the number of samples.
Therefore, by default ``read_txt`` will transpose the input data.
This behavior can be changed by passing ``T=False`` to ``read_txt``.    

.. ipython:: python
   
   import pysurvey as ps
   datafile = '../demo/data/fake_data.counts'
   ps.read_txt(datafile) 
   ps.read_txt(datafile, T=False)


``read_txt`` will try and automatically detected whether input files contain 
lineage information. If lineage information is detected, it is returned as a :class:`Lineages` object.

.. ipython:: python
   
   datafile = '../demo/data/fake_data_lin.counts'
   counts,lins = ps.read_txt(datafile) # file with lineages
   counts
   lins
   type(lins)

Lineage information can only be detected if it has a "reasonable" column header, such as lineage, or taxa. If the column containing the lineage information is labeled differently, the lineage label needs to be specified via the ``lin_label`` argument.

.. ipython:: python
   
   datafile = '../demo/data/fake_data_lin2.counts'
   counts,lins = ps.read_txt(datafile, lin=True, lin_label='lin_info') # file with lineages
   counts
   lins


.. ipython:: python
	
   datafile = '../demo/data/fake_data_out.counts'
   ps.write_txt(counts, datafile)


Writing text files
------------------

When a :class:`DataFrame` is written using ``write_txt``, it is also transposed by default to produce a text file that can be then read directly using ``read_txt``. 
This behavior is controlled by the ``T`` argument.

.. ipython:: python
   
   datafile = '../demo/data/fake_data.counts'
   ps.write_txt(counts, datafile) 

If a :class:`Lineages` object is passed through the ``lin`` argument, the lineage information is also written ou. The lineage column is by default titled "lineage", and can be changed via the ``lin_label`` argument.

.. ipython:: python

   datafile = '../demo/data/fake_data_lin.counts'
   ps.write_txt(counts, datafile, lin=lins)
   
   datafile = '../demo/data/fake_data_lin2.counts'
   ps.write_txt(counts, datafile, lin=lins, lin_label='lin_info') 



