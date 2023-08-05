# -*- python -*-
#
#  This file is part of the CNO software
#
#  Copyright (c) 2011-2012 - EBI
#
#  File author(s): CNO developers (cno-dev@ebi.ac.uk)
#
#  Distributed under the GPLv2 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-2.0.html
#
#  CNO website: http://www.ebi.ac.uk/saezrodriguez/software.html
#
##############################################################################
"""Provide a Python interface to CellNOptR (a R package).

::

    >>> from cellnopt.wrapper.wrapper_cnor import *
    >>> data = readMIDAS(file)

.. note:: All optional arguments are identical to the CellNOptR package but in lower case.

:Details:

In principle, all functions from CellNOptR can be called directly using RPY2::

    from rpy2.robjects.packages import importr
    rpack_CNOR = importr("CellNOptR")
    midas = rpack_CNOR.readMIDAS(file)

The returned object contains an attribute name
that can be useful to retrieve any fields. However, this require some
esoteric code. First, you need to know the name, then
you need to call the special function **rx2** as follows::

    cnodata.data.names
    Out[884]:
    <StrVector - Python:0xf4f30e0 / R:0x6641878>
    ['dataMatrix', 'TRcol', 'DAcol', 'DVcol']
    cnodata.rx2('DAcol')

This module ease the access to such fields thanks to a decorator::

    from cellnopt.wrapper.wrapper_cnor import readMIDAS
    midas = readMIDAS(file)
    midas.DAcol
    <FloatVector - Python:0x166bd638 / R:0x15f69f80>
    [5.000000, 6.000000, 7.000000, ..., 9.000000, 10.000000, 11.000000]

.. note:: the access to midas.DAcol is read-only. To write, you must use the
    rpy2 syntax

The :mod:`cellnopt.wrapper.wrapper_cnor` module provide a function for each
original CellNOptR (R package) functions.

Since the R package may change, the reader should consult the original R package
for up-to-date documentation. Nevertheless, if you use a Python shell, the
**??** signs returns the docstring of the functions that are just copy of the
original one (the R one). For developers, this feature is performed via a
decorator called :func:`~cellnopt.wrapper.wrapper_cnor.Rsetdoc` that fetches the R
documentation and replaces the __doc__ variable. Another decorator sets
attributes to the returned objects so that R variables (found in **names**) are
available as attributes (see :mod:`~cellnopt.wrapper.tools.Rnames2attributes`).

.. currentmodule::  cellnopt.wrapper.wrapper_cnor

Here below are the CellNOptR functions that can be called from  Python thanks to
the :mod:`cellnopt.wrapper.wrapper_cnor` module.

.. autosummary::

    cellnopt.wrapper.wrapper_dt.gaBinaryTimeScale


"""
__author__ = """\n""".join(['Thomas Cokelaer <cokelaer@ebi.ac.uk'])
__revision__ = "$Rev: 2565 $"

# Use Rnames2attributes decorator to ease the access to R names
from rtools import *

import os
# rpy2
from rpy2 import robjects
from rpy2.robjects.packages import importr
import tempfile
from pylab import imread, imshow
import rpy2.rinterface
from rpy2.robjects import NULL

try:
    rpack_CNORdt = RPackage("CNORdt", require="1.0.0").package
    #rgbl = load_Rpackage("RBGL") # required by CellNOptR
    __all__  = ['gaBinaryDT', 'computeScoreDT', 'cutAndPlotResultsDT', 'simulatorDT']
except:
    __all__ = []




def Rsetdoc(f):
    """Decorator that copy the R doc into the wrapped Python function.

    .. note:: function to be used for developers only as a decorator to
       R function.

    """
    name = f.__name__
    doc = buildDocString("CNORdt", name)
    if f.__doc__:
        f.__doc__ += doc
    else:
        f.__doc__ = doc
    return f


@Rsetdoc
@Rnames2attributes
def computeScoreDT(cnolist, model, bString, simlist=None, indexlist=None,
    sizeFac=1e-4, NAFac=1, boolUpdates=10, lowerB=0.8, upperB=10):


    return rpack_CNORdt.computeScoreDT(cnolist, model, bString,
        convertor(simlist), convertor(indexlist), sizeFac, NAFac, boolUpdates, 
        lowerB,upperB)[0] 



@Rsetdoc
@Rnames2attributes
def cutAndPlotResultsDT(cnolist, model, bString, simlist=None,
    indexlist=None,  plotPDF=False, tag=None, 
    plotParams={'maxrows':10}, boolUpdates=10,
    lowerB=.8, upperB=10,sizeFac = 1e-04, NAFac = 1):


    return rpack_CNORdt.cutAndPlotResultsDT(model, bString, convertor(simlist),
        cnolist, convertor(indexlist), plotPDF, convertor(tag), convertor(plotParams),
        boolUpdates, lowerB, upperB, sizeFac, NAFac)

@Rsetdoc
@Rnames2attributes
def gaBinaryDT(cnolist, model, initBstring=None, sizeFac=1e-4, NAFac=1, **kargs):
    initBstring = convertor(initBstring)

    popSize = kargs.get("popsize", 50)
    pMutation = kargs.get("pmutation", .5)
    maxTime = kargs.get("maxtime", 60)
    maxGens = kargs.get("maxgens", 500)
    stallGenMax = kargs.get("stallgenmax", 100)
    selPress = kargs.get("selpress", 1.2)
    elitism = kargs.get("elitism", 5)
    relTol = kargs.get("reltol", .1)
    verbose = kargs.get("verbose", True)
    priorBitString = convertor(kargs.get("priorBitString", None))
    maxSizeHashTable = kargs.get("maxSizeHashTable", 5000)
    boolUpdates = kargs.get("boolUpdates", 10)
    lowerB = kargs.get("lowerB", 0.8)
    upperB = kargs.get("upperB", 10)

    return rpack_CNORdt.gaBinaryDT(cnolist, model, initBstring=initBstring, sizeFac=sizeFac,
        NAFac=NAFac, popSize=popSize, pMutation=pMutation, maxTime=maxTime, maxGens=maxGens,
        stallGenMax=stallGenMax,  selPress=selPress, elitism=elitism, relTol=relTol,
        verbose=verbose, priorBitString=priorBitString,
        maxSizeHashTable=maxSizeHashTable, boolUpdates=boolUpdates, lowerB=lowerB,
        upperB=upperB)


@Rsetdoc
@Rnames2attributes
def simulatorDT(cnolist, model, simlist, indices, boolUpdates=10, prevSim=NULL):

    return rpack_CNORdt.simulatorDT(cnolist, model, simlist, indices,
        boolUpdates, prevSim=convertor(prevSim))
    






