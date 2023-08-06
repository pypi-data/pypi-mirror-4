==========================
caspo :- PyASP, CellNOpt.
==========================

caspo combines PyASP_ and CellNOpt_ to provide an easy to use software for learning Boolean logic models of protein signaling networks from a prior knowledge network in `.sif format`_ and a phospho-proteomics dataset in `MIDAS format`_.

.. _PyASP: http://pypi.python.org/pypi/pyasp
.. _CellNOpt: http://www.ebi.ac.uk/saezrodriguez/cno/
.. _`.sif format`: http://wiki.cytoscape.org/Cytoscape_User_Manual/Network_Formats
.. _`MIDAS format`: http://www.ebi.ac.uk/saezrodriguez/cno/doc/cnodocs/midas.html

Installation
============

You can install caspo by running::

	$ pip install caspo

Note that you may need root (sudo) access for this. Otherwise, you can use a virtualenv_. Before using caspo make sure that R_ is already installed. The first time you run caspo, CellNOptR will be downloaded and installed in your R environment.

.. _R: http://www.r-project.org/
.. _virtualenv: http://pypi.python.org/pypi/virtualenv

Usage
=====

Typical usage is::
	
	$ caspo.py pkn.sif midas.csv
	
For more options you can ask for help as follows::

	$ caspo.py --help
	usage: caspo.py [-h] [--version] [--fit F] [--size S] [--discrete D] [--gtts]
	                [--cross N K] [--out O]
	                pkn midas

	positional arguments:
	  pkn           Prior knowledge network in SIF format
	  midas         Experimental dataset in MIDAS file

	optional arguments:
	  -h, --help    show this help message and exit
	  --version     show program's version number and exit
	  --fit F       suboptimal enumeration tolerance (Default to 0)
	  --size S      suboptimal size enumeration tolerance (Default to 0). Combined
	                with --fit could lead to a huge number of models
	  --discrete D  discretization over [0,D] (Default to 100)
	  --gtts        compute Global Truth Tables (Default to False). This could
	                take some time for many models.
	  --cross N K   compute N random K-fold cross validation
	  --out O       output directory path (Default to current directory)
	
Samples
=======

Sample files are available for the `prior knowledge network`_ and the `phospho-proteomics dataset`_

.. _`prior knowledge network`: http://www.cs.uni-potsdam.de/~sthiele/bioasp/downloads/samples/liverdata/ExtLiverPCB.sif
.. _`phospho-proteomics dataset`: http://www.cs.uni-potsdam.de/~sthiele/bioasp/downloads/samples/liverdata/ExtLiverPCB.csv

Output
======

By default, the output of caspo will be 4 comma-separated-values files:
	- models.csv: Matrix representation of logic models
	- frequencies.csv: Frequencies of hyperedges occurrence
	- exclusive.csv: Mutual exclusives hyperedges with their corresponding frequencies
	- inclusive.csv: Mutual inclusives hyperedges with their corresponding frequencies

When using the --gtts option, caspo will also output:
	- gtts_stats.csv: Basic cluster analysis.
	- gtt-%i.csv: Explicit computation of each Global Truth Table

When using the --cross N K option, caspo will also output:
	- cross_validation_%i.csv: K-fold cross validation report for each of the N runs

