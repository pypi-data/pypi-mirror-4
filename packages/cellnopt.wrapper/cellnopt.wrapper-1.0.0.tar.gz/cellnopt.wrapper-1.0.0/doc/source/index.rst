

#############################
CNOLAB.WRAPPER documentation
#############################



Motivation 
###########

The package `cellnopt.wrapper <http://pypi.python.org/pypi/cellnopt.wrapper/>`_ provides 


 1. A Python interface to `CellNOptR <http://bioconductor.org/packages/release/bioc/html/CellNOptR.html>`_ and related add-ons (e.g. CNORode, CNORfuzzy). CellNOptR is a R package dedicated to Optimising Signalling Pathways to data (See `CellNOpt page <ihttp://www.cellnopt.org>`_) using boolean logic modelling.
 2. Ease test suite integration
 3. Enhance the user interface and data mining

.. _installation:

Installation
###################

prerequisites
===============

Of course, you will need to install `Python <http://www.python.org/download/>`_
(linux and mac users should have it installed already). 

We recommend also to install `ipython <http://ipython.org/>`_, which provides a more flexible shell alternative to the
python shell itself.

installation
================
Since **cellnopt.wrapper** is available on `PyPi <http://pypi.python.org/>`_, the following command should install the package and its dependencies automatically:: 

    easy_install cellnopt.wrapper

.. note:: easy_install you may need root permission (under linux, use sudo)

**cellnopt.wrapper** provides facilities to call CellNOptR package, which is a package
available on BioConductor. To install it, open a R session and type::

    source("http://bioconductor.org/biocLite.R")
    biocLite("CellNOptR")

Earlier and most recent versions are available on `CellNOpt page <http://www.cellopt.org>`_

known issues
===================

The installation should be smooth. However, the dependencies rpy2 requires R to
be installed. So, you will need to install R before hand. We recommend R version 2.15
which is the latests version. It is also compulsary if you want the latest
version of CellNOptR (1.2) from bioconductor.


In order to test if rpy2 is installed properly, run this code in a python
shell::

    import rpy2;
    from rpy2 import robjects; robjects.r("version")

If you get this kind of error::

    LookupError: 'show' not found

You may find a solution here `rpy2 and R compatibility <http://thomas-cokelaer.info/blog/2012/01/installing-rpy2-with-different-r-version-already-installed/>`_.

TODO
======

Some functions do not have a wrapper: plotCNOlistLarge, plotCNOlistLargePDF,
simulatorT1, getFit, simulatorT2, writeDot, simFuzzyT1, writeNetwork

User guide
##################


.. toctree::
    :maxdepth: 2
    :numbered:

    quickstart.rst
    tutorial.rst


References
##################


.. toctree::
    :maxdepth: 2
    :numbered:

    references
