 #! /usr/bin/env python
"""
Demo of StochPy Functionalities
===============================

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: July 09, 2012
"""

import stochpy
smod = stochpy.SSA()

class Demo():
    def __init__(self):     
        print "Welcome to the demo mode of StochPy, which currently consists out of 10 examples"
        raw_input("press any button to continue\n")   
        self.DoDemoSimulations()
       
    def Demo1(self):
        """ Use the Immigration-Death model for doing basic simulations with the Direct method, some plotting and exporting results """    
        print "\n### (1) Use the Immigration-Death model for doing basic simulations with the Direct method, some plotting and exporting of results ###"
        raw_input("press any button to continue\n")
        print ">>> smod = stochpy.SSA() # start SSA module"
        print ">>> smod.DoStochSim(IsTrackPropensities=True)"
        smod.DoStochSim(IsTrackPropensities=True)
        print ">>> smod.GetMeanWaitingtimes() # calculate mean waiting times"        
        smod.GetMeanWaitingtimes()
        print ">>> smod.PrintMeanWaitingtimes()"
        smod.PrintMeanWaitingtimes()          
        print ">>> smod.PlotTimeSim() # plot time course of species"
        smod.PlotTimeSim()
        print ">>> smod.PlotPropensities() # plot time course of propensities"
        smod.PlotPropensities()
        print ">>> smod.PlotWaitingtimes()"
        smod.PlotWaitingtimes()
        print ">>> smod.Export2File('TimeSim')"        
        smod.Export2File('TimeSim')
        print ">>> smod.Export2File('Waitingtimes')"
        smod.Export2File('Waitingtimes')
        print ">>> smod.Export2File('Propensities')"  
        smod.Export2File('Propensities')
        
    def Demo2(self):    
        """ Use the Immigration-Death model for a stochastic simulation with multiple trajectories """
        print "\n### (2) Use the Immigration-Death model for a stochastic simulation with multiple trajectories ###"
        raw_input("press any button to continue\n") 
        print ">>> smod.DoStochSim(trajectories=3,end=3000,mode='steps')  # multiple trajectories"       
        smod.DoStochSim(trajectories=3,end=3000) 
        print ">>> smod.PlotTimeSim()"
        smod.PlotTimeSim()   
        print ">>> smod.data_stochsim.simulation_trajectory # trajectory number"
        smod.data_stochsim.simulation_trajectory
        print ">>> smod.ShowMeans()"        
        smod.ShowMeans()
        print ">>> smod.ShowStandardDeviations"
        smod.ShowStandardDeviations()  
        print ">>> smod.GetTrajectoryData(1) # switch to data from trajectory 1"
        smod.GetTrajectoryData(1)      
        print ">>> smod.data_stochsim.simulation_trajectory # trajectory number"
        smod.data_stochsim.simulation_trajectory
        print ">>> smod.ShowMeans()"        
        smod.ShowMeans()
        print ">>> smod.ShowStandardDeviations"
        smod.ShowStandardDeviations()  
    
    def Demo3(self):
        """ Use the Immigration-Death model to demonstrate probability density functions """
        print "\n### (3) Use the Immigration-Death model to demonstrate probability density functions (10^6 time points) ###"
        raw_input("press any button to continue\n")     
        print ">>> smod.DoStochSim(trajectories=1,end=1000000,mode='steps')"
        smod.DoStochSim(trajectories=1,end=1000000,mode='steps')       
        print ">>> smod.PlotDistributions() # plot species distributions"
        smod.PlotDistributions()
        print ">>> smod.PlotDistributions(bin_size=5) # bin_size = 5"
        smod.PlotDistributions(bin_size=5)
        print ">>> smod.PlotDistributions(bin_size=10) # bin_size = 10"        
        smod.PlotDistributions(bin_size=10)
    
    def Demo4(self):
        """ Use Birth-Death model to illustrate the interpolation features """
        print "\n### (4) Use Birth-Death model to illustrate the interpolation features ###"
        raw_input("press any button to continue\n")     
        print ">>> smod.Model('dsmts-001-01.xml.psc') # parse a different model"
        smod.Model('dsmts-001-01.xml.psc')
        print ">>> smod.DoStochSim(trajectories=1000,end=50,mode='time')"
        smod.DoStochSim(trajectories=1000,end=50,mode='time') 
        print ">>> smod.GetInterpolatedData(frames=50)"
        smod.GetInterpolatedData(frames=50)
        print ">>> smod.PrintInterpolatedData()"        
        smod.PrintInterpolatedData()  
        print ">>> smod.PlotInterpolatedData()"
        smod.PlotInterpolatedData()  
        print ">>> smod.Export2File('Interpol')"
        smod.Export2File('Interpol')
        
    def Demo5(self):
        """ Use Decaying-Dimerizing model to illustrate performance differences between different stochastic simulation algorithms """
        print "\n### (5) Use Decaying-Dimerizing model to illustrate performance differences between different stochastic simulation algorithms ###"
        raw_input("press any button to continue\n")
        print ">>> smod.Model('DecayingDimerizing.psc')"
        smod.Model('DecayingDimerizing.psc')
        print ">>> smod.DoStochSim(method = 'Direct',trajectories=1,end=50,mode='time')"
        smod.DoStochSim(method = 'Direct',trajectories=1,end=50,mode='time')
        print ">>> smod.DoStochSim(method = 'FirstReactionMethod',trajectories=1,end=50,mode='time')"
        smod.DoStochSim(method = 'FirstReactionMethod',trajectories=1,end=50,mode='time')
        print ">>> smod.DoStochSim(method = 'NextReactionMethod',trajectories=1,end=50,mode='time')"
        smod.DoStochSim(method = 'NextReactionMethod',trajectories=1,end=50,mode='time')
        print ">>> smod.PlotWaitingtimes()"
        smod.PlotWaitingtimes() 
        print ">>> smod.DoStochSim(method = 'TauLeaping',trajectories=1,end=50,mode='time',epsilon=0.03) # should outperform all other implementations"
        smod.DoStochSim(method = 'TauLeaping',trajectories=1,end=50,mode='time',epsilon=0.03)
        print ">>> smod.PlotTimeSim()"
        smod.PlotTimeSim()
        print ">>> smod.PlotWaitingtimes() # should give an error"
        smod.PlotWaitingtimes()                 
        
    def Demo6(self):
        """ Demo of StochPy's next reaction method handling events"""
        print "\n### (6) Demo of StochPy's next reaction method handling events ###"
        raw_input("press any button to continue\n")
        print ">>> smod.Model('dsmts-003-03.xml.psc')"
        smod.Model('dsmts-003-03.xml.psc') 
        print ">>> smod.DoStochSim(method = 'NextReactionMethod',trajectories=1000,end=50,mode='time')"
        smod.DoStochSim(method = 'NextReactionMethod',trajectories=1000,end=50,mode='time')    
        print ">>> smod.PlotInterpolatedData()"
        smod.PlotInterpolatedData()

    def Demo7(self):
        """ Demo of StochPy's first reaction method handling events"""
        print "\n### (7) Demo of StochPy's first reaction method handling events ###"
        raw_input("press any button to continue\n")
        print ">>> smod.Model('dsmts-003-04.xml.psc')"
        smod.Model('dsmts-003-04.xml.psc') 
        print ">>> smod.DoStochSim(method = 'FirstReactionMethod',trajectories=1000,end=50,mode='time')"
        smod.DoStochSim(method = 'FirstReactionMethod',trajectories=1000,end=50,mode='time')    
        print ">>> smod.PlotInterpolatedData()"
        smod.PlotInterpolatedData() 

    def Demo8(self):
        """ Demo of StochPy's direct method for supporting events """
        print "\n### (8) Demo of StochPy's direct method handling events ###"
        raw_input("press any button to continue\n")
        print ">>> smod.Model('dsmts-02-10.xml.psc')"
        smod.Model('dsmts-002-10.xml.psc') 
        print ">>> smod.DoStochSim(method = 'Direct',trajectories=1000,end=50,mode='time')"
        smod.DoStochSim(method = 'Direct',trajectories=1000,end=50,mode='time')    
        print ">>> smod.PlotInterpolatedData()"
        smod.PlotInterpolatedData()        
    
    def Demo9(self):
        """  Demo of StochPy's direct method for handling volume and HasOnlySubstanceUnits """
        print "\n### (9) Demo of StochPy's direct method for handling volume and HasOnlySubstanceUnits ###"
        raw_input("press any button to continue\n")
        print ">>> smod.Model('dsmts-02-11.xml.psc')"
        smod.Model('dsmts-001-11.xml.psc')  
        print ">>> smod.DoStochSim(method = 'Direct',trajectories=1000,end=50,mode='time')"
        smod.DoStochSim(method = 'Direct',trajectories=1000,end=50,mode ='time')
        print ">>> smod.PlotInterpolatedData()"
        smod.PlotInterpolatedData()  

    def Demo10(self):
        """  Demo of StochPy for doing (preprogrammed) Sequential simulations """
        print "\n### (10) Demo of StochPy for doing (preprogrammed) Sequential simulations ###"
        raw_input("press any button to continue\n")
        print ">>> cmod = stochpy.CellDivision() # start cell division module"
        cmod = stochpy.CellDivision()
        print ">>> cmod.DoCellDivisionStochSim(distribution='normal',mean=2, sd=0.1,generations=3,trajectories=1)"
        cmod.DoCellDivisionStochSim(distribution='normal',mean=2, sd=0.1,generations=3,trajectories=1)
        print ">>> cmod.PlotTimeSim()"
        cmod.PlotTimeSim()
    
    def DoDemoSimulations(self):
        self.Demo1()
        self.Demo2()
        self.Demo3()
        self.Demo4()
        self.Demo5()
        self.Demo6()
        self.Demo7()
        self.Demo8()
        self.Demo9()
        self.Demo10()
