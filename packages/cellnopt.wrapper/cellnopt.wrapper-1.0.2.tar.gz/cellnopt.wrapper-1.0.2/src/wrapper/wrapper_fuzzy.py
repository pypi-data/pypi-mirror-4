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
"""Wrapper to CNORfuzzy package. 

:Usage:

::

    >>> from cellnopt.wrapper.wrapper_fuzzy import *
    >>> data = readMIDAS(file)

.. note:: All optional arguments are identical to the CNOR version but in lower case.

.. note:: some functions have been renamed

:Details:

All functions from CNOR can be called directory using RPY::

    from rpy2.robjects.packages import importr
    CNOR = importr("CNORfuzzy")
    midas = CNOR.readMIDAS(file)
    
When using a function from cno.cnor, you call the function with the same name 
from the R package called CellNOptR. 

The object returned by the CNOR functions contains an attributes names
that can be useful to retrieve any fields. However, this require some 
esoteric code. First, you need to know the name, then
you need to call the special function **rx2** as follows::

    cnodata.data.names
    Out[884]: 
    <StrVector - Python:0xf4f30e0 / R:0x6641878>
    ['dataMatrix', 'TRcol', 'DAcol', 'DVcol']
    cnodata.rx2('DAcol')

    
This module ease the access to such fields thanks to a decorator::

    from cnor import readMIDAS
    midas = readMIDAS(file)
    midas.DAcol
    <FloatVector - Python:0x166bd638 / R:0x15f69f80>
    [5.000000, 6.000000, 7.000000, ..., 9.000000, 10.000000, 11.000000]

"""
__author__ = """\n""".join(['Thomas Cokelaer <cokelaer@ebi.ac.uk'])
__revision__ = "$Rev: 2565 $"

import logging
logging.basicConfig(level=logging.ERROR)
import os
import rpy2.rinterface
from rpy2 import robjects


# Use Rnames2attributes decorator to ease the access to R names
#try:
#    from cellnopt.wrapper.tools import *
#except:
from rtools import *

# load CNOR package
try:
    rpack_CNORfuzzy = RPackage("CNORfuzzy", fuzzy="1.0.0").package
    __all__  = [ 'interpretDiscreteGA', 'CNORwrapFuzzy',
        'compileMultiRes', 'plotMeanFuzzyFit', 'defaultParametersFuzzy',
        'prep4simFuzzy', 'gaDiscreteT1', 'intStringFuzzy', 'reduceFuzzy',
        'getRefinedModel', 'writeFuzzyNetwork']
except:
    __all_ = []



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
    doc = buildDocString("CNORfuzzy", name)
        
    if f.__doc__:
        f.__doc__ += doc 
    else:
        f.__doc__ = doc 
    return f




@Rsetdoc
@Rnames2attributes
def prep4simFuzzy(model, params, verbose=False):
    return rpack_CNORfuzzy.prep4simFuzzy(model=model, paramsList=params,verbose=verbose)

@Rsetdoc
@Rnames2attributes
def defaultParametersFuzzy(cnolist=robjects.NA_Logical, model=robjects.NA_Logical):
    return rpack_CNORfuzzy.defaultParametersFuzzy(cnolist, model)

@Rsetdoc
@Rnames2attributes
def CNORwrapFuzzy(cnolist, model, params=robjects.NA_Logical, verbose=False):
    return rpack_CNORfuzzy.CNORwrapFuzzy(data=cnolist,model=model,
paramsList=params, verbose=verbose)

@Rsetdoc
@Rnames2attributes
def compileMultiRes(allRes, tag=robjects.NULL, show=True):
    return rpack_CNORfuzzy.compileMultiRes(allRes, tag, show)

@Rsetdoc
@Rnames2attributes
def plotMeanFuzzyFit(postRefThresh, allFinalMSEs, allRes,
    plotPDF=False,tag=robjects.NULL,show=True):
    return rpack_CNORfuzzy.plotMeanFuzzyFit(postRefThresh, allFinalMSEs, allRes, plotPDF, tag, show)

@Rsetdoc
@Rnames2attributes
def writeFuzzyNetwork(postrefthresh, allfinalmses, allres,
        tag=robjects.NULL,verbose=False):
    return rpack_CNORfuzzy.writeFuzzyNetwork(postRefThresh=postrefthresh,
        allFinalMSEs=allfinalmses,  allRes=allres,  tag=tag,verbose=verbose)


@Rsetdoc
@Rnames2attributes
def gaDiscreteT1(cnolist, model, simlist,
    indexlist,paramslist,initbstring=None, 
               sizefac=ga_options['sizefac'], nafac=ga_options['nafac'],
               popsize=ga_options['popsize'], maxtime=ga_options['maxtime'], 
               pmutation=ga_options['pmutation'], maxgens=ga_options['maxgens'], 
               stallgenmax=ga_options['stallgenmax'],selpress=ga_options['selpress'], 
               elitism=ga_options['elitism'], reltol=ga_options['reltol'],verbose=False):
    assert popsize >= elitism, "popsize must be > than elitism" 
    if initbstring == None:
        initbstring = initStringFuzzy(params, simlist) 
    return rpack_CNORfuzzy.gaDiscreteT1(CNOlist=cnolist, model=model, 
                           simList=simlist, 
                           indexList=indexlist, 
                           paramsList = paramslist,
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
                           selTol=reltol,
                           verbose=verbose)

@Rsetdoc
@Rnames2attributes
def interpretDiscreteGA(model, simlist, paramslist, intstring):
    return rpack_CNORfuzzy.interpretDiscreteGA(model=model,simList=simlist,
            paramsList=paramslist,intString=intstring)

@Rsetdoc
@Rnames2attributes
def getRefinedModel(res, cnolist, cutmodel, cutsimlist, indexlist, refparams):
    return rpack_CNORfuzzy.getRefinedModel(res=res, CNOlist=cnolist, cutModel=cutmodel,
        cutSimList=cutsimlist, indexList=indexlist, refParams=refparams)

@Rsetdoc
@Rnames2attributes
def reduceFuzzy(firstcutoff, cnolist, model, simlist, res, params, indexlist):
    return rpack_CNORfuzzy.reduceFuzzy(firstCutOff=firstcutoff, CNOlist=cnolist,
        model=model, simList=simlist, res=res, params=params,
        indexList=indexlist)






def intStringFuzzy(params, simlist):
    """build up Bstring for the fuzzy logic case

    :param list params: fuzzy logic parameter object (uses Type2Funs, Type1Funs
and params.Type2Funs)

    ::

        >>> l = initBstringFuzzy(params, simlist)
        [1, 1]

    """
    from numpy import random
    l = simlist.numType1[0] + simlist.numType2[0]
    data = random.randint(params.Type2Funs.dim[0], size=l)
    return robjects.IntVector(data)

