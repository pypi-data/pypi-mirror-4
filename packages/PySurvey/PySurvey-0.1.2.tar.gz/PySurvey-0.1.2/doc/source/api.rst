.. _api:

.. currentmodule:: pysurvey

*************
API Reference
*************

Metadata operations
-------------------

.. autosummary::
   :toctree: generated/

   drop_missing_meta   
   filter_by_meta
   sort_by_meta


Filtering
---------

.. autosummary::
   :toctree: generated/

   filter_by_vals   
   filter_by_meta
   keep


Data maifulation
----------------

.. autosummary::
   :toctree: generated/

   normalize   
   to_fractions
   to_binary
   rarefy

.. currentmodule:: pysurvey.core.compositional_methods

Compositional methods
---------------------

.. autosummary::
   :toctree: generated/

   alr   
   clr
   replace_zeros
   variation_mat

.. currentmodule:: pysurvey

Analysis methods
----------------

.. autosummary::
   :toctree: generated/

   PCoA
   basis_corr
   correlation
   discriminating_components
   dist_mat
   permute_w_replacement
   rank_abundance
   sample_diversity


File IO
-------

.. autosummary::
   :toctree: generated/

   read_txt
   write_txt


Lineages
--------

Data Structures
~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: generated/

   Lineage.__init__
   Lineages.__init__


IO
~~

.. autosummary::
   :toctree: generated/

   Lineages.from_dict
   Lineages.from_pickle
   Lineages.from_txt
   Lineages.to_pickle
   Lineages.to_txt


Lineage methods
~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: generated/

   group_taxa
   Lineage.get_assignment
   Lineages.get_assigned
   Lineages.get_assignments
   Lineages.get_ids
   Lineages.filter

