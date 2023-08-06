Tutorial
###########

.. contents::

CellNOptR interface
======================

From the :ref:`quickstart`  section, you've seen that **cellnopt.wrapper** provides an interface to CNOR (R package). Let us illustrate this ability with a long example.

Example
----------

First, let us get some data. **cellnopt.wrapper** provides a function called
:func:`cellnopt.wrapper.tools.get_data` and a set of model and data to play with. The function get_data will
help you to get the proper pathname of those files::

    from cellnopt.wrapper import get_data
    model_filename = get_data("ToyModelMKM.sif")
    data_filename = get_data("ToyModelMKM.csv")

Each CellNOptR function has its Python function with a similar prototype. For instance
:func:`cellnopt.wrapper.wrapper_cnor.readSIF`::

    from cellnopt.wrapper import readSIF
    from cellnopt.wrapper import get_data

    model_filename = get_data("ToyModelMKM.sif")
    model = readSIF(model_filename)

The python function *readSIF* calls the R function called *readSIF*. Of course,
you must use the Python syntax instead of the R function. Although the two
syntaxes are similar, there are a few differences summarizes below. 

The example below is taken from CellOptR documenation with just a few
editions. For instance, TRUE (R syntax) is now True (python syntax)::

    # Read the data sets ====================================================
    # data = readMIDAS(get_data('ToyModelMKM.csv')) # 
    from cellnopt.wrapper import *
    midas_filename = get_data('ToyModelMKM.csv')
    pknmodel = readSIF(get_data('ToyModelMKM.sif'))

    # create the CNOLIST object and compute residual errors
    cnolist = CNOlist(midas_filename)  # CNOlist function replaces readMIDAS+makeCNOlist function calls

    # some sanity checks
    checkSignals(cnolist, pknmodel)

    # pre processing =========================================================
    model = preprocessing(cnolist, pknmodel, expansion=True,
        compression=True, cutNONC=True)

    # GA simulation ==========================================================

    # You can create an initial guess (here only ones), which length must equal the number of reacId
    initbstring = initBstring(model.reacID) 
    # some dummy values to quickly generate some results
    kargs = {'popsize':50,'maxgens':10, 'stallgenmax':10, 'elitism':5,}
    T1opt = gaBinaryT1(cnolist=cnolist, model=model, initbstring=initbstring, verbose=True, **kargs)

    # plotting and writting results
    tag = "Tutorial"   # The original

    cutAndPlotResultsT1(model=model, bString=T1opt.bString,  
        cnolist=cnolist, plotpdf=True, tag=tag)
    plotFit(T1opt, filename=tag + "_evolFitT1.pdf")
    plotCNOlistPDF(cnolist, filename=tag + "_ModelGraph.pdf")

    writeScaffold(modelcomprexpanded=model, optimrest1=T1opt, modeloriginal=model,
        cnolist=cnolist, tag=tag)
    writeNetwork(modeloriginal=model, modelcomprexpanded=model, optimrest1=T1opt,  
        cnolist=cnolist, tag=tag)

    # Note that None is not accepted by R, so we need to use the special R 
    namesdata = {'CNOlist' : 'ToyModel', 'model': 'ToyModel'}



    namesfiles = {    'dataPlot' : tag + "_ModelGraph.pdf",
                      'evolFitT1':  tag + "_evolFitT1.pdf", 
                      'evolFitT2' : None, 
                      'simResultsT1' : tag + "_SimResultsT1.pdf",
                      'simResultsT2' : None, 
                      'scaffold' : tag + "_Scaffold.sif",
                      'scaffoldDot' : tag + "_Scaffold.dot",
                      'tscaffold' : tag + "_TimesScaffold.EA",
                      'wscaffold' : tag + "_weightsScaffold.EA",
                      'PKN' : tag + "_PKN.sif", 
                      'PKNdot' : tag + "_PKN.dot",
                      'wPKN' : tag + "_TimesPKN.EA", 
                      'nPKN' : tag + "_nodesPKN.NA"}

    resError = rpack_CNOR.residualError(cnolist)
    writeReport(modeloriginal=pknmodel, modelopt=model, optimrest1=T1opt, cnolist=cnolist,
        directory=tag, namesdata=namesdata, namesfiles=namesfiles, rese=resError)


.. topic:: Implementation difference

   * In all functions, the optional arguments are the same as in R, but we use lower case to simplify the user interface.
   * TRUE and FALSE in R become True and False in Python
   * To access to a variable in R, one can use the $ sign (e.g. data$reacID). With Rpy2 package the pythonic way to access the such variables is to call the method rx2 with the name of the variable as argument (e.g., data.rx2('reacID')). This syntax is not very convenient, so to ease the access to such attributes, the cellnopt.wrapper module uses **rtools** to create attributes for each name found in the names attribute  (i,e., in data.names).:





Use CNOR outputs in Python
===================================


From the CNOR interface, you can use the plotting functionalities of the R library:

.. doctest::

    from cellnopt.wrapper import *
    cnolist = CNOlist(get_data('ToyModelMKM.csv'))
    plotCNOlist(cnolist)

However, you can also play with matplotlib (matlab-lie interface) to plot other data sets

.. plot::
    :width: 50%
    :include-source:

    # first, we need the import
    from cellnopt.wrapper.wrapper_cnor import *
    from cellnopt.wrapper import get_data

    # then, we create a cnolist to play with
    midas = readMIDAS(get_data('ToyModelMKM.csv'))
    cnolist = makeCNOlist(midas)

    # cnolist contains the midas data in valueSignals, let us extract the time t1
    # and convert the data thanks to numpy
    import numpy
    data = cnolist.valueSignals.iteritems() # will iterate through the valuesSignals matrices
    data.next()  # skip the t0
    t1 = data.next()  # t1[0] cnontains the names, t1[1] the data
    data = numpy.array(t1[1])  # convert to numpy array
    labels = list(cnolist.namesSignals)

    # Finally, we use matplotlib to plot the results
    from pylab import *
    clf();
    pcolor(data)
    colorbar();
    hot();
    #xticks(linspace(0,6,7)+0.5, labels, rotation=90)



Using a CNOR class  
=========================================================

The :mod:`~cellnopt.wrapper.cnor` module provides a funtion called CNOR that ease the development of scripts. Indeed, from the example above, it is clear that one has to be very careful with all the arguments. Moreover, running CNOR involves about 20 different commands. Thanks to the class :class:`~cellnopt.wrapper.cnor.CNORBool` that has the same spirit as the original CNORbool function except that it is an object. It is not linked to the CNORbool function from the R package. 

Example
---------

The quickest way to run CNO is to read the data and use the method :meth:`cellnopt.wrapper.cnor.CNORbool.run`::

    from cellnopt.wrapper import *

    midasfile = get_data('ToyModelMKM.csv')
    siffile = get_data('ToyModelMKM.sif')

    # The directory where to save the data, and the prefix for all filenames is
    # related to the variable **tag**
    tag = "Tutorial"
    cnorwrap = CNORbool(siffile, midasfile, tag=tag)
    cnowrap.preprocessing()
    # now, we run everything from pre-processing, GA algorithm, and report outputs
    cnorwrap.run(popsize=10, maxgens=50)     # here we set some simple GA parameters to 
                                            # fasten the tutorial example.


If you want to run CNO step by step, you can still do it, however,  you do not need to worry about arguments anymore:

.. plot::
    :width: 50%
    :include-source:

    from cellnopt.wrapper import *

    midasfile = get_data('ToyModelMKM.csv')
    siffile = get_data('ToyModelMKM.sif')

    cnorwrap = CNORbool(siffile, midasfile, tag="Tutorial")

    # preprocessing is called when creating the object, but you can run it again
    cnorwrap.preprocessing(expansion=False)

    # plotting and printing results, used later on in the report.
    cnorwrap.plotCNO()
    cnorwrap.plotCNOlistPDF()

    # GA algo
    #cnorwrap.init_training()
    cnorwrap.gaBinaryT1(popsize=10, maxgens=20, elitism=5)
    cnorwrap.plotFit()   # a matplotlib version of plotFit (see not below)

    #
    #cnorwrap.cutAndPlotResultsT1()
    #cnorwrap.writeScaffold()
    #cnorwrap.writeNetwork()
    #cnorwrap.writeReport()


 
.. note:: Note that :meth:`~cno.cnor.CNORbool.plotFit` has been rewritten in Python to demonstrate the ability to use matplotlib to plot the results given by the R package. The default functio (R function) can still be used by providing the argument plot='R'.



Using cellnopt.wrapper.wrapper_cnor to test CellNOptR
==========================================================


If you download the source of cellnopt.cno, there is a test directory that tests
all the modules described in this documentation. Consequently, when running the
tests you are actually testing cellnopt.cno but also CNOR by the way of the 
cellnopt.wrapper module.


Additional test can be added. See in particular test_CNOR_unit.py and
test_CNOR_functional.py


Generally, you can either use the R functions that have been wrapped in
cellnopt.wrapper.wrapper_cnor to create unit and functional tests. However, you may have
extra R code that required works in Python so instead, you can also provide
an entire piece of R code. The test code would look like:

::

    import rpy2
    from rpy2 import robjects

    robjects.r('''
        f <- function(r, verbose=FALSE) {
           if (verbose) {
               cat("I am calling f().\n")
           }
           2 * pi * r
       }
       ''')   
    r_f = robjects.r['f']
    r_f(3) 




