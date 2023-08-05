The package **cellnopt.wrapper** provides a wrapper to the CellNOpt R packages using rpy2.
It allows to easily access to `CellNOptR
<http://bioconductor.org/packages/release/bioc/html/CellNOptR.html>`_ package
via python. In addition, a python class is provided to manipulate the package in
an object-oriented fashion. Similarly, other related R package are wrapped
(e.g., CNORode and CNORfuzzy, coming soon on bioconductor)


For instance, to access all CellNOptR functionalities, type::

    from cellnopt.wrapper import *


For a full documentation, see the sphinx documentation in the ./doc directory.

Please visit also `www.cellnopt.org <http://www.cellnopt.org>`_ for more information about CellNOpt.

