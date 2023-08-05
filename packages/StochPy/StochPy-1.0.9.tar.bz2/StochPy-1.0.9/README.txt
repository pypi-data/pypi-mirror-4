StochPy Stochastic modeling in Python
=====================================

Copyright (c) 2010-2012, Timo R. Maarleveld, Brett G. Olivier, and Frank J. Bruggeman
All rights reserved.

StochPy is distributed under a BSD style licence.

Author information
------------------

Timo R. Maarleveld, Brett G. Olivier, Frank J. Bruggeman
Centrum Wiskunde en Informatica, Amsterdam, Netherlands
VU University, Amsterdam, Netherlands

e-mail: tmd200@users.sourceforge.net
web: http://sourceforge.net/projects/stompy/

Documentation can be found in the user guide (see Documentation directory)
One can find the stochastic testsuite files (.psc) in the added zip file

Installation
------------
The following software is required before installling StochPy:

- Python 2.x+
- NumPy 1.x+
- Matplotlib (optional)
- libsbml (optional)
- libxml2 (optional)

Linux/MAC OS/Cygwin
~~~~~~~~~~~~~~~~~~~

1) cd to directory StochPy-1.0.5
2) sudo python setup install

Windows
~~~~~~~
Use the available windows installer or the setup file

Usage
-----
>>> import stochpy
>>> help(stochpy)
>>> smod = stochpy.SSA()
>>> help(smod)
>>> smod.DoStochSim(IsTrackPropensities=1) # Do a stochastic time simulation
>>> smod.PlotTimeSim()  
>>> smod.PlotDistributions()
>>> smod.PlotPropensities()
>>> smod.GetWaitingtimes()
>>> smod.PlotWaitingtimes()
>>> smod.DoStochSim(trajectories = 10,method = 'Direct',end = 1000, mode = 'steps')
>>> smod.data_stochsim              # data object that stores the data of a simulation trajectory (See user guide)
>>> smod.data_stochsim.trajectory   # trajectory
>>> smod.GetTrajectoryData(3)       # Get data from the third trajectory
>>> smod.ShowMeans()                # shows the means of every species in the model for the selected trajectory (3)
>>> smod.ShowStandardDeviations()
>>> smod.GetInterpolatedData()
>>> smod.data_stochsim_interpolated # data object that stores the interpolated data
>>> smod.data_stochsim_interpolated.means # means for every time point
