.. _install:

.. currentmodule:: survey

************
Installation
************

Currently, there is no installer for :mod:`survey`. 
To use, download the `source code <https://bitbucket.org/yonatanf/survey>`__ and manually add the source folder to the python path.

Python version support
~~~~~~~~~~~~~~~~~~~~~~

Python 2.5 to 2.7. Python 3 is not supported.


Dependencies
~~~~~~~~~~~~

  * `NumPy <http://www.numpy.org>`__: 1.5.1 or higher.
  * `pandas <http://pandas.sourceforge.net/index.html>`__ 0.3.0
  * `DataStructures <https://bitbucket.org/yonatanf/datastructures/overview>`__


Optional dependencies
~~~~~~~~~~~~~~~~~~~~~

  * `utilities <https://bitbucket.org/yonatanf/utilities/overview>`__: distances, MI, etc'
  * `scikits-learn <http://scikit-learn.org/0.10/index.html>`__: machine learning tool such as: Gaussian mixture models, etc'
  * `pycognet <http://pycogent.sourceforge.net/>`__: PCoA, rarefaction
  * `SciPy <http://www.scipy.org>`__: miscellaneous statistical functions and hierarchical clustering
  * `matplotlib <http://matplotlib.sourceforge.net/>`__ and `matplotlibX <https://bitbucket.org/yonatanf/matplotlibx/overview>`__ : for plotting
  * `rpy2 <http://rpy.sourceforge.net/rpy2/doc-2.1/html/index.html/>`__: for using R functions 

.. note::

   Without the optional dependencies, many useful features will not
   work. Hence, it is highly recommended that you install these. A packaged
   distribution like the `Enthought Python Distribution
   <http://enthought.com/products/epd.php>`__ may be worth considering.


