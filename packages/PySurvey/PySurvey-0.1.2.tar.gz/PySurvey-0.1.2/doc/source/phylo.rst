.. _phylo:

.. currentmodule:: pysurvey


.. ipython:: python
   :suppress:

   import numpy as np
   import pysurvey as ps
   from pandas import DataFrame as DF
   from numpy import shape, log, where
   np.set_printoptions(precision=4, suppress=True)

***********
Phylogenies
***********

When working with 16S surveys, it is often desirable to include phylogenetic information in the analysis.
This section shows the basics of the way phylogenetic information is parsed, stored and used in :mod:`pysurvey`.     

:class:`Lineages` is the data structure used to hold phylogenetic information. It is a Python `Dictionary <http://docs.python.org/release/2.5.2/lib/typeDFapping.html>`__ with additional methods, which hold :class:`Lineage` objects. 


Taxonomy Formats
----------------

The taxonomy formats that can be parsed by `survey` are the following:


- ``QIIME`` - pairs of '[levelName]__[assignment]' separated by semicolons. Level names are displayed even for unassigned levels. This is the default format. Examples:

   * `k__Bacteria;p__Firmicutes;c__Clostridia;o__Clostridiales;f__Veillonellaceae;g__;s__`
   * `k__Bacteria;p__Proteobacteria;c__Gammaproteobacteria;o__;f__;g__;s__`

- ``HMP`` - pairs of '[assignment]([confidence])' separated by semicolons. Unassigned levels are omitted. Examples:

   * `Root(100);Bacteria(100);"Firmicutes"(100);"Bacilli"(100);Bacillales(100);Bacillaceae(99);Bacillus(99);`
   * `Root(100);Bacteria(100);"Firmicutes"(100);"Clostridia"(100);Clostridiales(100);`  

- ``RDP`` - triplets of '[assignment]\\t[levelName]\t[confidence]', separated by tabs. Unassigned levels are blanks, and all tabs are retained! Examples:

   * `Bacteria\\tdomain\\t0.98\\tOD1\\tphylum\\t0.47\\t\\t\\t\\t\\t\\t\\t\\t\\t\\tOD1_genera_incertae_sedis\\tgenus\\t0.47`


Parsing taxonomies 
-------------------

Taxonomic information is typically included in a the counts file, and can be parse along with it.

.. ipython:: python

   file = '../demo/data/fake_data_lin.counts'
   counts, lins = ps.read_txt(file, lin=True)
   counts
   lins

See :ref:`io<read_txt>` for more information.

Alternatively, taxonomies can be parsed from a txt file containing only taxonomic information using the :func:`~pysurvey.Lineages.from_txt` method. The text file needs to be formatted as '[otu id]\\t[taxonomy]'. 

The keyword ``format`` sets the taxonomy format to be used, and the keyword ``n_skip`` sets the number of header lines to be ignored by the parser.

.. ipython:: python

   file = '../demo/data/fake_data.lins'
   lins = ps.Lineages.from_txt(file, n_skip=3)
   lins


Grouping by taxonomy 
--------------------

Grouping OTUs by their taxonomy is done using the `group_taxa` method. 
For OTUs that are unassigned at the desired level, the default behavior is to used the highest assigned level.

.. ipython:: python

   ps.group_taxa(counts,lins, 'p')
   ps.group_taxa(counts,lins, 's')

 
If the ``best`` keyword is set to ``False`` all OTUs that are unassigned at the desired level are grouped together. Note that this may result in grouping together OTUs from very diverse phylogenetic groups.    

.. ipython:: python

   ps.group_taxa(counts,lins, 's', best=False)


Misc. Examples 
---------------

.. ipython:: python

   # ids of OTUs that have an assigned taxonomy at given level
   lins.get_assigned('g')
   # ids of OTUs with a specific taxonomy at given level
   lins.get_ids('o', 'o.Bacteroidales')
   # Taxonomic assignment at given level
   lins.get_assignments('g')
   lins.get_assignments('g', best=True)


