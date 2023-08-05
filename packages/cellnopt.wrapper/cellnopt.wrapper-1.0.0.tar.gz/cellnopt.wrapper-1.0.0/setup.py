# -*- coding: utf-8 -*-
__revision__ = "$Id: setup.py 2565 2012-10-17 13:29:07Z cokelaer $"
import sys
import os
from setuptools import setup, find_packages
import glob


_MAJOR               = 1
_MINOR               = 0
_MICRO               = 0
version              = '%d.%d.%d' % (_MAJOR, _MINOR, _MICRO)
release              = '%d.%d' % (_MAJOR, _MINOR)

metainfo = {
    'authors': {'Cokelaer':('Thomas Cokelaer','cokelaer@ebi.ac.uk')},
    'version': version,
    'license' : 'GPL',
    'download_url' : ['http://pypi.python.org/pypi/cellnopt.wrapper'],
    'url' : ['http://www.ebi.ac.uk/~cokelaer/cellnopt/wrapper'],
    'description':'CellNOpt R packages wrapper and utilities' ,
    'platforms' : ['Linux', 'Unix', 'MacOsX', 'Windows'],
    'keywords' : ['Graph Theory', 'Genetic Algorithm', 'Cell Theory',
        'Signalling Pathways', 'CellNOpt', 'rpy2', 'cno'],
    'classifiers' : [
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Scientific/Engineering :: Mathematics',
          'Topic :: Scientific/Engineering :: Physics']
    }


# todo : simplify this 
namespace = 'cellnopt'
pkg_root_dir = 'src'
pkgs = [ pkg for pkg in find_packages(pkg_root_dir)]
top_pkgs = [pkg for pkg in pkgs if  len(pkg.split('.')) < 2]
packages = pkgs
package_dir = dict( [('',pkg_root_dir)] + [(namespace + "." + pkg, pkg_root_dir + "/" + pkg) for pkg in top_pkgs] )

# files in share/data
datadir = os.path.join('share','data')
datafiles = [(datadir, [f for f in glob.glob(os.path.join(datadir, '*'))])]

setup(
    name             = 'cellnopt.wrapper',
    version          = version,
    maintainer       = metainfo['authors']['Cokelaer'][0],
    maintainer_email = metainfo['authors']['Cokelaer'][1],
    author           = metainfo['authors']['Cokelaer'][0],
    author_email     = metainfo['authors']['Cokelaer'][1],
    long_description = open("README.txt").read(),
    keywords         = metainfo['keywords'],
    description = metainfo['description'],
    license          = metainfo['license'],
    platforms        = metainfo['platforms'],
    url              = metainfo['url'],      
    download_url     = metainfo['download_url'],
    classifiers      = metainfo['classifiers'],

    # package installation
    packages = find_packages('src'),
    package_dir  = package_dir,
    namespace_packages = [namespace],
    #create_namespaces = True,
    install_requires = ['rpy2', 'rtools', "easydev>=0.5.0"],
    data_files = datafiles,
    )


