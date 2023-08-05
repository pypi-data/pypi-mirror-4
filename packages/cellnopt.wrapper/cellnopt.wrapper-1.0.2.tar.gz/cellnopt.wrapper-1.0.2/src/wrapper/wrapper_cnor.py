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

    cellnopt.wrapper.wrapper_cnor.cutNONC
    cellnopt.wrapper.wrapper_cnor.compressModel
    cellnopt.wrapper.wrapper_cnor.computeScoreT1
    cellnopt.wrapper.wrapper_cnor.computeScoreTN
    cellnopt.wrapper.wrapper_cnor.checkSignals
    cellnopt.wrapper.wrapper_cnor.cutAndPlot
    cellnopt.wrapper.wrapper_cnor.cutAndPlotResultsT1
    cellnopt.wrapper.wrapper_cnor.cutAndPlotResultsT2
    cellnopt.wrapper.wrapper_cnor.expandGates
    cellnopt.wrapper.wrapper_cnor.findNONC
    cellnopt.wrapper.wrapper_cnor.gaBinaryT1
    cellnopt.wrapper.wrapper_cnor.gaBinaryTN
    cellnopt.wrapper.wrapper_cnor.indexFinder
    cellnopt.wrapper.wrapper_cnor.makeCNOlist
    cellnopt.wrapper.wrapper_cnor.normaliseCNOlist
    cellnopt.wrapper.wrapper_cnor.plotFit
    cellnopt.wrapper.wrapper_cnor.plotCNOlist
    cellnopt.wrapper.wrapper_cnor.plotCNOlistPDF
    cellnopt.wrapper.wrapper_cnor.plotModel
    cellnopt.wrapper.wrapper_cnor.prep4sim
    cellnopt.wrapper.wrapper_cnor.readMIDAS
    cellnopt.wrapper.wrapper_cnor.readSIF
    cellnopt.wrapper.wrapper_cnor.residualError
    cellnopt.wrapper.wrapper_cnor.preprocessing
    cellnopt.wrapper.wrapper_cnor.simulateTN
    cellnopt.wrapper.wrapper_cnor.writeScaffold
    cellnopt.wrapper.wrapper_cnor.writeNetwork
    cellnopt.wrapper.wrapper_cnor.writeMIDAS
    cellnopt.wrapper.wrapper_cnor.writeReport
    cellnopt.wrapper.wrapper_cnor.writeSIF

"""
__author__ = """\n""".join(['Thomas Cokelaer <cokelaer@ebi.ac.uk'])
__revision__ = "$Rev: 2611 $"

# Use Rnames2attributes decorator to ease the access to R names
from rtools import *

import os
# rpy2
from rpy2 import robjects
from rpy2.robjects.packages import importr
import tempfile
import rpy2.rinterface
from rpy2.robjects import NULL

try:
    rpack_CNOR = RPackage("CellNOptR", require="1.4.0").package
    #rgbl = load_Rpackage("RBGL") # required by CellNOptR
    __all__  = ['readSIF', 'readMIDAS', 'readMidas', 'makeCNOlist', 'readSif',
            'makeCNOlist', 'indexFinder', 'cutNONC', 'CNOlist',
            'compressModel', 'expandGates', 'residualError', 'prep4sim',
            'checkSignals', 'findNONC', 'plotFit', 'plotCNOlist',
            'preprocessing','simulateTN', 'CNORbool_R', 
            'plotCNOlistPDF', 'cutAndPlot', 'cutAndPlotResultsT1','cutAndPlotResultsT2',
            'gaBinaryT1', 'gaBinaryTN', 'normaliseCNOlist', 'writeScaffold',
            'writeNetwork', 'writeReport', 'computeScoreTN', 'writeMIDAS',
            'rpack_CNOR', 'initBstring','ga_options','plotModel','computeScoreT1', 'writeSIF']
except:
    __all__ = []



#: a test
ga_options = {'sizefac':0.0001,
              'nafac':1,
              'popsize':50,
              'maxtime':60,
              'pmutation':0.5,
              'maxgens':500,
              'stallgenmax':100,
              'selpress':1.2,
              'elitism':5,
              'reltol':0.1}


def Rsetdoc(f):
    """Decorator that copy the R doc into the wrapped Python function.

    .. note:: function to be used for developers only as a decorator to
       R function.

    """
    name = f.__name__
    doc = buildDocString("CellNOptR", name)
    if f.__doc__:
        f.__doc__ += doc
    else:
        f.__doc__ = doc
    return f


@Rsetdoc
@Rnames2attributes
def CNOlist(data, subfield=False, verbose=False):
    return rpack_CNOR.CNOlist(data, subfield, verbose)

@Rsetdoc
@Rnames2attributes
def writeMIDAS(cnolist, filename, timeIndices=None, overwrite=False):
    rpack_CNOR.writeMIDAS(cnolist, filename, convertor(timeIndices), overwrite)

@Rsetdoc
@Rnames2attributes
def writeSIF(model, filename):
    rpack_CNOR.writeSIF(model, filename)


@Rnames2attributes
def readSif(filename):
    import warnings
    warnings.warn("Deprecated function, use readSIF instead")
    return rpack_CNOR.readSIF(filename)

@Rsetdoc
@Rnames2attributes
def readSIF(filename):
    return rpack_CNOR.readSIF(filename)

@Rsetdoc
@Rnames2attributes
def readMIDAS(filename, verbose=True):
    return rpack_CNOR.readMIDAS(MIDASfile=filename,verbose=verbose)

@Rnames2attributes
def readMidas(filename, verbose=True):
    import warnings
    warnings.warn("Deprecated function, use readMIDAS instead")
    return rpack_CNOR.readMIDAS(MIDASfile=filename,verbose=verbose)


@Rsetdoc
@Rnames2attributes
def makeCNOlist(dataset, subfield=False, verbose=True, ):
    return rpack_CNOR.makeCNOlist(dataset=dataset, subfield=subfield, verbose=verbose)


@Rsetdoc
@Rnames2attributes
def indexFinder(cnolist, sif, verbose=True):
    return rpack_CNOR.indexFinder(cnolist, sif, verbose=verbose)


@Rsetdoc
@Rnames2attributes
def cutNONC(model, indices):
    return rpack_CNOR.cutNONC(model, indices)


@Rsetdoc
@Rnames2attributes
def compressModel(model, indices):
    return rpack_CNOR.compressModel(model, indices)


@Rsetdoc
@Rnames2attributes
def expandGates(model):
    return rpack_CNOR.expandGates(model, ignoreList=robjects.NA_Logical)


@Rsetdoc
@Rnames2attributes
def residualError(cnolist): # renamed to have consistent naming convention
    return rpack_CNOR.residualError(cnolist)

@Rsetdoc
@Rnames2attributes
def prep4sim(model):
    return rpack_CNOR.prep4sim(model)


@Rsetdoc
# no need for the Rnames2attributes decorator checkSignals return NULL
def checkSignals(cnolist, sif):
    # this function returns nothing some, this is just a call (no return)
    rpack_CNOR.checkSignals(cnolist, sif)


@Rsetdoc
# return a list (no names to be extracted so no need for the decorators)
def findNONC(model, indices, verbose=True):
    return rpack_CNOR.findNONC(model, indices, verbose=verbose)


@Rsetdoc
#no need for a decorator, just plot the results
def plotFit(data, pdf=False, filename=NULL):
    rpack_CNOR.plotFit(optRes=data, filename=filename)


@Rsetdoc
#no need for a decorator, just plot the results
def plotCNOlist(data, show=True, filename=None):
    from rtools import Rplot
    rp = Rplot(show=show, filename=filename)
    rp._start()
    rpack_CNOR.plotCNOlist(data)
    rp._end()


@Rsetdoc
#no need for a decorator, just plot the results
def plotCNOlistPDF(cnolist=None, filename=None):
    rpack_CNOR.plotCNOlistPDF(cnolist, filename)


def get_temp_name():
    # just to get a name
    tmp = tempfile.NamedTemporaryFile(suffix=".png")
    name = tmp.name
    tmp.close()
    return name


def cutAndPlot(cnolist, model, bStrings, show=True, filename=None):

    from rtools import Rplot
    rp = Rplot(show=show, filename=filename)
    rp._start()
    rp.pythoncode("from cellnopt import *; rpack_CNOR.cutAndPlot(cnolist, model, bStrings)")
    rp._end()



@Rsetdoc
#no need for a decorator, just plot the results
def cutAndPlotResultsT1(model=None, bString=None, plotpdf=True,
                        cnolist=None, tag=NULL,  showR=False):
    if isinstance(bString, list) == True:
        bString = robjects.IntVector(bString)

    if showR==False:
        grdevices = importr('grDevices')
        name = get_temp_name()
        grdevices.png(file=name, width=1024, height=1024)
    # this function returns nothing some, this is just a call (no return)
    rpack_CNOR.cutAndPlotResultsT1(model=model, bString=bString,
                             CNOlist=cnolist, plotPDF=plotpdf,
                             tag=tag)
    if showR==False:
        try:
            from pylab import imread, imshow
        except ImportError, e:
            print(e)
            print("install pylab to use the showR==False option")
        grdevices.dev_off()
        imshow(imread(name))
        os.remove(name)

@Rsetdoc
#no need for a decorator, just plot the results
def cutAndPlotResultsT2(model=None, bStringT1=None, bStringT2=None,
                        plotpdf=True, simlist=None, indexlist=None,
                        cnolist=None, tag=NULL):
    if isinstance(bStringT1, list) == True:
        bStringT1 = robjects.IntVector(bStringT1)
    if isinstance(bStringT2, list) == True:
        bStringT2 = robjects.IntVector(bStringT2)

    rpack_CNOR.cutAndPlotResultsT2(model=model,
                                    bStringT1=bStringT1,
                                    bStringT2=bStringT2,
                                    CNOlist=cnolist,
                                    plotPDF=plotpdf,
                                    tag=tag)

@Rsetdoc
@Rnames2attributes
def CNORbool_R(cnolist, model):
    return rpack_CNOR.CNORbool(cnolist, model)

@Rsetdoc
@Rnames2attributes
def gaBinaryT1(cnolist=None, model=None,  initbstring=None,
               sizefac=ga_options['sizefac'], nafac=ga_options['nafac'],
               popsize=ga_options['popsize'], maxtime=ga_options['maxtime'],
               pmutation=ga_options['pmutation'], maxgens=ga_options['maxgens'],
               stallgenmax=ga_options['stallgenmax'], selpress=ga_options['selpress'],
               elitism=ga_options['elitism'], reltol=ga_options['reltol'], verbose=False):
    # the original code is not consistent with the naming convention
    # need to fix it e meanwhile, this wrapper takes care of it
    if isinstance(initbstring, list) == True:
        initbstring = robjects.IntVector(initbstring)
    assert popsize > elitism, "popsize must be > than elitism"
    return rpack_CNOR.gaBinaryT1(CNOlist=cnolist,
                           model=model,
                           initBstring=initbstring,
                           sizeFac=sizefac,
                           NAFac=nafac,
                           popSize=popsize,
                           maxTime=maxtime,
                           pMutation=pmutation,
                           maxGens=maxgens,
                           stallGenMax=stallgenmax,
                           selPress=selpress,
                           elitism=elitism,
                           relTol=reltol,
                           verbose=verbose)


@Rsetdoc
@Rnames2attributes
def gaBinaryTN(cnolist=None, model=None, bstrings=None, 
               sizefac=ga_options['sizefac'], nafac=ga_options['nafac'],
               popsize=ga_options['popsize'], maxtime=ga_options['maxtime'],
               pmutation=ga_options['pmutation'], maxgens=ga_options['maxgens'],
               stallgenmax=ga_options['stallgenmax'], selpress=ga_options['selpress'],
               elitism=ga_options['elitism'], reltol=ga_options['reltol'], verbose=False):
    # the original code is not consistent with the naming convention
    # need to fix it e meanwhile, this wrapper takes care of it
    if isinstance(bstringT1, list) == True:
        bstringT1 = robjects.IntVector(initbstringT1)
    assert popsize > elitism, "popsize must be > than elitism"
    return rpack_CNOR.gaBinaryTN(CNOlist=cnolist,
                           model=model,
                           bStrings=bstrings,
                           sizeFac=sizefac,
                           NAFac=nafac,
                           popSize=popsize,
                           maxTime=maxtime,
                           pMutation=pmutation,
                           maxGens=maxgens,
                           stallGenMax=stallgenmax,
                           selPress=selpress,
                           elitism=elitism,
                           relTol=reltol,
                           verbose=verbose)


@Rsetdoc
@Rnames2attributes
def normaliseCNOlist(cnolist, EC50Data=0.5,hillCoef=2,EC50Noise=0.1,
                     detection=0,saturation=None,
                     changeTh=0,norm2TorCtrl="time"):

    #todo saturation default values must be inf
    return rpack_CNOR.normaliseCNOlist(cnolist, EC50Data=EC50Data,
                                 HillCoef=hillCoef,
                                 EC50Noise=EC50Noise,
                                 detection=detection,
                                 changeTh=changeTh,
                                 norm2TorCtrl=norm2TorCtrl
                                 )

@Rsetdoc
#no need for a decorator, just plot the results
def writeScaffold(cnolist=None, modelcomprexpanded=None, optimrest1=None,
                  optimrest2=None, tag=NULL, modeloriginal=None):
    if optimrest1 == None:
        optimrest1 = robjects.NA_Logical
    if optimrest2 == None:
        optimrest2 = robjects.NA_Logical

    return rpack_CNOR.writeScaffold(modelComprExpanded=modelcomprexpanded,
                optimResT1=optimrest1, optimResT2=optimrest2,
                modelOriginal=modeloriginal, CNOlist=cnolist,  tag=tag)


#no need for a decorator, just plot the results
@Rsetdoc
def writeNetwork(cnolist=None, modelcomprexpanded=None, optimrest1=None,
                 optimrest2=None, tag=NULL,
                 modeloriginal=None):


    if optimrest2 == None:
        optimrest2 = robjects.NA_Logical

    return rpack_CNOR.writeNetwork(modelOriginal=modeloriginal,
                             modelComprExpanded=modelcomprexpanded,
                             optimResT1=optimrest1,
                             optimResT2=optimrest2,
                             CNOlist=cnolist,
                             tag=tag)


# no need for a decorator, just for writting results
@Rsetdoc
def writeReport(modeloriginal=None, modelopt=None, optimrest1=None,
                optimrest2=None, cnolist=None ,
                namesfiles=None, namesdata=None,
                directory="test", rese=None):
    """Write a report of a CNO analysis

    :param namesdata: must be a dictionary {'CNOlist':name1, 'model':name2}
    :param namesfiles: must be a dictionary with the following keys
        'dataPlot', 'evolFitT1', 'evolFitT2', 'simResultsT1', 'simResultsT2',
        'scaffold', 'scaffoldDot', 'tscaffold', 'wscaffold', 'PKN',
        'PKNdot','wPKN', 'nPKN'

    :Original documentation:
    """
    if optimrest2 == None:
        optimrest2 = robjects.NA_Logical

    # namesdata must be compatible with R
    assert isinstance(namesdata, dict)
    assert sorted(namesdata.keys()) == sorted(['CNOlist','model'])
    namesdata = robjects.ListVector(namesdata)

    #namesfiles must be compatible with R
    assert sorted(namesfiles.keys()) == sorted([
                                'dataPlot', 'evolFitT1','evolFitT2',
                                 'simResultsT1', 'simResultsT2', 'scaffold',
                                 'scaffoldDot', 'tscaffold', 'wscaffold',
                                 'PKN', 'PKNdot', 'wPKN', 'nPKN'])
    for k in namesfiles.keys():
        if namesfiles[k] ==None:
            namesfiles[k] = robjects.NA_Logical
    namesfiles = robjects.ListVector(namesfiles)

    if optimrest1 == None:
        optimrest1 = robjects.NULL

    return rpack_CNOR.writeReport(modelOriginal=modeloriginal,
            modelOpt=modelopt, optimResT1=optimrest1, optimResT2=optimrest2,
            CNOlist=cnolist, directory=directory,
            namesFiles=namesfiles,
            namesData=namesdata,
            resE = rese)

#@Rsetdoc
@Rnames2attributes
def simulateT2(cnolist, model, bstringt1):
    raise DeprecatedWarning("use simulateTN instead")



#@Rsetdoc
@Rnames2attributes
def simulateTN(cnolist, model, bstrings):
    if isinstance(bstrings, list) == True:
        for x in bstrings:
            assert isinstance(x, list)
        bstrings = robjects.Vector([robjects.IntVector(x) for x in bstrings])
    else:
        raise TypeError("bStrings must be a list of list")
    return rpack_CNOR.simulateTN(CNOlist=cnolist, model=model,  bStrings=bstrings)



def computeScoreT1(cnolist=None, model=None, bstring=None, simlist=None,
    indexlist=None, sizeFac=0.0001, NAFac=1):

    if isinstance(bstring, list) == True:
        bstring = robjects.IntVector(bstring)
    else:
        # todo: check that if not a list, it is a R list
        pass

    simlist = convertor(simlist)
    indexlist = convertor(indexlist)
    #return rpack_CNOR.computeScoreT1_2(CNOlist=cnolist, model=model,
    #     bString=bstring, simList=simlist, indexList=indexlist, sizeFac=sizeFac, NAFac=NAFac)[0]
    return rpack_CNOR.computeScoreT1(CNOlist=cnolist, model=model,
         bString=bstring, simList=simlist, indexList=indexlist, sizeFac=sizeFac, NAFac=NAFac)[0]


def computeScoreT2(*args, **kargs):
    raise DeprecatedWarning("computeScoreT2 is deprecated use computeScoreTN instead")


def computeScoreTN(cnolist=None, model=None, bstrings=None, sizeFac=0.0001, NAFac=1):

    if isinstance(bstrings, list) == True:
        for x in bstrings:
            assert isinstance(x, list)
        bstrings = robjects.Vector([robjects.IntVector(x) for x in bstrings])
    else:
        raise TypeError("bStrings must be a list of list")

    return rpack_CNOR.computeScoreTN(cnolist, model, NULL, 
        NULL, NULL, NULL, NULL, NULL, sizeFac, NAFac, bstrings)[0]


# the following is not part of CNO but ease its integration
def initBstring(reacID):
    """build up string made of 1 with a length equal to the reacID length

    :param list reacID: list of reactions

    Function used by the GA algorithm.

    ::

        >>> l = initBstring(['a', 'b'])
        [1, 1]

    """
    l = len(reacID)
    return robjects.IntVector([1] * l)


@Rsetdoc
@Rnames2attributes
def plotModel(model, cnolist=None, stimuli=None, signals=None, inhibitors=None,
    compressed=None, output=None, filename=None, bString=None, indexIntegr=None,
    remove_dot=True, graphvizParams=None):
    """model is a sif filename, cnolist is optional"""

    cnolist = convertor(cnolist)
    filename = convertor(filename)

    if output == None:
         output = "STDOUT"

    bString = convertor(bString)
    indexIntegr = convertor(indexIntegr)

    stimuli = convertor(stimuli)
    signals = convertor(signals)
    inhibitors = convertor(inhibitors)
    compressed = convertor(compressed)
    graphvizParams = convertor(graphvizParams)

    return rpack_CNOR.plotModel(model=model, CNOlist=cnolist, stimuli=stimuli,
        compressed=compressed, signals=signals,
        inhibitors=inhibitors,output=output,bString=bString,
        filename=filename, indexIntegr=indexIntegr, remove_dot=remove_dot,
graphvizParams=graphvizParams)



@Rsetdoc
@Rnames2attributes
def preprocessing(cnolist, model, cutNONC=True, compression=True,
    expansion=True, ignoreList=None, maxInputsPerGate=2, verbose=True):

    cnolist = convertor(cnolist)
    if ignoreList==None:
        ignoreList=robjects.NA_Logical
    return rpack_CNOR.preprocessing(cnolist, model, cutNONC=cutNONC,
        compression=compression, expansion=expansion, ignoreList=ignoreList,
        verbose=verbose, maxInputsPerGate=maxInputsPerGate)

