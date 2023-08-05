from cellnopt.wrapper import cnor
from cellnopt.wrapper.data import get_data 
from cellnopt.data import cnodata
from nose.tools import assert_almost_equal



midasfile = cnodata('ToyModelMKM.csv')
midasfile2 = get_data('ToyModelT2.csv')
siffile = cnodata('ToyModelMKM.sif')


class TestCNOR():
    """ Test the following R example (R_timecourse SVN 131) using the wrapped
    functions of the R package called CNOR.
    
    Note that variable names are not always easy to follow, but I kept the same
    name as in the example and original code to ease the code development.
    
    library(CellNOptR)
    library(RBGL)
    dir.create("CNOR_analysis")
    setwd("CNOR_analysis")

    # copy files to working directory
    cpfile <- dir(system.file("ToyModel", package = "CellNOptR"), full=TRUE)
    file.copy(from=cpfile, to=getwd(), overwrite=TRUE)

    # make CNOlistToy
    dataToy <- readMIDAS(MIDASfile = "ToyDataMMB.csv")
    CNOlistToy <- makeCNOlist(dataset = dataToy, subfield = FALSE)

    # visualize data
    plotCNOlist(CNOlistToy)

    ToyModel <- readSIF(sifFile = "ToyModelMKM.sif")
    checkSignals(CNOlistToy, ToyModel)
    indicesToy <- indexFinder(CNOlistToy, ToyModel, verbose = TRUE)

    # a check when any cut is made to a model:
    ToyNCNOindices <- findNONC(ToyModel, indicesToy, verbose = TRUE)
    ToyNCNOcut <- cutNONC(ToyModel, ToyNCNOindices)
    indicesToyNCNOcut <- indexFinder(CNOlistToy, ToyNCNOcut)

    # compression and expansion
    ToyNCNOcutComp <- compressModel(ToyNCNOcut, indicesToyNCNOcut)
    indicesToyNCNOcutComp <- indexFinder(CNOlistToy, ToyNCNOcutComp)
    ToyNCNOcutCompExp <- expandGates(ToyNCNOcutComp)

    # prep model
    resECNOlistToy <- residualError(CNOlistToy)
    ToyFields4Sim <- prep4sim(ToyNCNOcutCompExp)
    initBstring <- rep(1, length(ToyNCNOcutCompExp$reacID))

    ToyT1opt <- gaBinaryT1(CNOlist = CNOlistToy, Model = ToyNCNOcutCompExp,
        SimList = ToyFields4Sim, indexList = indicesToyNCNOcutComp,
        initBstring = initBstring, verbose = FALSE)

    # plot results
    cutAndPlotResultsT1(Model = ToyNCNOcutCompExp, bString = ToyT1opt$bString,
        SimList = ToyFields4Sim, CNOlist = CNOlistToy, indexList = indicesToyNCNOcutComp,
        plotPDF = FALSE)
    plotFit(OptRes = ToyT1opt)

    # write data
    writeScaffold(ModelComprExpanded = ToyNCNOcutCompExp,
        optimResT1 = ToyT1opt, optimResT2 = NA, ModelOriginal = ToyModel,
        CNOlist = CNOlistToy)

    writeNetwork(ModelOriginal = ToyModel, ModelComprExpanded = ToyNCNOcutCompExp,
        optimResT1 = ToyT1opt, optimResT2 = NA, CNOlist = CNOlistToy)

    namesFilesToy <- list(dataPlot = "ToyModelGraph.pdf",
       evolFitT1 = "evolFitToyT1.pdf", evolFitT2 = NA, simResultsT1 = "ToyNCNOcutCompExpSimResultsT1.pdf",
       simResultsT2 = NA, scaffold = "ToyNCNOcutCompExpScaffold.sif",
       scaffoldDot = "ModelModelComprExpandedScaffold.dot",
       tscaffold = "ToyNCNOcutCompExpTimesScaffold.EA",
       wscaffold = "ToyNCNOcutCompExpweightsScaffold.EA",
       PKN = "ToyModelPKN.sif", PKNdot = "ToyModelPKN.dot",
       wPKN = "ToyModelTimesPKN.EA", nPKN = "ToyModelnodesPKN.NA")

    writeReport(ModelOriginal = ToyModel, ModelOpt = ToyNCNOcutCompExp,
        optimResT1 = ToyT1opt, optimResT2 = NA, CNOlist = CNOlistToy,
        directory = "testToy", namesFiles = namesFilesToy,
        namesData = list(CNOlist = "Toy", Model = "ToyModel"),
        resE = resECNOlistToy)
    """

    def __init__(self):

        # Th
        # read the data
        self.dataToy = cnor.readMIDAS(midasfile)
        self.ToyModel = cnor.readSIF(siffile)

        # create the cnolist
        self.CNOlistToy = cnor.makeCNOlist(self.dataToy)
        self.indicesToy = cnor.indexFinder(self.CNOlistToy, self.ToyModel)

        # remove NONC
        self.ToyNONCindices = cnor.findNONC(self.ToyModel, self.indicesToy) # empty in the toy model case
        self.ToyNONCcut = cnor.cutNONC(self.ToyModel, self.ToyNONCindices) # empty in the toy model case
        self.indicesToyNONCcut = cnor.indexFinder(self.CNOlistToy, self.ToyNONCcut)

        # compression
        self.ToyNONCcutComp = cnor.compressModel(self.ToyNONCcut, self.indicesToyNONCcut)
        self.indicesToyNONCcutComp = cnor.indexFinder(self.CNOlistToy, self.ToyNONCcutComp)

        # expansion
        self.ToyNONCcutCompExp = cnor.expandGates(self.ToyNONCcutComp)

        # pre model
        self.resECNOlistToy = cnor.residualError(self.CNOlistToy)
        self.ToyFields4Sim = cnor.prep4sim(self.ToyNONCcutCompExp)
        self.initBstring = cnor.initBstring(self.ToyNONCcutCompExp.reacID)

        # GA algorithm
        # stupid values to make this execution quick 
        self.ToyT1opt = cnor.gaBinaryT1(cnolist=self.CNOlistToy,
                                        model=self.ToyNONCcutCompExp,
                                        initbstring=self.initBstring,
                                        popsize=4,maxgens=10, 
                                        stallgenmax=10, elitism=2, verbose=False)


    def test_gaT1(self):
        # check the output structure
        for x in ['bString','stringsTolScores','stringsTol','results']:
            assert x in list(self.ToyT1opt.names)

        cnor.plotFit(self.ToyT1opt)

    def test_read_midas(self):
        assert list(self.dataToy.DAcol) == [5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0]
        assert list(self.dataToy.DAcol) ==  list(self.dataToy.rx2('DAcol')) 

    def test_read_sif(self):
        # check the number of namesSpecies
        assert len(self.ToyModel.namesSpecies) == 15
        # and names in the reacId attribute.
        for reac in self.ToyModel.reacID:
            assert reac in ['!Akt=Mek', 'EGF=PI3K', 'EGF=Ras', 'Erk=Hsp27', 'Jnk=cJun', 'Mek=Erk', 'Mek=p90RSK', 'PI3K=Akt', 'Raf=Mek', 'Ras=Raf', 'TNFa=PI3K', 'TNFa=TRAF6', 'TRAF6=Jnk',  'TRAF6=NFkB', 'TRAF6=p38', 'p38=Hsp27']

    def test_checkSignals(self):
        cnor.checkSignals(self.CNOlistToy, self.ToyModel)

    def test_makeCNOlist(self):
        assert list(self.CNOlistToy.namesCues) == ['EGF', 'TNFa', 'Raf', 'PI3K']

    def test_findNONC(self):
        # nothing to do since NONC is empty
        self.ToyNONCindices

    def test_cutNONC(self):
        # nothing to do since NONC is empty
        self.ToyNONCcut

    def test_compressModel(self):
        # check the number of namesSpecies
        assert len(self.ToyNONCcutComp.namesSpecies) == 12
        # and names in the reacId attribute.
        for name in self.ToyNONCcutComp.namesSpecies:
            assert name in ["EGF", "TNFa","Jnk","PI3K","Raf", "Akt" ,"Mek","Erk"   , "NFkB",   "cJun",   "Hsp27",  "p90RSK"]


    def test_indexFinder(self):
        index = self.indicesToy
        assert list(index.inhibited) == [8, 6]
        assert list(index.stimulated) == [1, 2]
        assert list(index.signals) == [9, 14, 12, 11, 15, 4, 13]

    def test_plotcnoList(self):
        import tempfile
        f = tempfile.NamedTemporaryFile()
        cnor.plotCNOlist(self.CNOlistToy)
        cnor.plotCNOlistPDF(self.CNOlistToy, filename=f.name)
        
    def test_pre4sim(self):
        pass

    def test_residualError(self):
        assert_almost_equal(self.resECNOlistToy[0], 2.289, places=3)


def test_writeMIDAS():
    data = cnor.readMIDAS(midasfile)
    cnolist = cnor.makeCNOlist(data)

    import os
    cnor.writeMIDAS(cnolist, "test.csv")
    data2 = cnor.readMIDAS("test.csv")
    cnolist2 = cnor.makeCNOlist(data2)
    os.remove("test.csv")

def test_writeSIF():
    data = cnor.readMIDAS(midasfile)
    model = cnor.readSIF(siffile)
    cnolist = cnor.makeCNOlist(data)
    newmodel = cnor.preprocessing(cnolist, model)
    cnor.writeSIF(newmodel, "ToyModel2.sif")
    import os
    os.remove("ToyModel2.sif")


def test_computeScoreT1():
    data = cnor.readMIDAS(midasfile)
    model = cnor.readSIF(siffile)
    cnolist = cnor.makeCNOlist(data)

    newmodel = cnor.preprocessing(cnolist, model)
    a = cnor.computeScoreT1(cnolist, newmodel, [1]*16)
    assert_almost_equal(0.0947746, a)

    a = cnor.computeScoreT1(cnolist, newmodel, [1]*16, sizeFac=0.0001)
    assert_almost_equal(0.0947746, a)

    a = cnor.computeScoreT1(cnolist, newmodel, [1]*16, sizeFac=0.)
    assert_almost_equal(0.0946746, a)

    bestBS = [1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0]
    a = cnor.computeScoreT1(cnolist, newmodel, bestBS)
    assert_almost_equal(0.02964261, a)


def test_computeScoreTN():
    """These numbers are correct from version 1.3.19 of CellNOptR before using computeScoreT2"""
    # here we test computeScoreT2 so we need another data set that comprises
    # 2 time steps.
    data = cnor.readMIDAS(midasfile2)
    model = cnor.readSIF(siffile)
    cnolist = cnor.makeCNOlist(data)
    newmodel = cnor.preprocessing(cnolist, model)

    # best bitstring at time1 
    bestBS = [1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0]
    a = cnor.computeScoreT1(cnolist, newmodel, bestBS)
    assert_almost_equal(0.05927206, a)

    # a guess for time 2. Length is the number of zeros in bestBS
    bsT2 = [1,0,0,0,0,0,0] # must return 0.03805263

    # input to computeScoreT2
    simT1=cnor.simulateTN(cnolist, newmodel, [bestBS])

    a = cnor.computeScoreTN(cnolist, newmodel, bstrings=[bestBS, bsT2])
    assert_almost_equal(0.03805263, a)


