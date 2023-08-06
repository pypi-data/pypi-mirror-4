.. PySurvey documentation master file, created by
   sphinx-quickstart on Thu Aug  4 17:46:29 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PySurvey: Interactive analysis of survey data
==============================================

**Version**: |version|
**Date**: |today| 

:mod:`PySurvey` is a `Python <http://www.python.org>`__ package designed to perform interactive analysis of survey data, 
composed of counts of occurrence of different categories in a collection of samples. 
Specifically, :mod:`PySurvey` is developed in the context of genomic surveys, such as 16S surveys, where one studies the occurrence of OTUs across samples.
Though much of :mod:`PySurvey`'s functionality is not unique to survey data, and equivalent features are implemented in many other packages, :mod:`PySurvey` is intended to serve as a 'one-stop-shop', and thus attempts to includes all the methods that are commonly used in the analysis of genomic survey data (often by wrapping around other packages), with a sensible choice of default parameters (e.g. distance metrics, etc').

:mod:`PySurvey` is based on the powerful `pandas <http://pandas.pydata.org/>`__ package which offers rich data structures which are 
tailored and optimized for interactive analysis of large data tables.

--------------------------
``PySurvey`` Resources
--------------------------
- **Documentation:** http://yonatanfriedman.com/docs/survey/index.html
- **Source Repository:** https://bitbucket.org/yonatanf/pysurve

--------------------------
Key Features
--------------------------
  - General utility:
	- Metadata support.
	- Filtering of samples/components.
	- ML and Bayesian estimation of component fractions.

  - Exploratory analysis:
	- Dimension reduction: PCoA.
	- Clustering: hierarchical, gaussian mixture models GMM.
	- Compositional correlations via `SparCC <https://bitbucket.org/yonatanf/sparcc>`__.
	- Plotting: sorted heatmaps, stacked plots, ...
  
  - Ecological theory:
  	- Sample diversities (alpha diversity).	
	- Rarefaction.
  	- Rank abundance plots. 


  	
Contents:

.. toctree::
   :maxdepth: 2
   
   install
   basics
   analysis
   metadata
   filter
   diversity
   phylo
   io
   plotting
   api


Please post comments or questions at https://bitbucket.org/yonatanf/PySurvey/issues.