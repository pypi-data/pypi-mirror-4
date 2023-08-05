"""
StochPy Cell Division Module
============================

Example of a sequential simulator. This simulator tracks one cell for N generations. Different distributions (gamma, normal, lognormal) can be used to determine the next cell division time. Cell division is simulated with a binomial distribution.

Most of the functionalities of the SSA module such as plotting and writing to a file are also available in this module.

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: September 21, 2012
"""

############################## IMPORTS ###################################
import os,sys,copy,time
try: import numpy as np
except:
    print "Make sure that the NumPy module is installed"  
    print "This program does not work without NumPy"
    print "See http://numpy.scipy.org/ for more information about NumPy"
    sys.exit()

import stochpy.modules.StochSim as StochSim
import  stochpy.modules.Analysis as Analysis

class CellDivision():
    """
    Input options:     
     - *File*  [default = ImmigrationDeath.psc]
     - *dir*   [default = /home/user/stochpy/pscmodels/ImmigrationDeath.psc]     
     
    Usage (with High-level functions):
    >>> cmod = stochpy.CellDivision()
    >>> help(cmod)
    >>> cmod.DoCellDivisionStochSim()
    >>> cmod.DoCellDivisionStochSim(self,distribution = 'gamma',mean = 10, sd = 3,generations = 5,IsTrackPropensities=False)
    >>> cmod.Model(File = 'filename.psc', dir = '/.../')
    >>> cmod.Reload()
    >>> cmod.PlotTimeSim()
    >>> cmod.PlotPropensities()  
    >>> cmod.PlotWaitingtimes()
    >>> cmod.PlotDistributions(bin_size = 3)
    >>> cmod.ShowMeans()
    >>> cmod.ShowStandardDeviations()
    >>> cmod.ShowOverview()  
    >>> cmod.ShowSpecies()
    """
    def __init__(self,File = None,dir = None):
        print "Welcome to the Cell Division simulation module"
        if os.sys.platform != 'win32':
            output_dir = os.path.join(os.path.expanduser('~'),'Stochpy',)
            if File == dir == None:
                dir = os.path.join(os.path.expanduser('~'),'Stochpy','pscmodels')
                File = 'CellDivision.psc'
        else:
            output_dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy',)
            if File == dir == None:
                dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','pscmodels')
                File = 'CellDivision.psc'
        Method = 'Direct' # HARD CODED
        self.output_dir = output_dir
        self.model_dir = dir       
        self.ssa_mod = StochSim.SSA(Method,File,dir,Mode = 'time',IsInteractive=True,IsTrackPropensities=False)         
        try: 
            Analysis.plt.ion()   # Set on interactive pylab environment
        except Exception,er:
            print er            

    def Trajectories(self,n):
        """
        Set the number of trajectories to be generated
      
        Input:
         - *n* (int)
        """
        try: self.ssa_mod.sim_trajectories = int(n)
        except: print "Error: The number of trajectories must be a integer"
        
        
    def DoCellDivisionStochSim(self,distribution='normal',mean=1, sd=0.1,generations=2,trajectories=False,IsTrackPropensities=False):
        """ 
        Do stochastic simulations with cell divisions 
        
        Input:
         - *distribution* (string)
         - *mean* (float/int)
         - *sd* (float/int)
         - *generations* (int)
         - *IsTrackPropensities* (boolean)         
         
        Included distributions:
         - gamma
         - lognormal
         - normal        
         
        The Direct method is hardcoded
        """
        try: 
            del self.data_stochsim # remove old model data
            del self.data_stochsim_interpolated
        except: pass

        if trajectories != False: self.Trajectories(trajectories)
        self.ssa_mod.IsTrackPropensities=IsTrackPropensities
        self.ssa_mod.IsFastMethod = False
        self.ssa_mod.HasWaitingtimes = False
        self.ssa_mod.HasMeanWaitingtimes = False
        self.ssa_mod.HasInterpol = False       
          
        X_matrix = copy.deepcopy(self.ssa_mod.SSA.X_matrixinit)                
        try:
            self.ssa_mod.DeleteTempfiles()  # Delete '.dat' files
        except:
            pass    
        
        self.ssa_mod.sim_mode = 'celldivision'        
        if self.ssa_mod.sim_trajectories == 1: 
            print "Info: 1 trajectory is generated"
        else:
            file = open(os.path.join(self.output_dir,'ssa_sim.log'),'w')
            file.write("Trajectory\tNumber of time steps\tEnd time\n")
            print "Info: %s trajectories are generated"  % self.ssa_mod.sim_trajectories
            print "Info: Time simulation output of the trajectories is stored at %s in directory: %s" % (self.ssa_mod.model_file[:-4]+'(traj).dat',self.ssa_mod.temp_dir)
            print "Info: output is written to: %s" % os.path.join(self.ssa_mod.output_dir,'ssa_sim.log')
        t1 = time.time()
        for self.ssa_mod.traj in xrange(1,self.ssa_mod.sim_trajectories+1):            
            if distribution.lower() == 'gamma':
                self.cell_division_times = np.random.gamma(mean,sd,generations)
            elif distribution.lower() == 'lognormal':
                self.cell_division_times = np.random.lognormal(mean,sd,generations)        
            elif distribution.lower() == 'normal':
                self.cell_division_times = np.random.normal(mean,sd,generations)
                        
            self.cell_division_times =  abs(self.cell_division_times)                   
            self.ssa_mod.settings = StochSim.SSASettings(self.ssa_mod.SSA.X_matrixinit,10**10,0,0,self.ssa_mod.IsTrackPropensities) 
            for i in xrange(len(self.cell_division_times)):                               
                self.ssa_mod.settings.endtime += self.cell_division_times[i]                
                self.ssa_mod.SSA.Execute(self.ssa_mod.settings)  # hardcoded to the Direct SSA
                for j in xrange(self.ssa_mod.SSA.n_species): # divide each species between two cells with probability 0.5 according to a bin. dist.
                    species_amount = self.ssa_mod.SSA.sim_output[-1][1:][j]                
                    if species_amount:
                        self.ssa_mod.SSA.X_matrix[j] = np.random.binomial(species_amount,0.5,1)                
                 
                temp = copy.deepcopy(list(self.ssa_mod.SSA.X_matrix))
                temp.insert(0,self.cell_division_times[0:i+1].sum())
                temp.append(np.NAN)
                self.ssa_mod.SSA.sim_output[-1] = copy.copy(temp)                
                self.ssa_mod.settings.X_matrix = copy.copy(self.ssa_mod.SSA.X_matrix)  
                self.ssa_mod.settings.starttime += self.cell_division_times[i]               
                
            self.ssa_mod.FillDataStochsim()    
            self.ssa_mod.SSA.X_matrixinit = copy.deepcopy(X_matrix)
            if self.ssa_mod.sim_trajectories == 1: 
                print "Number of time steps %s End time %s" % (self.ssa_mod.SSA.timestep,self.ssa_mod.SSA.sim_t)
            elif self.ssa_mod.sim_trajectories > 1:
                self.ssa_mod.DumpTrajectoryData(self.ssa_mod.traj)        
        t2 = time.time()  
        self.simulation_time = t2-t1
        print "Simulation time: %s" % self.simulation_time
        self.ssa_mod.n_trajectories_simulated = copy.copy(self.ssa_mod.sim_trajectories)     
        self.ssa_mod.IsSimulationDone = True
        self.data_stochsim = copy.copy(self.ssa_mod.data_stochsim)        
        try: 
            self.ssa_mod.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.ssa_mod.SSA.rate_names,self.plot.plotnum)
        except: 
            self.ssa_mod.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.ssa_mod.SSA.rate_names)          

    def Model(self,File,dir = None): 
        """
        Give the model, which is used to do stochastic simulations on

        Input:
         - *File* filename.psc (string)
         - *dir* [default = None] the directory where File lives (string)
        """   
        self.ssa_mod.Model(File,dir)

    def Reload(self):
        """ Reload the entire model again. Useful if the model file has changed"""
        self.ssa_mod.Reload()
        
    def GetTrajectoryData(self,n=1):
        """ 
        Switch to another trajectory, by default, the last trajectory is accesible      
       
        Input:
         - *n* [default = 1] (int)
        """ 
        self.ssa_mod.GetTrajectoryData(n) 
        self.data_stochsim = copy.copy(self.ssa_mod.data_stochsim)
                       
    def DumpTrajectoryData(self,n):
        """ 
        Dump trajectory data
      
        Input:
         - *n* (int)
        """ 
        self.ssa_mod.DumpTrajectoryData(n)         

    def ShowSpecies(self):
        """ Print the species of the model """
        print self.ssa_mod.ShowSpecies()

    def ShowOverview(self):
        """ Print an overview of the current settings """
        self.ssa_mod.ShowOverview()
    
    def PlotTimeSim(self,maxpoints2plot = 10000,species2plot = True,linestyle = 'solid',marker = '',colors = None,title = 'StochPy Time Simulation Plot'):
        """
        Plot time simulation output for each generated trajectory
        Default: PlotTimeSim() plots time simulation for each species

        Input: 
         - *maxpoints2plot* [default = 10000] (integer)
         - *species2plot* [default = True] as a list ['S1','S2'] 
         - *linestyle* [default = 'solid'] dashed, solid, and dash_dot (string)
         - *marker* [default = ''] ('v','o','*',',')
         - *title* [default = 'StochPy Time Simulation Plot']  (string)
        """
        self.ssa_mod.PlotTimeSim(maxpoints2plot,species2plot,linestyle,marker,colors,title)

    def PlotDistributions(self,species2plot = True, linestyle = 'dotted',colors=None,title = 'StochPy Probability Density Function',bin_size=1):
        """
        Plots the PDF for each generated trajectory
        Default: PlotDistributions() plots PDF for each species

        Input:
         - *species2plot* [default = True] as a list ['S1','S2']
         - *linestyle* [default = 'dotted'] (string)
         - *colors* (list)
         - *title* [default = 'StochPy Probability Density Function'] (string)     
         - *bin_size* [default=1] (integer)
        """
        self.ssa_mod.PlotDistributions(species2plot,linestyle,colors,title,bin_size)
                
    def PlotPropensities(self,maxpoints2plot = 10000,rates2plot = True,linestyle = 'solid',marker = '',colors = None,title = 'StochPy Propensities Plot'):
        """ 
        Plot time simulation output for each generated trajectory

        Default: PlotPropensities() plots propensities for each species

        Input:
         - *maxpoints2plot* [default = 10000] (integer)
         - *rates2plot* [default = True]: species as a list ['S1','S2']
         - *marker* [default = ''] ('v','o','*',',')
         - *linestyle* [default = 'solid']: dashed, dotted, and solid (string)
         - *colors* [default = None] (list)
         - *title* [default = 'StochPy Propensities Plot'] (string)
        """
        self.ssa_mod.PlotPropensities(maxpoints2plot,rates2plot,linestyle,marker,colors,title)

    def GetWaitingtimes(self):
        """ Get for each reaction the waiting times """ 
        self.ssa_mod.GetWaitingtimes()

    def PlotWaitingtimes(self,rates2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Waitingtimes Plot'):
        """
        Plot obtained waiting times
        default: PlotWaitingtimes() plots waiting times for all rates
    
        Input:
         - *rates2plot* [default = True]  as a list of strings ["R1","R2"]
         - *linestyle* [default = 'None'] dashed, dotted, dash_dot, and solid (string)
         - *marker* [default = 'o'] ('v','o','*',',')
         - *colors* [default =  None] (list)
         - *title* [default = 'StochPy Waitingtimes Plot'] (string)
        """    
        self.ssa_mod.PlotWaitingtimes(rates2plot,linestyle,marker,colors,title)

    def GetInterpolatedData(self,frames=51):
        """
        Perform linear interpolation for each generated trajectory. Linear interpolation is done for all integer time points, between the start time (0) end the endtime.
    
        Input:
         - *frames* (int)
        """    
        self.ssa_mod.GetInterpolatedData(frames)
        
    def PlotInterpolatedData(self,species2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Interpolated Time Plot (# of trajectories = )'): 
        """
        Plot the averaged interpolation result. For each time point, the mean and standard deviation are plotted 
        
        Input:
         - *species2plot* [default = True] as a list ['S1','S2']
         - *linestyle* [default = 'dotted'] dashed, solid, and dash_dot (string)
         - *marker* [default = ','] ('v','o','*')
         - *colors* [default =  None] (list)
         - *title* [default = StochPy Interpolated Time (# of trajectories = ... ) ] (string)
        """      
        self.ssa_mod.PlotInterpolatedData(species2plot,linestyle,marker,colors,title)    
              
    def ShowMeans(self):
        """ Print the means of each species for the selected trajectory"""
        self.ssa_mod.ShowMeans()

    def ShowStandardDeviations(self):
        """ Print the standard deviations of each species for the selected trajectory"""      
        self.ssa_mod.ShowStandardDeviations()

    def Export2File(self,what='TimeSim', directory=None):
        """
        Export output to a file

        Input:
         - *what* [default = TimeSim] TimeSim, Propensities, Distributions, Waitingtimes, and Interpol (string)
         - *directory* [default = None] (string)
        """
        self.ssa_mod.Export2File(what,directory)
