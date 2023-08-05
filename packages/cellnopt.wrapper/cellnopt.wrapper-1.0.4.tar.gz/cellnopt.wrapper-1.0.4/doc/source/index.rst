###############################
CELLNOPT.WRAPPER documentation
###############################



Motivation 
###########

The package `cellnopt.wrapper <http://pypi.python.org/pypi/cellnopt.wrapper/>`_ provides 


 1. A Python interface to `CellNOptR <http://bioconductor.org/packages/release/bioc/html/CellNOptR.html>`_ and related add-ons (e.g. CNORode, CNORfuzzy). CellNOptR is a R package dedicated to the Optimisation of Signalling Pathways to data (See `CellNOpt page <ihttp://www.cellnopt.org>`_). In particular, it uses boolean logic modelling but other formalisms (e.g. ODE) are available.
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

**cellnopt.wrapper** is available on `PyPi <http://pypi.python.org/>`_. The following command should install the package and its dependencies automatically:: 

    easy_install cellnopt.wrapper

.. note:: easy_install you may need root permission (under linux, use sudo)

**cellnopt.wrapper** provides facilities to call CellNOptR package, which is a R package
available on BioConductor. If CellNOptR is not installed on your system, then
the first time that you import **cellnopt.wrapper** in a Python shell, it will
download and install the R package automatically. The version downloaded will
depend on the version of **cellnopt.wrapper**. For instance in version 1.0.3,
CellNOptR 1.4.0 will be installed. If you want a newer version, you can install
it yourself as follows. First, open a R session. Then simply type::

    source("http://bioconductor.org/biocLite.R")
    biocLite("CellNOptR")

Recent versions of CellNOptR are available on `CellNOpt page <http://www.cellopt.org>`_ in the download section.

known issues
===================

The installation should be smooth. However, the dependencies rpy2 requires R to
be installed. So, you will need to install R before hand. We recommend R version 2.15
which is the latest version. It is also compulsary if you want the latest
version of CellNOptR (1.4) from bioconductor.


In order to test if rpy2 is installed properly, run this code in a python
shell::

    import rpy2;
    from rpy2 import robjects; robjects.r("version")

If you get this kind of error::

    LookupError: 'show' not found

You may find a solution here `rpy2 and R compatibility <http://thomas-cokelaer.info/blog/2012/01/installing-rpy2-with-different-r-version-already-installed/>`_.


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

Changes
===========

.. toctree::
    :maxdepth: 1

    ChangeLog
