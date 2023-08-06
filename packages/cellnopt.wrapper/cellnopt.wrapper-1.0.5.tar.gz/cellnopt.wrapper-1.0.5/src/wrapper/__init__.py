import pkg_resources
try:
    version = pkg_resources.require("cellnopt.wrapper")[0].version
except:
    version = "unknown"


import tools as tools
from tools import *

import data
from data import get_data

import wrapper_cnor
from wrapper_cnor import *

import wrapper_ode
from wrapper_ode import *

import wrapper_fuzzy
from wrapper_fuzzy import *

import wrapper_dt
from wrapper_dt import *

import cnor
from cnor import *

import help
from help import *


from cellnopt.data import cnodata


def info():
    from rtools import RPackageManager
    pm = RPackageManager()
    import easydev
    print(easydev.underline("Available packages"))
    print( pm['CellNOptR'])
    print( pm['CNORode'])
    print( pm['CNORfuzzy'])
    print( pm['CNORdt'])
