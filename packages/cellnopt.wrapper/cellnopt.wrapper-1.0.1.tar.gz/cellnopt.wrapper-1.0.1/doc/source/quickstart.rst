.. _quickstart:

Quick Start
#################

Getting some help
=================

Getting some help on a CellNOptR (and wrapped function in cellnopt.wrapper) is
easy:: 

    >>> from cellnopt.wrapper import cnohelp
    >>> cnohelp("readSIF")

Converting R script into Python
================================

R script using the functional approach of CellNOptR can be easily translated into Python script thanks to **cellnopt.wrapper**

First, make sure that CellNOptR and **cellnopt.wrapper** are installed (see :ref:`installation`). 

Import the entire package::

    >>> from cellnopt.wrapper import *

From now on, you should be able to call the CellNOptR functionalities. For
instance, to read a SIF or MIDAS files::

    >>> s = readSIF(get_data("ToyModelMKM.sif"))
    >>> m = readMIDAS(get_data("ToyModelMKM.csv"))

Those 2 files are provided with the package. 

The variable *s* is a R data.frame. In R, you would acces to the names of this
data frame using the $ sign: **s$names**. However, in Python, you type::

    >>> print s.names
    [1] "reacID"       "namesSpecies" "interMat"     "notMat"

.. warning:: this is a read-only access !! 

Then, once you know the name of a field, you can access to it as follows::

    >>> print s.namesSpecies
    [1] "EGF"    "TNFa"   "TRAF6"  "Jnk"    "p38"    "PI3K"   "Ras"    "Raf"   
    [9] "Akt"    "Mek"    "Erk"    "NFkB"   "cJun"   "Hsp27"  "p90RSK"

As a final illustration, we can use the plotModel function to plot the network::

    >>> plotModel(s, makeCNOlist(m, subfield=False))

.. image:: network.png
   :width: 30%


.. note:: All functions from CellNOptR are wrapped in :mod:`~cellnopt.wrapper.wrapper_cnor`. 

.. note:: The syntax is alsmost identical. Some names have been changed slightly and
    most of the user arguments are lower cases (instead of mixes of lower/upper cases in CellNOptR). 

You can use cellnopt.wrapper in a functional way copy and paste existing R script
and little edition. 


Another way is to use the classes written in cellnopt.wrapper.cnor module. Let us
consider the ToyModel data and model::


    from cellnopt.wrapper import get_data, CNORbool
    b = CNORbool(get_data("ToyModelT2.sif"), get_data("ToyModelT2.csv"))
    b.preprocessing() # compression/expansion/cutNONC species
    b.gaBinaryT1(popsize=5, maxgens=10)
    b.plotFit()
    b.cutAndPlotResultsT1()
        
    # best score is in b.T1opt.results

    # if you want T2 steady state analysis if you have the relevant data, carry
    # on by typing
    b.gaBinaryT2()
    b.cutAndPlotResultsT2()
    # best score is in b.T1opt.results






See the tutorial, references and CNOR tutorial for more helps.
