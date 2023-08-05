"""Unit test for CNO.cnor module"""
__author__ = "thomas cokelaer <cokelaer@ebi.ac.uk>"
from cellnopt.wrapper.data import get_data
try:
    from cellnopt.wrapper import CNORode
    ode = True
except:
    ode = False
    pass
import os
import glob
from os.path import join as pj

from nose.tools import assert_almost_equal

# the data file to be used for these tests 


class testCNORode():

    def __init__(self):
        model = get_data("ToyODE.sif")
        midas = get_data("ToyODE.csv")
        if ode == True:
            self.o = CNORode(model, midas)
        self.output = midas.replace('.csv','.png')

    def test_run(self):
        self.o.iters = 2
        self.o.maxtime = 4
        if ode == True:
            self.o.run(method='ga', buffering=True)
            self.o.plotLBodeFitness(filename=self.output, show=False)

    def test_computeScore(self):
        if ode == True:
            self.o.reset(random=True)
            self.o.computeScore()

            self.o.reset(random=False)
            res = self.o.computeScore(x=self.o.ode_parameters.parValues)
            assert_almost_equal(res, 0.056049272544896375)
