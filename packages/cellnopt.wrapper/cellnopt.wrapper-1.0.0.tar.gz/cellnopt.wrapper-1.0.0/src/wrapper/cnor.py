# -* python -*-
#
#  This file is part of the CNO software
#
#  Copyright (c) 2011-2012 - EBI
#
#  File author(s): Thomas Cokelaer <cokelaer@ebi.ac.uk>
#
#  Distributed under the GPLv2 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-2.0.html
#
#  CNO website: http://www.ebi.ac.uk/saezrodriguez/software.html
#
##############################################################################
# $Id: cnor.py 2565 2012-10-17 13:29:07Z cokelaer $
"""Provide a class to run CellNOptR from a Python interface

Most of the functions from CellNoptR are available directly (thanks to
the module :mod:`cno.wrapper` that is imported when importing this module)::

    >>> from cno.cnor import readMIDAS, locate_data
    >>> filename = locate_data('MIDAS-Training-ToyModelMKM.csv')
    >>> data = readMIDAS(filename)

The object returned by the original R functions can then be manipulated in
Python::

    data.DAcol
    <FloatVector - Python:0x166bd638 / R:0x15f69f80>
    [5.000000, 6.000000, 7.000000, ..., 9.000000, 10.000000, 11.000000]
    l = list(data.Col)

Note, however, that high-level functions such as CNORbool are not available.
The reason being that, Python can provide such a functionality using object
oriented class. Therefore, in addition to the wrapped functions, this module
provides a class :class:`CNORbool` that ease the usage of the CNOR functions
by assembling them into an object oriented class. The main interest being that methods do not
need to be feeded with arguments. Everything is taken care of within the
object.

.. autosummary::
    CNORbool

"""
import os
import copy
import time
from os.path import join as pj

from rpy2 import robjects
from rpy2.robjects import NULL

try:
    from cellnopt.wrapper.wrapper_cnor import *
except:
    pass

try:
    from cellnopt.wrapper import wrapper_ode
except:
    pass

try:
    from cellnopt.wrapper import wrapper_fuzzy
except:
    pass

try:
    from cellnopt.wrapper.tools import require
except:
    from tools import require

try:
    from cellnopt.wrapper import wrapper_dt
except:
    pass


__all__ = ["CNORdt", "CNORbool", "CNORode", "CNORfuzzy", "closeR", "pyplotModel"]

class CNORBase(object):
    """A Base class for CNOR classes"""

    def __init__(self, model, data=None, cnolist=None, verbose=False, debug=True):

        self._verbose = verbose
        self.debug = debug
        self.width = 10 # R dev size
        self.height = 10 #R dev size

        if isinstance(model, str):
            self._model_filename = model
            self._model = readSIF(self._model_filename)
        else:
            self._model = model

        if isinstance(data, str):
            self._data_filename = data
            self._data = readMIDAS(self._data_filename, verbose=verbose)
        elif data != None:
            self._data = data

        # here, data must have been set or then cnolist will be provided, so let
        # us check that if midas is None, cnolist is not
        if data == None and cnolist==None:
            raise ValueError("at least one of midas or cnolist argument must be provided. ")

        # if cnolist is none, it means that data was provided
        if cnolist == None:
            self._cnolist = makeCNOlist(self.data, verbose=self.verbose)
        else:
            self._cnolist = cnolist

        self._checkSignals()

    def _get_data(self):
        return self._data
    data = property(_get_data, doc="return the data object (Midas object)")

    def _get_model(self):
        return self._model
    model = property(_get_model, doc="return the PKN model")

    def _get_cnolist(self):
        return self._cnolist
    cnolist = property(_get_cnolist, doc="return the cnolist object")

    def _get_data_filename(self):
        return self._data_filename
    data_filename = property(_get_data_filename, doc="return the data filename")

    def _get_model_filename(self):
        return self._model_filename
    model_filename = property(_get_model_filename, doc="return the model filename")

    def _get_reacID(self):
        return self.model.rx2('reacID')
    reacID = property(_get_reacID)

    def _get_verbose(self):
        return self._verbose
    def _set_verbose(self, value):
        if isinstance(value, bool):
            self._verbose = value
        else:
            raise ValueError("verbose is a bool (only True/False accepted)")
    verbose = property(_get_verbose, _set_verbose, doc="switch verbose option on/off")

    def _checkSignals(self):
        checkSignals(self.cnolist, self.model)

    def preprocessing(self, expansion=True, compression=True, cutNONC=True):
        from cellnopt.wrapper.wrapper_cnor import preprocessing
        expmodel = preprocessing(self.cnolist, self.model, cutNONC=cutNONC,
            expansion=expansion,  compression=compression, verbose=self.verbose)
        self.expmodel = expmodel

    def plotPKNModel(self, **kargs):
        plotModel(self.model, self.cnolist, **kargs)

    def plotModel(self, **kargs):
        plotModel(self.expmodel, self.cnolist, **kargs)

    def closeRdev(self):
        robjects.r("dev.off()")
    def resizeRdev(self, width, height):
        raise NotImplementedError
    def newRdev(self):
        robjects.r("dev.new(width=%s, height=%s)" % (self.width, self.height))

    def plotCNO(self):
        plotCNOlist(self.cnolist)

    def plotCNOlist(self):
        plotCNOlist(self.cnolist)


def _Rplot(f):
    def wrapper(*args, **kargs) :
        #args[0] stands for self
        args[0].newRdev()
        res = f(*args, **kargs)
        return res
    return wrapper


class CNORbool(CNORBase):
    """Class to wrap CellNoptR functions (based on R_time_course example)

    :Usage:

    ::

        # Reading the input data, creating the CNOlist, and calling checkSignals and indexFinder.
        t = cnor.CNORbool('ToyModelMKM.sif', 'MIDAS-Training-ToyModelMKM.csv',
            path='share/data', verbose=True)

        # you can then plot the CNOlist
        t.plotCNO()

        # pre processing is required (cuts, compression/expansion)
        t.preprocessing()

        ## run the GA algorithm
        t.gaBinaryT1()

        # then plotting and writting the results
        t.cutAndPlotResultsT1()
        t.writeScaffold()
        t.writeNetwork()
        t.writeReport()

    Alternatively, there are aliases method that can be used::

        t = cnor.CNORbool('MIDAS-Training-ToyModelMKM.csv', 'ToyModelMKM.sif',
            path='share/data', verbose=True)
        t.preprocessing()
        t.gaBinaryT1()
        t.writeAll()

    or even faster::

        from cno import cnor
        t = cnor.CNORbool('ToyModelMKM.sif', 'MIDAS-Training-ToyModelMKM.csv',
            path='share/data', verbose=True)
        t.run(popsize=10)

    where *popsize* is a valid argument accepted by the GA algorithm.

    Most of the following methods calls the R function thanks to
    :mod:`cno.wrapper`. If no documentation is provided in the methods below,
    it means that the behaviour is exactly the same as the original version.

    You can still obtain the R documentation by introspecting the
    :mod:`cno.wrapper` module.

    """
    temp = True
    def __init__(self, model, data=None, cnolist=None,
                 path='.', verbose=False,
                 tag='CNORbool', debug=True):
        """**Constructor**


        :param str midasfile: the name of the MIDAS file
        :param str siffile: name of the SIF file
        :param str path: if provided, prefixes the midasfile and siffile
            arguments with a path
        :param str tag: used to create the output directory and prefix the file names.
        :param int debug: if set to 1 (default) time spent in the method is used.
        :param int verbose: propagate  verbose option to the methods (R functions)

        :Attributes:

        Read-Only:

         * :attr:`data`  :class:`~cno.wrapper.readMIDAS` object from CellNOptR
         * :attr:`model` :class:`~cno.wrapper.readSIF` object from CellNOptR
         * :attr:`data_filename`
         * :attr:`model_filename`
         * :attr:`tag`: the input arguments (CNORWrap by default)

        Read/Write:

         * :attr:`debug`: can be change to 0 (no debug) or 1 (debug)
         * :attr:`verbose`: can be change to False/True

        """
        # Read only attributes based oni input arguments
        super(CNORbool, self).__init__(model, data, cnolist, verbose, 
            debug=debug)

        self._debug_option = debug
        self._tag = tag



        self.indices = self.indexFinder(self.cnolist, self.model)

        # this may be populated later but require a default value
        self.T2opt = robjects.NA_Logical

        # the output file names
        self.namesFiles = { "dataPlot": tag + '_ModelGraph.pdf',
                      'evolFitT1':  tag + '_evolFitT1.pdf',
                      'evolFitT2':  robjects.NA_Logical,
                      'simResultsT1' : tag + "_SimResultsT1.pdf",
                      'simResultsT2' : robjects.NA_Logical,
                      'scaffold' : tag + "_Scaffold.sif",
                      'scaffoldDot' : tag + "_Scaffold.dot",
                      'tscaffold' : tag + "_TimesScaffold.EA",
                      'wscaffold' : tag + "_weightsScaffold.EA",
                      'PKN' : tag + "_PKN.sif",
                      'PKNdot' : tag + "_PKN.dot",
                      'wPKN' : tag + "_TimesPKN.EA",
                      'nPKN' : tag + "_nodesPKN.NA"}
        #self.preprocessing()
        self.residualError()


    def _get_tag(self):
        return self._tag
    tag = property(_get_tag, doc="return the tag for filenames")

    def _get_debug(self):
        return self._debug_option
    def _set_debug(self, value):
        if value in [0,1]:
            self._debug_option = value
        else:
            raise ValueError("debug can be set to 0 or 1 only")
    debug = property(_get_debug, _set_debug, doc="""debug option.
        1 prints information about time spent in a function
        0 :no output""")


    def _debug(f):
        """A simple decorator to debug tools
        """
        def wrapper( self, *args, **kargs ) :
            if self.debug==1:
                print 'Running ' + f.__name__,
                t = time.clock()

            res = f(self, *args, **kargs)
            if self.debug==1:
                print "...done (executed in %0.2fs)" % (time.clock() - t)
            return res
        wrapper.__doc__ = f.__doc__
        return wrapper


    @_debug
    def indexFinder(self, cnolist, model):
        index = indexFinder(cnolist, model, verbose=self.verbose)
        return index

    @_Rplot
    def plotCNOlistPDF(self):
        plotCNOlistPDF(cnolist=self.cnolist, filename=self.namesFiles['dataPlot'])

    @_debug
    def findNONC(self):
        raise DeprecationWarning("deprecated, use preprocessing instead")
        self.NONCindices = findNONC(self.model, self.indices, verbose=self.verbose)

    #@require('NONCindices', 'Consider running findNONC() before ')
    @_debug
    def cutNONC(self):
        raise DeprecationWarning("deprecated, use preprocessing instead")
        self.NONCcut = cutNONC(self.model, self.NONCindices)
        self.NONCcut_indices = self.indexFinder(self.cnolist, self.NONCcut)

    #@require('NONCcut_indices', "Run findNONC and cutNONC before compression")
    @_debug
    def compressModel(self):
        raise DeprecationWarning("deprecated, use preprocessing instead")
        # model compression
        self.NONCcutComp = compressModel(self.NONCcut, self.NONCcut_indices)
        self.NONCcutComp_indices = self.indexFinder(self.cnolist, self.NONCcutComp)


    @_debug
    def pre_processing(self):
        """Aliases that call some pre-processing methods

          #. :meth:`findNONC`
          #. :meth:`cutNONC`
          #. :meth:`compressModel`
          #. :meth:`expandGates`

        """
        raise DeprecationWarning("deprecated, use preprocessing instead")
        self.findNONC() # this create the NONCcut and NINCcutindices attributes
        self.cutNONC()
        self.compressModel()
        self.expandGates()


    @_debug
    def run(self, mode='T1', show=True, writeall=True, **kargs):
        """Run all the relevant methods in the proper order.

        :param str mode: 'T1' possible for now.

        The called methods are :

         #. :meth:`pre_processing`
         #. :meth:`gaBinaryT1`
         #. :meth:`writeAll`

         Arguments related to the GA can be provided. The following arguments
         (default in brackets) are possible:

            *  popsize (50)
            *  sizefac (0.0001),
            *  nafac (1),
            *  maxtime (60),
            *  pmutation (0.5),
            *  maxgens (500),
            *  stallgenmax (100),
            *  selpress (1.2),
            *  elitism (5),
            *  reltol (0.1),

        """
        assert mode in ['T1']
        if mode=='T1':
            self.gaBinaryT1(**kargs)
        #if writeall == True:
        #    self.writeAll(show=show)

    @_debug
    def expandGates(self):
        raise Error("deprecated, use preprocessing instead")
        if self.verbose:
            print 'Expanding the data'
        self.NONCcutCompExp = expandGates(self.NONCcutComp)

    @_debug
    def residualError(self):
        self.resECNOlist = residualError(self.cnolist)
        return self.resECNOlist


    def preprocessing(self, compression=True, expansion=True, cutNONC=True):
        super(CNORbool, self).preprocessing(compression=compression,    
            expansion=expansion, cutNONC=cutNONC)
        self.prep4sim()
        self.initBstring()

    @require('expmodel', 'You must run the pre processing step before pre4sim')
    @_debug
    def prep4sim(self):
        self.simlist = prep4sim(self.expmodel)


    @require('expmodel', 'Run the preprocessing step before gaBinaryT1')
    def initBstring(self, random=False):
        if random==True:
            raise NotImplementedError
        else:
            self.initStringT1 = [1] * len(self.expmodel.rx2('reacID'))


    @require('expmodel', 'Run the preprocessing step before gaBinaryT1')
    @_debug
    def gaBinaryT1(self, **kargs):
        """The GA algorithm

        Arguments are their default values:

        * sizefac = 1e-04,
        * nafac = 1,
        * popsize = 50,
        * pmutation = 0.5,
        * maxtime = 60,
        * maxgens = 500,
        * stallgenmax = 100,
        * selpress = 1.2,
        * elitism = 5,
        * relTol = 0.1

        :return: populates T1opt attribute with
                * the best bitstring
                *  a matrix with columns "Generation","Best_score","Best_bitString","Stall_Generation","Avg_Score_Gen","Best_score_Gen","Best_bit_Gen","Iter_time"
                *  the bitstrings whose scores are within the tolerance
                *  the scores of the above-mentionned strings

        t.T1opt.names contains the names to be used. For instance, t.T1opt.rx2['results']

        you can convert to numpy.array : numpy.array(t.T1opt.rx2('stringsTol'))
        otherwise you need to know the col and row: t.T1opt.rx2('stringsTol').nrow
        """

        kargs['verbose'] = kargs.get('verbose', self.verbose)

        self.T1opt = gaBinaryT1(cnolist=self.cnolist,
                                model=self.expmodel,
                                initbstring=self.initStringT1,
                                **kargs)


        # gaBinary contains 4 structures, one of them called results, which
        # is a R matrix structure containing the a matrix of 8 columns and
        # N rows, where N is the number of generation maxgens+1


        """colnames = ['Generation',
        'Best_score',
        'Best_bitString',
        'Stall_Generation',
        'Avg_Score_Gen',
        'Best_score_Gen',
        'Best_bit_Gen',
        'Iter_time']"""

        nrows = self.T1opt.results.nrow
        colnames = self.T1opt.results.colnames
        for i, name in enumerate(colnames):
            try:
                data = [float(x) for x in self.T1opt.results[nrows*i:nrows*(i+1)]]
            except:
                data = [x for x in self.T1opt.results[nrows*i:nrows*(i+1)]]

            setattr(self.T1opt.results, name, data)

    @require('T1opt', 'require gaBinaryT1 to be run')
    @_debug
    def gaBinaryTN(self, **kargs):

        kargs['verbose'] = self.verbose
        self.T2opt = gaBinaryTN(cnolist=self.cnolist,
                                model=self.expmodel,
                                bstringT1=self.T1opt.bString,
                                **kargs)
        """colnames = ['Generation',
        'Best_score',
        'Best_bitString',
        'Stall_Generation',
        'Avg_Score_Gen',
        'Best_score_Gen',
        'Best_bit_Gen',
        'Iter_time']"""

        nrows = self.T2opt.results.nrow
        colnames = self.T2opt.results.colnames
        for i, name in enumerate(colnames):
            try:
                data = [float(x) for x in self.T2opt.results[nrows*i:nrows*(i+1)]]
            except:
                data = [x for x in self.T2opt.results[nrows*i:nrows*(i+1)]]

            setattr(self.T2opt.results, name, data)

    def plotModel(self, **kargs):
        """plot optimised model"""
        if 'bString' in kargs.keys():
            pass
        else:
            try:
                bString = kargs.get("bString", self.T1opt.bString)
                kargs['bString'] = bString
            except:
                raise ValueError("gaBinaryT1 must be run first, or bString argument set to None.") 
        plotModel(self.expmodel, self.cnolist, **kargs)


    @require('T1opt', 'Run gaBinaryT1 first')
    @_debug
    def plotFit(self, time='T1', plotting='pylab'):
        """plotFir using either R original version or matplotlib version.

        """
        assert time in ['T1', 'T2']
        if time == 'T1':
            data = self.T1opt
        elif time == 'T2':
            data = self.T2opt
            if self.T2opt == robjects.NA_Logical:
                raise ValueError('todo')

        if plotting=='pylab':
            import pylab
            pylab.figure(1)
            pylab.clf()
            gen = data.results.Generation
            bestScore = data.results.Best_score
            avgScore = data.results.Avg_Score_Gen

            pylab.subplot(2, 1, 1)
            pylab.plot(gen, avgScore)
            pylab.ylabel('Average score of generation')
            ylims = pylab.ylim()
            pylab.ylim(0, ylims[1])

            pylab.subplot(2, 1, 2)
            pylab.plot(gen, bestScore)
            ylims = pylab.ylim()
            pylab.ylim(0, ylims[1])
            pylab.ylabel('Best Score')
            pylab.xlabel('Generation')
        else:
            print 'plotFit'
            print time
            print
            print self.namesFiles["evolFit"+time]
            self.newRdev()
            plotFit(data,filename=self.namesFiles["evolFit"+ time])


    #@require('T1opt', 'Run gaBinaryT1 first')
    #@_Rplot
    #@_debug
    def cutAndPlotResultsT1(self, bString=None, plotpdf=False):
        if bString==None:
            bString = self.T1opt.bString[:]
        self.cutAndPlot = cutAndPlotResultsT1(model=self.expmodel,
                            bString=bString,
                            cnolist=self.cnolist,
                            plotpdf=plotpdf,
                            tag=self.tag
                            )

    @require('T1opt', 'Run gaBinaryT1 first')
    @require('T2opt', 'Run gaBinaryT2 first')
    @_Rplot
    @_debug
    def cutAndPlotResultsT2(self, ):
        self.cutAndPlot = cutAndPlotResultsT2(model=self.expmodel,
                            bStringT1=self.T1opt.bString,
                            bStringT2=self.T2opt.bString,
                            cnolist=self.cnolist,
                            plotpdf=True,
                            tag=self.tag,
                            )





    @require('T1opt', 'T1opt missing run gaBinaryT1')
    @_debug
    def writeScaffold(self):
        #"""Creates these files:         weightsScaffold.EA
        # TimesScaffold.EA        Scaffold.dot        Scaffold.sif
        writeScaffold(modelcomprexpanded=self.expmodel,
                      optimrest1=self.T1opt, optimrest2=self.T2opt,
            modeloriginal=self.model, cnolist=self.cnolist,   tag=self.tag)



    @require('T1opt', 'T1opt missing run gaBinaryT1')
    @_debug
    def writeNetwork(self):
        writeNetwork(modeloriginal=self.model,
                     modelcomprexpanded=self.expmodel,
                     optimrest1=self.T1opt, optimrest2=self.T2opt,
                     cnolist=self.cnolist, tag=self.tag)


    @require('T1opt', 'T1opt missing run gaBinaryT1')
    @_debug
    def writeReport(self):
        #if self.tag != None:
        #    tag = self.tag + "_"

        writeReport(modeloriginal=self.model, modelopt=self.expmodel,
                    optimrest1=self.T1opt, optimrest2 = self.T2opt, cnolist=self.cnolist,
                    directory=self.tag, namesfiles=self.namesFiles,
                    namesdata={'CNOlist' : self.data_filename,
                               'Model': self.model_filename},
                    rese = self.resECNOlist)

    def writeAll(self, show=True):
        """Alias to write all results in files

        Calls:

         #. :meth:`writeScaffold`
         #. :meth:`writeNetwork`
         #. :meth:`plotCNOlistPDF`
         #. :meth:`cutAndPlotResultsT1`
         #. :meth:`plotFit`
         #. :meth:`writeReport`

        """

        self.writeScaffold()
        self.writeNetwork()
        self.plotCNOlistPDF() # save ModelGraph.pdf

        self.cutAndPlotResultsT1() # evolT1
        if self.T2opt != robjects.NA_Logical:
            self.cutAndPlotResultsT2() # evolT2

        self.plotFit('T1' ,plotting='R')
        if self.T2opt != robjects.NA_Logical:
            self.plotFit('T2' ,plotting='R')

        self.writeReport()

        #closeR()


def pyplotModel(model, midas=None, stimuli=None, signals=None,
        compressed=None, inhibitors=None, output="STDOUT", filename=None,
        bString=None, subfield=False, grdevices=False):
    if midas == None:
        cnolist = None
    else:
        try:
            m = readMIDAS(midas, verbose=False)
            cnolist = makeCNOlist(m, verbose=False, subfield=subfield)
        except:
            cnolist = midas # maybe user provided a cnolist, not a midas file
    assert output in ['PDF','SVG','PNG', "STDOUT"]

    if grdevices:
        assert filename
        from rpy2.robjects.packages import importr
        grdevices = importr('grDevices')
        if output ==  'PNG':
            grdevices.png(file=filename + ".png", width=1024, height=1024)
        elif output == 'SVG':
            grdevices.svg(file=filename + ".svg")
        elif output == 'PDF':
            grdevices.pdf(file=filename + ".pdf")

    plotModel(model, cnolist=cnolist, stimuli=stimuli,
        signals=signals,output=output, bString=bString,
        compressed=compressed, inhibitors=inhibitors, filename=filename)

    if grdevices:
        grdevices.dev_off()



def closeR():
    """Close all R devices

    When plotting with R, a graphical device is open, which can not be closed
    by hand (i.e., with the mouse button). This function properly close the
    devices by calling the R code: dev.off().

    ::

        closeR()
    """
    from rtools import RRuntimeError
    try:
        robjects.r('dev.off()')
    except RRuntimeError, e:
        print "Nothing to close. Original message:", e

class CNORdt(CNORBase):

    def __init__(self, model, data=None, cnolist=None, verbose=False):
        super(CNORdt, self).__init__(model, data, cnolist, verbose)


    @require('expmodel', "you must call preprocessing function.")
    def gaBinaryDT(self, **kargs):
        """arguments of rpack_CNORdt.gaBinaryDT"""
        self.T1opt = wrapper_dt.gaBinaryDT(self.cnolist, self.expmodel, **kargs)
        self.bs = self.T1opt.rx2('bString')
        nrows = self.T1opt.results.nrow
        colnames = self.T1opt.results.colnames
        for i, name in enumerate(colnames):
            try:
                data = [float(x) for x in self.T1opt.results[nrows*i:nrows*(i+1)]]
            except:
                data = [x for x in self.T1opt.results[nrows*i:nrows*(i+1)]]

            setattr(self.T1opt.results, name, data)

    @require('results', 'you must call gaBinaryDT before this function')
    def cutAndPlotResults(self, **kargs):
        wrapper_dt.cutAndPlotResultsDT(self.cnolist, self.expmodel, 
            self.bs, **kargs)


class CNORfuzzy(CNORBase):

    def __init__(self, model, data=None, cnolist=None, verbose=False):
        # to be defined before ca;; to super because makeCNOlist will be called
        # and requires verbose option.
        super(CNORfuzzy, self).__init__(model, data, cnolist, verbose)

        self.thresholds = [0.0001, 0.0005, 0.001, 0.002, 0.003, 0.004, 0.005,
            0.006, 0.007, 0.008, 0.009, 0.01, 0.013, 0.015, 0.017, 0.02, 0.025, 0.03, 0.05,
            0.1, 0.2, 0.3, 0.5]

        self.allRes = []
        self.params = wrapper_fuzzy.defaultParametersFuzzy(self.cnolist, self.model)
        self.preprocessing()

    def run(self, N=1, reset=True, verbose=False):
        try:
            delattr(self, "summary")
        except AttributeError:
            pass
        self.allRes = []
        for i in range(0, N):
            print "Performing analysis %s of %s" % (i+1, N)
            Res = wrapper_fuzzy.CNORwrapFuzzy(self.cnolist, self.model, self.params, verbose)
            self.allRes.append(Res)

    def _set_maxGens(self, data):
        assert data>0
        self.params.rx2['maxGens'] = data
    def _get_maxGens(self):
        return self.params.rx2('maxGens')
    maxGens = property(fget=_get_maxGens, fset=_set_maxGens)

    def _set_verbose(self, data):
        assert data in [True, False]
        self.params.rx2['verbose'] = data
        self._verbose = data
    def _get_verbose(self):
        return self._verbose
    verbose = property(fget=_get_verbose, fset=_set_verbose)

    def _set_optimisation_maxtime(self, data):
        assert data > 0
        optim = self.params.rx2('optimisation')
        optim.rx2['maxtime'] = data
        self.params.rx2['optimisation'] = optim
    def _get_optimisation_maxtime(self):
        return self.params.rx2('optimisation').rx2('maxtime')
    optimisation_maxtime = property(fget=_get_optimisation_maxtime,
                                    fset=_set_optimisation_maxtime)

    def compileMultiRes(self, results=None, show=False):
        if results != None:
            self.summary = wrapper_fuzzy.compileMultiRes(results)
        else:
            self.summary = wrapper_fuzzy.compileMultiRes(self.allRes)

    @require('summary', "summary attribute empty, run compileMultiRes first.")
    @_Rplot
    def plotMSE(self, **kwargs):
        """plot MSEs using interpolation of the results provided by the Fuzzy Analysis"""
        import numpy
        dimRow = self.summary.allFinalMSEs.dim[0]
        allFinalMSEs = numpy.matrix(self.summary.allFinalMSEs)
        allFinalNumParams = numpy.matrix(self.summary.allFinalNumParams)
        catExplore = numpy.zeros((dimRow, len(self.thresholds)))
        AbsNumParams = numpy.zeros((dimRow, len(self.thresholds)))
        AbsMSEs = numpy.zeros((dimRow, len(self.thresholds)))

        # interpolation
        for i in range(0,len(self.thresholds)):
            for j in range(0, dimRow):
                currIX = numpy.where(allFinalMSEs[j,]-allFinalMSEs[j,1]<=self.thresholds[i])[1]
                catExplore[j,i] = numpy.max(currIX)

        for i in range(0,dimRow):
            for j in range(0, len(self.thresholds)):
                AbsNumParams[i,j] = allFinalNumParams[i, catExplore[i,j]]
                AbsMSEs[i,j] = allFinalMSEs[i, catExplore[i,j]]

        # final mean MSEs and number of parameters
        self.meanMSEs = numpy.mean(AbsMSEs, axis=0)
        self.meanNPs = numpy.mean(AbsNumParams, axis=0)

        from pylab import xlabel, ylabel, legend, hold, clf, axis, show, \
            semilogx, grid, xticks, yticks,linspace,gca, figure

        fontsize = 20
        fig1 = figure()
        ax1 = fig1.add_subplot(111)
        line1 = ax1.semilogx(self.thresholds, self.meanMSEs, 'b-o', **kwargs)
        ylabel("MSEs", fontsize=fontsize)
        xticks(fontsize=16)
        yticks(fontsize=16)

        axis([self.thresholds[0], self.thresholds[-1],
            min(self.meanMSEs)/1.01,max(self.meanMSEs)*1.01])

        ax2 = fig1.add_subplot(111, sharex=ax1, frameon=False)
        line2 = ax2.plot(self.thresholds, self.meanNPs, 'r-o')
        ax2.yaxis.tick_right()
        ax2.yaxis.set_label_position("right")
        ylabel("Number of Parameters", fontsize=fontsize)

        legend((line1, line2), ("mean MSEs", "mean Number of Parameters"),
            loc="center left", prop={'size':13})
        grid()
        xticks(fontsize=16)
        yticks(fontsize=16)
        #show()


    @_Rplot
    def plotMeanFuzzyFit(self, threshold=0.01, plotPDF=True):
        wrapper_fuzzy.plotMeanFuzzyFit(threshold, self.summary.allFinalMSEs,
            self.allRes, plotPDF=plotPDF)


class CNORode(CNORBase):
    """

    t = CNORode("ToyModel.sif", "ToyModel.csv", method='ga')
    t.preprocessing(compression=False, expansion=False) # True does not work
    t.run()
    t.plotn()
    t.plotLBodeFitness()

    .. warning:: when compressing


    """

    def __init__(self, model, data=None, cnolist=None, verbose=False,
method='ga', maxtime=None, iters=None):
        super(CNORode, self).__init__(model, data, cnolist, verbose)
        self._method = method

        self.paramsGA = wrapper_ode.defaultParametersGA()
        self.paramsSSm = wrapper_ode.defaultParametersSSm()

        self.paramsGA.rx2['verbose'] = verbose
        self.paramsGA.rx2['monitor'] = verbose
        self.paramsSSm.rx2['verbose'] = verbose

        # the following are attributes to be changed.
        self._iters = self.paramsGA.rx2('iters')
        self._maxtime = self.paramsSSm.rx2('maxtime')
        if maxtime:
            self.maxtime = maxtime
        if iters:
            self.iters = iters
        self.preprocessing(compression=False, expansion=False)
        self.reset()


    def preprocessing(self, **kargs):
        # it the model changes, the ode parameters (list of k, n and tau
        # parameters could change, so need to call reset()
        assert kargs.get('expansion') == False, "expansion must be False with CNORode preprocessing"
        if kargs.get('compression') == True:
            import warnings
            warnings.warn(""""compression is dangerous with CNORode. use with care.
if plotn() does not work, this may be because compressed model lose ambiguous edges""")

        super(CNORode, self).preprocessing(**kargs)

    @require("expmodel", "call preprocessing first")
    def reset(self, random=False):
        self.ode_parameters = wrapper_ode.createLBodeContPars(self.expmodel,
                random=random)

    def _set_iters(self, data):
        assert data > 0
        self.paramsGA.rx2['iters'] = data
    def _get_iters(self):
        return self.paramsGA.rx2('iters')
    iters = property(fget=_get_iters, fset=_set_iters)

    def _set_maxtime(self, data):
        assert data > 0
        self.paramsSSm.rx2['maxtime'] = data
    def _get_maxtime(self):
        return self.paramsSSm.rx2('maxtime')
    maxtime = property(fget=_get_maxtime, fset=_set_maxtime)

    def _set_verbose(self, data):
        assert data in [True, False]
        self.paramsGA.rx2['verbose'] = data
        self.paramsSSm.rx2['verbose'] = data
        self._verbose = data
    def _get_verbose(self):
        return self._verbose
    verbose = property(fget=_get_verbose, fset=_set_verbose)

    def _set_method(self, method):
        assert method in ['ga', 'essm']
        self._method = method
    def _get_method(self):
        return self._method
    method = property(fget=_get_method, fset=_set_method)

    def _get_best_score(self):
        if self.method == 'ga':
            #return self.ode_parameters.rx2('res').rx2('best') that is a vector.
            # the best score is the last one.
            return list(self.ode_parameters[8][11])
        elif self.method == 'essm':
            #return self.ode_parameters.rx2('ssm_results').rx2('fbest')
            # sometimes, we pickling results, names are lost, so we need to
            # specify the indices. Not robust if the code changes...
            # the last [0] is to extract the float out of the R vector of length
            # 1
            return self.ode_parameters[8][4][0] 
    bestscore = property(_get_best_score)

    @require('expmodel', 'Call preprocessing method first')
    def run(self, method=None, buffering=False, reset=False):
        self.buf = []
        if buffering:
            from rpy2 import rinterface
            rinterface.set_writeconsole(self._rbuffer)

        if method != None:
           self.method = method

        #if reset==True:
        #self.reset()

        if self.method == 'ga':
            self._run_ga()
            if self.verbose:print("GA analysis done")
        else:
            self._run_essm()
            if self.verbose:print("SSM analysis done")
        # restore default function
        if buffering:
            rinterface.set_writeconsole(rinterface.consolePrint)

        self.ode_parameters_names_ga = ["parNames", "parValues", "index_opt_pars",
            "index_n", "index_k", "index_tau", "LB", "UB", "res"]

        self.ode_parameters_names_ga_res = ["type", "stringMin", "stringMax",
"popSize", "iters", "suggestions", "population", "elitism", "mutationChance",
"evaluations",    "best" ,"mean"]

        self.ode_parameters_names_ssm = ["parNames", "parValues", "index_opt_pars",
            "index_n", "index_k", "index_tau", "LB", "UB", "ssm_results"]

        self.ode_parameters_names_ssm_res = ["f", "x", "time", "neval", "fbest" ,
            "xbest", "numeval", "end_crit", "cpu_time", "Refset_x", "Refset_f", 
            "Refset_fpen", "Refset_const", "Refset_penalty"]





    def _get_k(self):
        try:
            return [list(self.ode_parameters.parValues)[i] for i in self.indexk]
        except:
            return [list(self.ode_parameters[1])[i] for i in self.indexk]
    k = property(_get_k)

    def _get_n(self):
        try:
            return [list(self.ode_parameters.parValues)[i] for i in self.indexn]
        except:
            return [list(self.ode_parameters[1])[i] for i in self.indexn]
    n = property(_get_n)

    def _get_tau(self):
        try:
            return [list(self.ode_parameters.parValues)[i] for i in self.indextau]
        except:
            return [list(self.ode_parameters[1])[i] for i in self.indextau]
    tau = property(_get_tau)

    def _get_indextau(self):
        # -1 because R indices starts at 1
        try:
            indices = [int(x-1) for x in list(self.ode_parameters.index_tau)]
        except:
            indices = [int(x-1) for x in list(self.ode_parameters[5])]
        return indices
    indextau = property(_get_indextau)

    def _get_indexk(self):
        # -1 because R indices starts at 1
        try:
            indices = [int(x-1) for x in list(self.ode_parameters.index_k)]
        except:
            indices = [int(x-1) for x in list(self.ode_parameters[4])]
        return indices
    indexk = property(_get_indexk)

    def _get_LB(self):
        return list(self.ode_parameters.LB)
    LB = property(_get_LB)

    def _get_UB(self):
        return list(self.ode_parameters.UB)
    UB = property(_get_UB)

    def _get_LB_k(self):
        return [self.LB[x] for x in self.indexk]
    LB_k = property(_get_LB_k)

    def _get_UB_k(self):
        return [self.UB[x] for x in self.indexk]
    UB_k = property(_get_UB_k)

    def _get_LB_n(self):
        return [self.LB[x] for x in self.indexn]
    LB_n = property(_get_LB_n)


    def _get_UB_n(self):
        return [self.UB[x] for x in self.indexn]
    UB_n = property(_get_UB_n)

    def _get_LB_tau(self):
        return [self.LB[x] for x in self.indextau]
    LB_tau = property(_get_LB_tau)

    def _get_UB_tau(self):
        return [self.UB[x] for x in self.indextau]
    UB_tau = property(_get_UB_tau)

    def _get_indexn(self):
        # -1 because R indices starts at 1
        try:
            iN = [int(x-1) for x in list(self.ode_parameters.index_n)]
        except:
            iN = [int(x-1) for x in list(self.ode_parameters[3])]
        return iN
    indexn = property(_get_indexn)

    def _run_ga(self):
        self.ode_parameters = wrapper_ode.parEstimationLBode(self.cnolist,
            self.expmodel, method=self.method,
            ode_parameters=self.ode_parameters, indices=NULL,
            params=self.paramsGA)

    def _run_essm(self):
        self.ode_parameters = wrapper_ode.parEstimationLBode(self.cnolist,
            self.expmodel, method=self.method,
            ode_parameters=self.ode_parameters, indices=NULL,
            params=self.paramsSSm)

    def _rbuffer(self, x):
         # function that append its argument to the list 'buf'
         self.buf.append(x)

    #@_Rplot
    def plotLBodeFitness(self, filename=None, show=True, colormap="heat"):
        if filename:
            from rpy2.robjects.packages import importr
            grdevices = importr('grDevices')
            grdevices.png(file=filename, width=512, height=512)
            res = wrapper_ode.plotLBodeFitness(self.cnolist, self.expmodel,
                self.ode_parameters, NULL, colormap=colormap)
            grdevices.dev_off()
            #closeR()

        if show:
            res = wrapper_ode.plotLBodeFitness(self.cnolist, self.expmodel,
                self.ode_parameters, NULL)
        return res


    #@_Rplot
    def plotLBodeModelSim(self, filename=None, show=True):
        if filename:
            from rpy2.robjects.packages import importr
            grdevices = importr('grDevices')
            grdevices.png(file=filename, width=512, height=512)
            wrapper_ode.plotLBodeModelSim(self.cnolist, self.expmodel,
                self.ode_parameters)
            grdevices.dev_off()
            #closeR()
        if show:
            wrapper_ode.plotLBodeModelSim(self.cnolist, self.expmodel,
                self.ode_parameters)

    def plotFit(self):
        from pylab import plot, xlabel, ylabel, grid
        try:
            plot(self.ode_parameters.rx2('res').rx2('best'), 'or-')
        except:
            try:
                # the ga case
                plot(self.ode_parameters[9][10], 'or-')
            except:
                # the ssm case
                try:
                    plot(self.ode_parameters[9][10], 'or-')
                except:
                    raise Exception

        xlabel('Number of iterations')
        ylabel('Objective function')
        grid()

    def plotk(self):
        M = max(self.k)
        if M >= 1:
            k = [x/M for x in self.k]
        else:
            k = self.k[:]
        from cellnopt.wrapper import plotModel
        try:
            plotModel(self.expmodel, self.cnolist, bString=k)
        except:
            plotModel(self.model, self.cnolist, bString=k)


    def plotn(self):

        M = max(self.n)
        if M >= 1:
            n = [x/M for x in self.n]
        else:
            n = self.n[:]
        from cellnopt.wrapper import plotModel
        try:
            plotModel(self.expmodel, self.cnolist, bString=n)
        except:
            plotModel(self.model, self.cnolist, bString=n)

    def computeScore(self, x=None, random=True):

        minlp_obj_function = wrapper_ode.getLBodeContObjFunction(self.cnolist,
            self.model, self.ode_parameters, NULL, time=1,                 verbose=0,
        transfer_function=3,    reltol=1e-4,            atol=1e-3,
        maxStepSize=1e6,        maxNumSteps=100000,     maxErrTestsFails=50,
        nan_fac=1)

        if x == None:
            if random == True:
                x = wrapper_ode.createLBodeContPars(self.expmodel, random=True)
                x = x.parValues[:]
                print(x)
            else:
                x = self.ode_parameters.parValues[:]
            #print x
        f = minlp_obj_function(x)
        return f[0]
