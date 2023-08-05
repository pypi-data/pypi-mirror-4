# -*- python -*-
# -*- coding: utf-8 -*-
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
# $Id: tools.py 2565 2012-10-17 13:29:07Z cokelaer $
"""Utilities for cellnopt.wrapper

Created by Thomas Cokelaer <cokelaer@ebi.ac.uk>
Copyright (c) 2011. GPL

.. testsetup:: *

    from rpy2.robjects.packages import importr
    import numpy
    from cno import *

"""
__author__ = """\n""".join(['Thomas Cokelaer <cokelaer@ebi.ac.uk'])


__all__ = ['require']

import logging
import os
import rpy2
from rpy2 import robjects
from rpy2.robjects import rinterface
from rpy2.robjects.packages import importr
from rpy2.robjects import r
 


# decorator with arguments and optional arguments for a method
def require(*args_deco, **kwds_deco):
    """Decorator for class method to check if an attribute exist

    .. doctest::

        from cno.tools import require

        class Test(object):
            def __init__(self):
               self.m = 1
            @require('m')
            def print(self):
                print self.m
        t = Test()
        t.print()


    """
    if len(args_deco) != 2:
        raise ValueError()
    attribute = args_deco[0]
    msg = args_deco[1]

    if len(attribute.split('.'))>2:
        raise AttributeError('This version of require decorator introspect only 2 levels')

    def decorator(func):
        # func: function object of decorated method; has
        # useful info like f.func_name for the name of
        # the decorated method.

        def newf(*args, **kwds):

            # This code will be executed in lieu of the
            # method you've decorated.  You can call the
            # decorated method via f(_args, _kwds).
            names = attribute.split('.')

            if len(names) == 1:
                if hasattr(args[0], attribute):
                   return func(*args, **kwds)
                else:
                   raise AttributeError('%s not found. %s' % (names, msg))
            elif len(names) == 2:
                if hasattr(getattr(args[0], names[0]), names[1]):
                    return func(*args, **kwds)
                else:
                   raise AttributeError('%s not found. %s' % (names, msg))


        newf.__name__ = func.__name__
        newf.__doc__ = func.__doc__
        return newf

    return decorator







