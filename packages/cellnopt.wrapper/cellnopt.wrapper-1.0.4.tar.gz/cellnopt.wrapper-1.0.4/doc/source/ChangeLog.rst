Change Log
################

1.0
=====
1.0.4: 
    * remove numpy dependencies as much as possible. Still a method in cnor
      that uses it so it is not needed anymore in the setup. THere was also a
      dependency in cellnopt.data fixed in version 0.7.8 so this package requires
      cellnopt.data>=0.7.8
1.0.3:
    * install CellNOptR 1.4.0 automatically if not installed (other packages
	such as CNORode, fuzzy and dt are not installed automatically yet)
    * wrappers: small changes on the attributes
    * fix tests
	* wrapper_fuzzy: 
		* add these functions adding simFuzzyT1, computeScoreFuzzy, rpack_CNORfuzzy
		* fixed the require=1.0.0 when importing the package.
		* wrapper_fuzzy: add nTF=7 argument in defaultParametersFuzzy function
		* simlist argument in function interpretDiscreteGA is not needed anymore
		* fixing typo in intStringFuzzy
	* using CNOlist function instead of makeCNOlist whereever needed
	* cnor module: CNORfuzzy has a new property called stallGenMax
	* import cellnopt.data inside init

1.0.2:

1.0.1: 
	* remove pylab dependencies with warnings instead of errors.

1.0.0: 
	* renamed in cellnopt.wrapper

0.9
==========

0.9.27: 
	* uses rtools package ( tools module + some other functionalities)

0.9.26: 
	* uses new plotLBode function in wrapper_ode. fix bug in simulateT2

0.9.25: 
	* update to reflect major changes in CellNoptR (simlist and indices not
	  used), 
	* computeScoreT2 is called TN, similarly for gaBinaryT2. 
	* simulateT1 is now called simulateTN. 
	* cutandPlot replaces cutAndPlotT1, T2 and TN;

0.9.24: 
	* add missing data module, 
	* update preprocessing according to new R code.

0.9.23: 
	* fix init and wrappers so that it can be imported without the R 
	  packages instaled. useful for other R wrapping such as pymeigo. Fix tests.

0.9.17:
	* add Rplot decorator to have more flexibility on size of the R plots. 

0.9.16: 
	* add gabinaryT2 + cutAndplotResultsT2 in the class and fix related bug in the 
	  wrapper.	
	* add tools in CNORode to plot some results on k, n, tau + properties (e.g.,
	  best_score).
	* fix tests
	* rpackagse name starts with rpack prefix now.

0.9.15: fix bugs in tools (R tools)

0.9.14:

0.9.13: 
	* reflect changes made in CNO 1.3.19
	* add Base class in cnor module toease development of CNORode, CNORfuzzy and 
	  CNORbool classes
	* add tests
	* add computeScore in CNORode

0.9.12: 
	* make a robust Rdoc to sphinx doc parser, get back to makeCNOlist instead of makeCNOList

0.9.11: 
	* adapt computeScore arguments to the new API

0.9.10:

0.9.9: 
	* use new API (readSIF and prep4sim)

0.9.8: 
	* tests, uses preprocessing to replace previous calls to expandGates, compression, and cutnonc

0.9.7: 
	* add computeScore

0.9.5: 
	* documentation updated
