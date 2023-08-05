"""Unit test for CNO.cnor module"""
__author__ = "thomas cokelaer <cokelaer@ebi.ac.uk>"
from cellnopt.wrapper.data import get_data
from cellnopt.wrapper import CNORbool, CNORode, CNORfuzzy
import os
import glob
from os.path import join as pj

from nose.tools import assert_almost_equal

# the data file to be used for these tests 
#shared = pj(cno.__path__[0], '..','..','share', 'data')
midasfile = get_data('ToyModelMKM.csv')
siffile = get_data('ToyModelMKM.sif')


    
class TestCNORWrap():
    
    def __init__(self):
        #self.cnordata = cnor.CNORWrap(midasfile, siffile, verbose=False)
        #self.run()
        pass

    def test_run(self):
        self.cnordata = CNORbool(siffile, midasfile, verbose=True)
        #self.run()
        self.cnordata.preprocessing()
        self.cnordata.run(verbose=False, popsize=5, maxgens=20, stallgenmax=10, elitism=2)
        self.cnordata.plotCNO()
        self.cnordata.plotFit()
        self.cnordata.plotFit(plotting='R')
        self.cnordata.cutAndPlotResultsT1()
        self.cnordata.writeScaffold()
        self.cnordata.writeNetwork()
        #self.cnordata.writeReport()

    def test_attributes(self):
        try:
            self.verbose = True
            self.verbose = False
            self.verbose = 1
            assert False
        except:
            assert True
        try:
            self.debug = 0
            self.debug = 1
            self.debug = 'dummy'
            assert False
        except:
            assert True

        # readonly
        for a in ['data', 'model','tag','data_filename', 'model_filename']:
            try:
                setattr(self, a, 'dummy')
                assert False
            except:
                assert True

    def tearDown(self):
        import shutil
        import os
        #shutil.rmtree("CNORbool")
        import glob
        filenames = glob.glob("CNORbool*")
        for this in filenames: 
            os.remove(this)
        #except:
        #    pass

def _test_cnowrap_no_inputs():
    try:
        cnordata = CNORbool(midasfile='dummy') 
        assert False
    except:
        assert True

    try:
        cnordata = CNORbool(siffile='dummy') 
        assert False
    except:
        assert True



