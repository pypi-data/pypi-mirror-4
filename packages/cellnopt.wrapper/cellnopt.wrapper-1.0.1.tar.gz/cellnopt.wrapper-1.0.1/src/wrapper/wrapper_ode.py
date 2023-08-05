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
"""Wrapper to rpack_CNORode package. 

:Usage:

::

    >>> from cellnopt.wrapper.wrapper_ode import *
    >>> data = readMIDAS(file)

.. note:: All optional arguments are identical to the CNOR version but in lower case.

.. note:: some functions have been renamed

:Details:

All functions from CNOR can be called directory using RPY::

    from rpy2.robjects.packages import importr
    rpack_CNORode = importr("CNORode")
    midas = rpack_CNORode.readMIDAS(file)
    
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
#    #from cellnopt.wrapper.wrapper_cnor import *
#except:
#    from tools import *
#    #from wrapper_cnor import *

#import tools
#from tools import *
from rtools import *
# load CNOR package
try:
    rpack_CNORode = RPackage("CNORode", require="1.0.0").package

    __all__  = ['createLBodeContPars', 'plotLBodeFitness', 'parEstimationLBode',
    'defaultParametersSSm', 'defaultParametersGA', 'getLBodeContObjFunction', 
    'plotLBodeModelSim']
except:
    __all__  = []





def Rsetdoc(f):
    """Decorator that copy the R doc into the wrapped Python function.

    .. note:: function to be used for developers only as a decorator to
       R function.

    """
    name = f.__name__
    doc = buildDocString("CNORode", name)

    if f.__doc__:
        f.__doc__ += doc 
    else:
        f.__doc__ = doc 
    return f




@Rsetdoc
@Rnames2attributes
def createLBodeContPars(model, default_n=3, default_k=0.5, default_tau=1, 
        LB_n=1, UB_n=5, LB_k=0.1, UB_k=0.9,  LB_tau=0.01, UB_tau=10, 
        opt_n=True, opt_k=True, opt_tau=True, random=False):

    return rpack_CNORode.createLBodeContPars(model, 
        default_n=default_n, default_k=default_k, default_tau=default_tau,
        LB_n=LB_n, UB_n=UB_n, LB_k=LB_k, UB_k=UB_k,
        LB_tau=LB_tau, UB_tau=UB_tau, opt_n=opt_n, opt_k=opt_k, opt_tau=opt_tau,
        random=random)

@Rsetdoc
@Rnames2attributes
def defaultParametersGA():
    return rpack_CNORode.defaultParametersGA()

@Rsetdoc
@Rnames2attributes
def defaultParametersSSm():
    return rpack_CNORode.defaultParametersSSm()

@Rsetdoc
@Rnames2attributes
def plotLBodeFitness(cnolist, model, ode_parameters, indices, colormap="heat"):
    """TODO    adjMatrix=NULL,             time=1,
        verbose=0,                  transfer_function=3,        reltol=1e-4,
        atol=1e-3,                  maxStepSize=Inf,
maxNumSteps=100000,
        maxErrTestsFails=50,        plot_index_signals=NULL,
plot_index_experiments=NULL,
        plot_index_cues=NULL
    """
    return rpack_CNORode.plotLBodeFitness(cnolist, model, ode_parameters,
indices, colormap=colormap)

@Rsetdoc
@Rnames2attributes
def plotLBodeModelSim(cnolist, model, ode_parameters):
    """TODO   
  indices=NULL,               adjMatrix=NULL,             time=1,
    verbose=0,                  transfer_function=3,        reltol=1e-4,
     atol=1e-3,                  maxStepSize=Inf,  maxNumSteps=100000,
         maxErrTestsFails=50,        large=FALSE,                nsplit=4

    """
    return rpack_CNORode.plotLBodeModelSim(cnolist, model, ode_parameters)

@Rsetdoc
@Rnames2attributes
def parEstimationLBode(cnolist, model, method, ode_parameters, indices, params):
    if method == 'ga':
        return rpack_CNORode.parEstimationLBode(cnolist,model, method=method,
            ode_parameters=ode_parameters,indices=indices, paramsGA=params)
    elif method == 'essm':
        return rpack_CNORode.parEstimationLBode(cnolist,model, method="essm",
            ode_parameters=ode_parameters,indices=indices, paramsSSm=params)
    else:
        raise ValueError("method should be ga or ssm")

@Rsetdoc
@Rnames2attributes
def getLBodeContObjFunction(cnolist, model, ode_parameters, indices=None,
    time=1, verbose=False, transfer_function=3, reltol=0.0001, atol=0.001,
    maxStepSize=1e6, maxNumSteps = 1e5, maxErrTestsFails=50, nan_fac=1):

    if verbose == True:
        verbose = 1
    elif verbose == False:
        verbose = 0
    return rpack_CNORode.getLBodeContObjFunction(cnolist, model,
        ode_parameters,indices, time, verbose, transfer_function, reltol, atol,
        maxStepSize, maxNumSteps, maxErrTestsFails, nan_fac)



@Rsetdoc
@Rnames2attributes
def simulate(cnolist, model, ode_parameters):
    return rpack_CNORode.simulate(cnolist,model,ode_parameters)
