# -*- python -*-
#
#  This file is part of the cellnopt package
#
#  Copyright (c) 2011-2012 - EBI - EMBL
#
#  File author(s): Thomas Cokelaer (cokelaer@ebi.ac.uk)
#
#  Distributed under the GPL License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  ModelData website: http://www.ebi.ac.uk/~cokelaer/cellnopt
#
##############################################################################
import os

__all__ = ["get_data"]


def get_data(filename):
    """Look for a given file in the share data directory of pycno

    :param str filename: a filename without path
    :return: a filename with valid path to share directory of pycno


    There are two data files provided in cellnopt.wrapper:

    #. ToyModelMMKM (extension .sif or .csv)
    #. LiverDREAM (extensnio.sif and .csv)

    ::

        >>> from cno import tools
        >>> fullpathname = tools.locate_data('ToyModelMKM.sif')

    """
    from os.path import join as pj
    from os.path import isfile
    from os import sep

    # read the full path name of this file including the file itself, so we
    # split all directory and rebuild the path without the file
    # itself to obtain the directory. surely there is a better
    # solution...
    moduledir = sep.join(__file__.split(sep)[:-1])
    sharedir =   pj(moduledir, '..','..','share', 'data')

    # now, given the share direcotry, look for the file and
    # check its existence.
    filedir = pj(sharedir, filename)
    if isfile(filedir):
        return filedir

    # well, it seems it did not work (develop mode maybe ?). So, let us try
    # something else
    sharedir =   pj(moduledir, '..','share', 'data')
    filedir = pj(sharedir, filename)
    if isfile(filedir):
        return filedir

    raise IOError("file %s not found in %s" % (filename, sharedir)  )

