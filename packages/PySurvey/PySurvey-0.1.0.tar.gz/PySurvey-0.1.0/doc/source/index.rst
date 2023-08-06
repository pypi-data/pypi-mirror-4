.. survey documentation master file, created by
   sphinx-quickstart on Thu Aug  4 17:46:29 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to survey's documentation!
==================================

:mod:`survey` is a `Python <http://www.python.org>`__ package designed to perform interactive analysis of survey data, 
composed of counts of occurrence of different categories in a collection of samples. 
Specifically, :mod:`survey` is developed in the context of genomic surveys, such as 16S surveys, where one studies the occurrence of OTUs across samples.
Though much of :mod:`survey`'s functionality is not unique to survey data, and equivalent features are implemented in many other packages, :mod:`survey` is intended to serve as a 'one-stop-shop', and thus attempts to includes all the methods that are commonly used in the analysis of survey data (often by wrapping around other packages), with a sensible choice of default parameters (e.g. distance metrics, etc').

Here are just a few of :mod:`survey`'s features:
  - General utility:
	- All the features of the extremely useful `pandas <http://pandas.sourceforge.net/index.html>`__ package, which supports **fast** operations on labeled arrays (and much more).
	- Filtering of samples/components.
	- ML and Bayesian estimation of component fractions.
  

  - Exploratory analysis:
	- Dimension reduction: PCoA, PCA.
	- Clustering: hierarchical, c-means, GMM.
	- Compositional correlations via `SparCC <https://bitbucket.org/yonatanf/sparcc>`__.
	- Plotting: sorted heatmaps, stacked plots, grouped bar plots, ...
  
  - Ecological theory:
  	- Compute various measures of sample diversity (alpha diversity).	
	- Rarefaction.
  	- Rank abundance plots.
  	- Relative Species abundance plots. 



  	
Contents:

.. toctree::
   :maxdepth: 2
   
   install
   basics
   plotting
   phylo
   surveymatrix
   lineages
   diversity

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Please post comments or questions at https://bitbucket.org/yonatanf/survey/issues.