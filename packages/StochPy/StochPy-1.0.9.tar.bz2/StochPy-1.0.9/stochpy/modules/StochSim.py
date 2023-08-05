 #! /usr/bin/env python
"""
Stochastic Simulation Module
============================

The main module of StochPy

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: July 9, 2012
"""

############################ IMPORTS ################################

from math import ceil
import sys,copy,time,os,getopt,cPickle,string,subprocess,cStringIO,shutil,bisect

try: 
    import numpy as np  
except:
    print "Make sure that the NumPy module is installed"  
    print "This program does not work without NumPy"
    print "See http://numpy.scipy.org/ for more information about NumPy"
    sys.exit()

import stochpy.modules.Analysis as Analysis
from stochpy.modules.PyscesMiniModel import InterpolatedDataObj
from stochpy.modules.PyscesMiniModel import IntegrationStochasticDataObj

try: 
    import stochpy.modules.InterfaceCain as InterfaceCain    
    IS_STOCHPY_CAIN = True
except: 
    IS_STOCHPY_CAIN = False

try: 
    import stochpy.modules.InterfaceStochKit as InterfaceStochKit
    import PSC2StochkitXML
    InterfaceStochKit.DeleteExistingData()
    IS_STOCHPY_KIT = True
except:
    IS_STOCHPY_KIT = False

import stochpy.implementations as implementations

class SSASettings():
    """   
    Input:
     - *X_matrix* (array)
     - *timesteps* (integer)
     - *starttime* (float)
     - *endtime* (float)
     - *istrackpropensities* (boolean)
    """
    def __init__(self,X_matrix,timesteps,starttime,endtime,istrackpropensities):
        self.X_matrix = X_matrix
        self.timesteps = timesteps
        self.starttime = starttime
        self.endtime = endtime
        self.IsTrackPropensities = istrackpropensities

############################ END IMPORTS ############################

class SSA():
  """
  SSA(Method='Direct',File=None,dir=None,Mode='steps',End=1000,Trajectories=1,IsInteractive=True,IsTrackPropensities=False)
  
  Input options:
   - *Method* [default = 'Direct'], Available methods: 'Direct', 'FirstReactionMethod','TauLeaping','Next Reaction Method'
   - *File* [default = ImmigrationDeath.psc]
   - *dir* [default = /home/user/stochpy/pscmodels/ImmigrationDeath.psc]
   - *Mode* [default = 'steps'] simulation for a total number of 'steps' or until a certain end 'time' (string)
   - *End* [default = 1000] end of the simulation (number of steps or end time)   (float)   
   - *Trajectories* [default = 1] (integer)
   - *TrackPropensities* [default = False] (Boolean)
  
  Usage (with High-level functions):
  >>> smod = stochpy.SSA()
  >>> help(smod)
  >>> smod.Model(File = 'filename.psc', dir = '/.../')
  >>> smod.Method('Direct')
  >>> smod.Reload()
  >>> smod.Trajectories(5)
  >>> smod.Timesteps(10000)
  >>> smod.TrackPropensities()
  >>> smod.DoStochSim()
  >>> smod.DoStochSim(end=1000,mode='steps',trajectories=5,method='Direct')
  >>> smod.PlotTimeSim()
  >>> smod.PlotPropensities()
  >>> smod.PlotInterpolatedData()
  >>> smod.PlotWaitingtimes()
  >>> smod.PlotDistributions(bin_size = 3)
  >>> smod.ShowMeans()
  >>> smod.ShowStandardDeviations()
  >>> smod.ShowOverview()
  >>> smod.ShowSpecies()
  >>> smod.DoTestsuite()
  """
  def __init__(self,Method='Direct',File=None,dir=None,Mode='steps',End=1000,Trajectories=1,IsInteractive=True,IsTrackPropensities=False):
    if os.sys.platform != 'win32':
        output_dir = os.path.join(os.path.expanduser('~'),'Stochpy',)
        temp_dir = os.path.join(os.path.expanduser('~'),'Stochpy','temp',)
        if File == dir == None:
            dir = os.path.join(os.path.expanduser('~'),'Stochpy','pscmodels')
            File = 'ImmigrationDeath.psc'
    else:
        output_dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy',)
        temp_dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','temp',)
        if File == dir == None:
            dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','pscmodels')
            File = 'ImmigrationDeath.psc'
    
    self.IsInteractive = IsInteractive
    self.model_file = File
    self.model_dir = dir
    self.output_dir = output_dir
    self.temp_dir = temp_dir
    self.Method(Method)
    self.sim_end = End
    self.sim_mode = Mode
    self.sim_trajectories = Trajectories    
    self.IsFrameSolverInit = True
    self.IsTrackPropensities = IsTrackPropensities
    self.IsSimulationDone = False
    self.IsFrameMethod = False
    self.HasWaitingtimes = False
    self.HasInterpol = False
    self.sim_dump = []
    if self.IsInteractive:
        try: 
            Analysis.plt.ion()   # Set on interactive pylab environment
        except Exception,er:
            print er
            
  def Method(self,method):
    """
    Method(method)
    
    Input:
     - *method* (string)

    Select one of the following four methods:    
     - *Direct*
     - *FirstReactionMethod*
     - *NextReactionMethod*
     - *TauLeaping*
     
    Note: input must be a string --> 'Direct' (not case sensitive)
    """
    self.IsTauLeaping = False
    IsNRM = False
    if method.lower() == 'direct':
        import stochpy.implementations.DirectMethod as DirectMethod
        self.sim_method = DirectMethod.DirectMethod
        print "Info: Direct method is selected to perform stochastic simulations"
        self.sim_method_name = "Direct"
    elif method.lower() == 'firstreactionmethod':
        import stochpy.implementations.FirstReactionMethod as FRM
        self.sim_method = FRM.FirstReactionMethod
        self.sim_method_name = "FirstReactionMethod"
        print "Info: First Reaction method is selected to perform stochastic simulations"
    elif method.lower() == 'tauleaping':
        import stochpy.implementations.TauLeaping as TauLeaping
        self.sim_method = TauLeaping.OTL
        self.sim_method_name = "TauLeaping"
        print "Info: Optimized Tau-Leaping method is selected to perform stochastic simulations"
        print "Info: User can change the 'epsilon' parameter with DoStochSim(epsilon = 0.01)"
        self.IsTauLeaping = True
    elif method.lower() == 'nextreactionmethod':
        import stochpy.implementations.NextReactionMethod as NRM
        self.sim_method = NRM.NextReactionMethod
        print "Info: Next Reaction method is selected to perform stochastic simulations"
        IsNRM = True
        self.sim_method_name = "NextReactionMethod"
    else:
        print "Error: Only valid options are: 'Direct', 'FirstReactionMethod', 'NextReactionMethod','TauLeaping'."
        print "Info: By default, the Direct method is selected"
        import stochpy.implementations.DirectMethod as DirectMethod
        self.sim_method = DirectMethod.DirectMethod
        self.sim_method_name = "Direct"

    self.SSA = self.sim_method(self.model_file,self.model_dir,self.output_dir,self.temp_dir)
    self.IsSimulationDone = False
    self.HasWaitingtimes = False
    self.HasMeanWaitingtimes = False
    self.HasInterpol = False
    
  def Timesteps(self,s):
      """
      Timesteps(s)
      
      Set the number of time steps to be generated for each trajectory
      
      Input:
       - *s* number of time steps (integer)
      """
      try:
          self.sim_end  = int(s)
          self.sim_mode = 'steps'
          print "Info: The number of time steps is: %s" % self.sim_end
      except:
          print "Error: The number of time steps must be an integer"

  def Endtime(self,t):
      """
      Endtime(t)
      
      Set the end time of the exact realization of the Markov jump process
      
      Input:
       - *t* (float)
      """    
      try:
          self.sim_end  = float(t)
          self.sim_mode = 'time'
          print "Info: The simulation end time is: %s" % self.sim_end
      except:
          print "Error: The end time must be an integer/float"

  def Trajectories(self,n):
      """
      Trajectories(n)
      
      Set the number of trajectories to be generated
      
      Input:
       - *n* (integer)
      """
      try:
          self.sim_trajectories = int(n)
      except:
          print "Error: The number of trajectories must be an integer"

  def Reload(self):
      """ Reload the entire model again. Useful if the model file has changed"""
      self.SSA.Parse(self.model_file,self.model_dir)
      self.model_file = self.SSA.ModelFile 
      self.model_dir = self.SSA.ModelDir
      self.IsSimulationDone = False
      self.HasWaitingtimes = False 
      self.HasMeanWaitingtimes = False
      self.HasInterpol = False

  def Model(self,File,dir=None):
      """
      Model(File,dir=None)
      
      Select model for simulation
            
      Input:
       - *File* filename (string)
       - *dir* [default = None] the directory where File is located (string)
      """    
      if self.IsSimulationDone:
          try: 
              del self.data_stochsim # Remove old model data
              del self.data_stochsim_interpolated
          except:
              pass                   # no previous simulations to delete
      self.model_file = File
      if dir != None: 
          self.model_dir = dir
      self.Reload()

  def Mode(self,sim_mode='steps'):
      """
      Mode(sim_mode='steps')
      
      Run a stochastic simulation for until `end` is reached. This can be either time steps or end time (which could be a *HUGE* number of steps).

      Input:
       - *sim_mode* [default = 'steps'] 'time' or 'steps'
       - *end* [default = 1000]   
      """
      self.sim_mode = sim_mode.lower()
      if self.sim_mode.lower() not in ['steps','time']:
          print "Mode '%s' not recognised using: 'steps'" % sim_mode
          self.sim_mode = 'steps'

  def GetTrajectoryData(self,n=1):
      """ 
      GetTrajectryData(n=1)
      
      Switch to another trajectory, by default, the last trajectory is accesible      
      
      Input:
       - *n* [default = 1] (integer)
      """ 
      try:      
          file_in = open(os.path.join(self.temp_dir,self.model_file+str(n)+'.dat'),'r')
          self.data_stochsim = cPickle.load(file_in)
      except:
          print "Error: trajectory %s does not exist" % n 

  def DumpTrajectoryData(self,n):
      """ 
      DumpTrajectoryData(n)
      
      Input:
       - *n* (integer)
      """ 
      try:    
          file_name = os.path.join(self.temp_dir,self.model_file+str(n)+'.dat')
          cPickle.dump(self.data_stochsim,file = open(file_name,'w'))
          self.sim_dump.append(file_name)
      except:
          print "Error: trajectory %s does not exist" % n 
          
  def ChangeParameter(self,parameter,value):
      """
      ChangeParameter(parameter,value)     
      
      Input:
       - parameter (string)
       - value (float)
      """
      if type(parameter) == str and (type(value) == float or type(value) == int):   
          try:
              self.SSA.parse.Mod.__pDict__[parameter]['initial'] = float(value)
              self.SSA.parse.BuildReactions()
              self.SSA.propensities = copy.deepcopy(self.SSA.parse.propensities) 
          except Exception,er:
              print er
              print "Parameters are: %s" % (sorted(self.SSA.parse.Mod.__pDict__))
      else:
          print "Error: parameter = string and value = float"   

  def ChangeInitialSpeciesAmount(self,species,value):
      """
      ChangeInitialSpeciesAmount(species,value)     
      
      Input:
       - species (string)
       - value (float)
      """
      if type(species) == str and (type(value) == float or type(value) == int):   
          try:
              self.SSA.parse.Mod.__sDict__[species]['initial'] = float(value)
              self.SSA.parse.BuildX()     
              self.SSA.X_matrixinit = copy.deepcopy(self.SSA.parse.X_matrix.transpose()[0])         
          except Exception,er:
              print er
              print "Species are: %s" % (sorted(self.SSA.parse.Mod.__sDict__))
      else:
          print "Error: parameter = string and value = float"       
  
      
  def DoStochKitStochSim(self,endtime=100,frames=10000,trajectories=False,IsTrackPropensities=False,customized_reactions=None,solver=None,keep_stats = False,keep_histograms = False):
      """
      DoStochKitStochSim(endtime=100,frames=10000,trajectories=False,IsTrackPropensities=False,customized_reactions=None,solver=None,keep_stats = False,keep_histograms = False)
      
      Do Stochastic simulations with StochKit in StochPy
      Make sure that the input file contains net stoichiometries
      
      Input:
       - *endtime* [default = 100] (float)
       - *frames* [default = 10000] (integer)
       - *trajectories* [default = False] (integer)
       - *IsTrackPropensities* [default = False] (boolean)
       - *customized_reactions* [default=None] (list of strings)
       - *solver* [default = None] (string)
       - *keep_states* [default = False] (boolean)
       - *keep_histograms* [default = False) (boolean)
      """      
      if IS_STOCHPY_KIT:      
          try:                        # remove pot. old model data
              del self.data_stochsim
              del self.data_stochsim_interpolated
          except:
              pass                   # no previous simulations to delete
      
          try: 
              self.DeleteTempfiles() # Delete '.dat' files
          except:
              pass                   # not '.dat' files to delete
          
          if self.IsFrameSolverInit:
              print "Warning: do not use net stoichiometries for framed-based simulators. Use X > {2}  in stead of $pool > X"
              self.IsFrameSolverInit= False              
          
          self.IsFrameMethod = True
          self.IsSimulationDone = False
          self.HasWaitingtimes = False
          self.HasMeanWaitingtimes = False
          self.IsTrackPropensities = IsTrackPropensities
          self.HasInterpol = False
          if trajectories != False:
              self.Trajectories(trajectories)                   
          stochkit_model_filename = self.model_file.split('.')[0]+'_stochkit.xml'          
          if customized_reactions != None:
              for reaction in customized_reactions:
                  r_index = self.SSA.rate_names.index(reaction)
                  self.SSA.parse.rate_eqs[r_index]['stochtype'] = 'customized'
                  
          IsSupported = True
          if self.SSA.aDict != {}:
              print "Error: StochKit solvers do not support assignments. Use the StochPy solvers DoStochSim()"
              IsSupported = False  
              
          if IsSupported: 
              if solver == None:                  
                  solver = InterfaceStochKit.STOCHKIT_SOLVER # use the default solver
          
              t1 = time.time()
              doc = PSC2StochkitXML.xml_createStochKitDoc(self.SSA)
              PSC2StochkitXML.xml_viewStochKitXML(doc,fname=os.path.join(self.temp_dir,stochkit_model_filename))          
              stochkit_model_filename_path = os.path.join(self.temp_dir, stochkit_model_filename)            
              stochkit_keep_stats = keep_stats
              stochkit_keep_histograms = keep_histograms
              stochkit_keep_trajectories = True
              stochkit_cmd = "-m %s -t%s -r%s -i%s --label -f" % (stochkit_model_filename_path,endtime,self.sim_trajectories ,frames)
              if not stochkit_keep_stats:
                  stochkit_cmd += " --no-stats"
              if stochkit_keep_histograms:
                  stochkit_cmd += " --keep-histograms"
              if stochkit_keep_trajectories:
                  stochkit_cmd += " --keep-trajectories"
              stochkit_cmd += " --out-dir %s" % (os.path.join(InterfaceStochKit.STOCHKIT_WORK_DIR,stochkit_model_filename))
          
              if self.sim_trajectories == 1:                  
                  print "Info: %s trajectory is generated until t = %s with %s frames" % (self.sim_trajectories,endtime,frames)
              else:                  
                  print "Info: %s trajectory are generated until t = %s with %s frames" % (self.sim_trajectories,endtime,frames)    
              try: 
                  solver_path = os.path.join(InterfaceStochKit.STOCHKIT_SOLVER_DIR, solver)
                  rcode = subprocess.call([solver_path, stochkit_cmd]) 
                  IsSimulation = True
              except Exception,er:
                  print er, solver_path
                  IsSimulation = False
                  
              if IsSimulation:    
                  t2 = time.time()    
                  self.simulation_time = t2-t1              
                  print "Simulation time including compiling %s" % self.simulation_time
                  if self.IsTrackPropensities:
                      print "Parsing data to StochPy and calculating propensities and distributions ..."
                  else:
                      print "Parsing data to StochPy and calculating distributions ..."
                  self.data_stochsim = InterfaceStochKit.GetStochKitOutput(stochkit_model_filename,self.SSA,endtime,self.sim_trajectories,frames,self.IsTrackPropensities)
                  
                  self.n_trajectories_simulated = copy.copy(self.sim_trajectories)
                  try:
                      self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names,self.plot.plotnum)
                  except:
                      self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names)
                  self.IsSimulationDone = True
                  print "Data successfully parsed into StochPy"
      else:
          raise RuntimeError, "\nError: StochKit and/or InterfaceStochKit is not installed or the directories in InterfaceStochKit.ini are incorrect"             
     
  def DoCainStochSim(self,endtime=100,frames=10000,trajectories=False,solver="HomogeneousDirect2DSearch",IsTrackPropensities=False):
      """      
      DoCainStochSim(endtime=100,frames=10000,trajectories=False,solver="HomogeneousDirect2DSearch",IsTrackPropensities=False)
      
      Use Cain implementations for frame-based stochastic simulations (www.cacr.caltech.edu/~sean/cain/DeveloperFile)
      Make sure that the input file contains net stoichiometries
      
      Input:
       - *endtime* [default = 100](float)
       - *frames* [default = 10000] (integer)
       - *trajectories* [default = False] (integer)
       - *solver* [default = HomogeneousDirect2DSearch] (string)
       - *IsTrackPropensities* [default = False] (boolean)
      """     
      if IS_STOCHPY_CAIN:      
          print "Warning: only mass-action kinetics can be correctly parsed by the Cain solvers"       
          try:                        # remove pot. old model data
              del self.data_stochsim  
              del self.data_stochsim_interpolated
          except:
              pass
      
          try:
              self.DeleteTempfiles() # Delete '.dat' files
          except:
              pass

          if self.IsFrameSolverInit:
              print "Warning: do not use net stoichiometries for framed-based simulators. Use X > {2} in stead of $pool > X"
              self.IsFrameSolverInit = False
      
          self.IsFrameMethod = True
          self.IsTrackPropensities = IsTrackPropensities
          self.HasInterpol = False  
          self.HasWaitingtimes = False
          self.HasMeanWaitingtimes = False   
          self.IsSimulationDone = False
          IsSupported = True
          if trajectories != False:
              self.Trajectories(trajectories)
     
          mersenne_twister_data = InterfaceCain.getCainInputfile(self.SSA,endtime,frames,self.sim_trajectories)            
          cain_cmd_filename = 'cain_in.txt'
          cmd_file = file(os.path.join(self.temp_dir, cain_cmd_filename), 'r')
          cain_cmd = cmd_file.read()
          cmd_file.close()
      
          if self.SSA.parse.Events != {}:
              print "Error: Cain solvers do not support events. Use the StochPy solvers DoStochSim()"
              IsSupported = False          
          if self.SSA.aDict != {}:
              print "Error: Cain solvers do not support assignments. Use the StochPy solvers DoStochSim()"
              IsSupported = False             
              
          try:
              if os.sys.platform == 'win32' and not solver.endswith('.exe'):
                  solver = solver.split('.')[0] + '.exe'
                 
              solver_path = os.path.join(InterfaceCain.CAIN_SOLVER_PATH,solver)  
              proc = subprocess.Popen(os.path.join(InterfaceCain.CAIN_SOLVER_PATH,solver),stdin=subprocess.PIPE,stdout=subprocess.PIPE) 
              IsFoundSolver = True
          except Exception,er:
              print er,solver_path 
              IsFoundSolver = False    
          
          if IsFoundSolver and IsSupported:
              if self.sim_trajectories == 1:                  
                  print "Info: %s trajectory is generated until t = %s with %s frames" % (self.sim_trajectories,endtime,frames)
              else:                  
                  print "Info: %s trajectory are generated until t = %s with %s frames" % (self.sim_trajectories,endtime,frames)   
              t1 = time.time()     
              stdout_values = proc.communicate(cain_cmd)[0]                  
              # TODO: remove the out_file part if we completely understand it
              #out_file = file(os.path.join(self.temp_dir, CAIN_CMD_FILENAME.replace('.txt','.out.txt')),'w')      
              #out_file.write(stdout_values)
              #out_file.flush()
              #out_file.close()
              t2 = time.time()       
              self.simulation_time = t2-t1            
              print "Simulation time %s" % self.simulation_time
              if self.IsTrackPropensities:
                  print "Parsing data to StochPy and calculating propensities and distributions ..."
              else:
                  print "Parsing data to StochPy and calculating distributions ..."
              cain_out = cStringIO.StringIO(stdout_values).readlines()          
              self.data_stochsim = InterfaceCain.getCainOutput2StochPy(cain_out,mersenne_twister_data,self.SSA,endtime,self.sim_trajectories,frames,self.IsTrackPropensities)
              self.n_trajectories_simulated = copy.copy(self.sim_trajectories)
              try: 
                  self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names,self.plot.plotnum)
              except:
                  self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names)
              self.IsSimulationDone = True
              print "Data successfully parsed into StochPy"
      else:
          raise RuntimeError, "\nError: InterfaceCain is not installed"
  
  def DoStochSim(self,end=False,mode=False,method=False,trajectories=False,epsilon = 0.03,IsTrackPropensities=False):
      """
      DoStochSim(end=10, mode='steps', method='Direct',trajectories = 1,epsilon = 0.03,IsTrackPropensities = False)

      Run a stochastic simulation for until `end` is reached. This can be either time steps or end time (which could be a *HUGE* number of steps).

      Input:
       - *end* [default=1000] simulation end (steps or time)
       - *mode* [default='steps'] simulation mode, can be one of:
         - *steps* (string) total number of steps to simulate
         - *time* (string) simulate until time is reached
       - *method* [default='Direct'] stochastic algorithm, can be one of:
         - Direct
         - FirstReactionMethod
         - NextReactionMethod
         - TauLeaping
       - *trajectories* [default = 1] number of trajectories
       - *epsilon* [default = 0.03] parameter for Tau-Leaping
       - *IsTrackPropensities* [default = False]
      """
      if mode != False:         
          self.Mode(sim_mode = mode)         
      if end != False:    
          if type(end) == int or type(end) == float or type(end) == np.float64: 
              self.sim_end = end      
          else:
              print "Error: end should be an integer or float\n 1000 is used by default"
              self.sim_end = 1000   
      try: 
          del self.data_stochsim    # remove old model data
          del self.data_stochsim_interpolated
      except:
          pass                      # no previous simulations to delete

      if method != False: 
          self.Method(method)
      if trajectories != False: 
          self.Trajectories(trajectories)
      self.IsTrackPropensities = IsTrackPropensities
      self.IsFrameMethod = False
      self.HasWaitingtimes = False
      self.HasMeanWaitingtimes = False
      self.HasInterpol = False
      try: 
          self.DeleteTempfiles()  # Delete '.dat' files
      except:
          pass                    # No '.dat' files to delete
    
      if self.sim_trajectories == 1:
          print "Info: 1 trajectory is generated"
      else: 
          file = open(os.path.join(self.output_dir,'ssa_sim.log'),'w')
          file.write("Trajectory\tNumber of time steps\tEnd time\n")
          print "Info: %s trajectories are generated"  % self.sim_trajectories
          print "Info: Time simulation output of the trajectories is stored at %s in directory: %s" % (self.model_file[:-4]+'(traj).dat',self.temp_dir)
          print "Info: output is written to: %s" % os.path.join(self.output_dir,'ssa_sim.log')
      t1 = time.time()
      for self.traj in xrange(1,self.sim_trajectories+1):
          if self.sim_method_name == "TauLeaping":
              if self.sim_mode == 'time':
                  self.settings = SSASettings(self.SSA.X_matrixinit,10**10,0,self.sim_end,self.IsTrackPropensities)
                  self.SSA.Execute(self.settings,epsilon)
              elif self.sim_mode == 'steps':
                  self.settings = SSASettings(self.SSA.X_matrixinit,self.sim_end,0,10**10,self.IsTrackPropensities)  
                  self.SSA.Execute(self.settings,epsilon)
              else:
                  print "Error: simulation mode should be 'time' or 'steps'. Steps is done by default"
                  self.settings = SSASettings(self.SSA.X_matrixinit,self.sim_end,0,10**10,self.IsTrackPropensities)  
                  self.SSA.Execute(self.settings,epsilon)
          else:
              if self.sim_mode == 'time':
                  self.settings = SSASettings(self.SSA.X_matrixinit,10**10,0,self.sim_end,self.IsTrackPropensities)
                  self.SSA.Execute(self.settings)
              elif self.sim_mode == 'steps':
                  self.settings = SSASettings(self.SSA.X_matrixinit,self.sim_end,0,10**10,self.IsTrackPropensities)          
                  self.SSA.Execute(self.settings)
              else:
                  self.settings = SSASettings(self.SSA.X_matrixinit,self.sim_end,0,10**10,self.IsTrackPropensities)   
                  print "Error: simulation mode should be 'time' or 'steps'. Steps is done by default"
                  self.SSA.Execute(self.settings)  
          self.FillDataStochsim() 
          if self.sim_trajectories == 1:
              print "Number of time steps %s End time %s" % (self.SSA.timestep,self.SSA.sim_t)
          elif self.sim_trajectories > 1:
              self.DumpTrajectoryData(self.traj)
      t2 = time.time()
      self.simulation_time = t2-t1
      print "Simulation time: %s" % self.simulation_time   
      self.IsSimulationDone = True
      self.n_trajectories_simulated = copy.copy(self.sim_trajectories)
      try: 
          self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names,self.plot.plotnum)
      except:
          self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names) 

  def DoCompleteStochSim(self,error = 0.001,size=100000):
      """      
      DoCompleteStochSim(self,error = 0.001,size=100000)
      
      Do stochsim until the first four moments converge (in development, alpha-status)
      
      Input:
       - *error* maximal allowed error
       - *size* (integer) number of steps before checking the first four moments
      """
      try: 
          del self.data_stochsim    # remove old model data
          del self.data_stochsim_interpolated
      except:
          pass                      # no previous simulations to delete
     
      self.Trajectories(1)
      self.IsTrackPropensities =  False
      self.IsFrameMethod = False
      self.HasWaitingtimes = False
      self.HasMeanWaitingtimes = False
      self.HasInterpol = False
      try: 
          self.DeleteTempfiles()  # Delete '.dat' files
      except:
          pass                    # No '.dat' files to delete    
      
      self.traj = 1
      t1 = time.time()
      self.settings = SSASettings(self.SSA.X_matrixinit,size,0,10**10,self.IsTrackPropensities)          
      self.SSA.Execute(self.settings)      
      (dist, means, sds,moments) = self.GetDistributions()  
      
      m1 = [np.array(moments[species].values()) for species in self.SSA.species]      
      IsContinue = True
      i=1
      data = []
      while IsContinue:          
          settings = SSASettings(self.SSA.X_matrix,size*(i+1),self.SSA.sim_t,10**10,self.IsTrackPropensities)          
          self.SSA.Execute(settings)
          (dist, means, sds,moments) = self.GetDistributions()          
          m2 = [np.array(moments[species].values()) for species in self.SSA.species] 
          max_total = 0
          for j in xrange(self.SSA.n_species):                            
              max_s = abs(1-(m2[j]/m1[j])).max()
              if max_s > max_total:
                   max_total = max_s          
          data.append(max_total)
          m1 = copy.deepcopy(m2)      
          i+=1     
          if max_total < error:
              IsContinue = False                  
      t2 = time.time()
      self.simulation_time = t2-t1
      print "Simulation time: %s" % self.simulation_time  
      self.FillDataStochsim()     
      self.IsSimulationDone = True
      self.n_trajectories_simulated = copy.copy(self.sim_trajectories)
      try: 
          self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names,self.plot.plotnum)
      except:
          self.plot = Analysis.DoPlotting(self.data_stochsim.species_labels,self.SSA.rate_names)          
          
  def PlotTimeSim(self,n_events2plot = 10000,species2plot = True,linestyle = 'solid',marker = '',colors = None,title = 'StochPy Time Simulation Plot'):
      """
      PlotTimeSim(n_events2plot = 10000,species2plot = True,linestyle = 'solid',marker = '',colors = None,title = 'StochPy Time Simulation Plot')
      
      Plot time simulation output for each generated trajectory
      Default: PlotTimeSim() plots time simulation for each species

      Input:
       - *n_events2plot* [default = 10000] (integer)
       - *species2plot* [default = True] as a list ['S1','S2'] 
       - *linestyle* [default = 'solid'] dashed, solid, and dash_dot (string)
       - *marker* [default = ''] ('v','o','*',',')
       - *title* [default = 'StochPy Time Simulation Plot']  (string)
      """
      IsPlot = True
      if not self.IsSimulationDone: 
          print  "Before plotting time simulation results first do a stochastic simulation"
          IsPlot = False
      else:    
          if species2plot == True: 
              species2plot = self.data_stochsim.species_labels
          if type(species2plot) == str:
              species2plot = [species2plot]    
          for species in species2plot:
              if species not in self.data_stochsim.species_labels:
                  print "Error: species %s is not in the model" % species
                  IsPlot = False
      if IsPlot:
          if str(n_events2plot).lower() == 'all':
              n_events2plot = self.data_stochsim.simulation_timesteps
          try:    
              traj = 1
              while traj <= self.n_trajectories_simulated:
                  if self.n_trajectories_simulated > 1:
                      self.GetTrajectoryData(traj)
                  self.plot.TimeSimulation(self.data_stochsim.getSpecies(),n_events2plot,species2plot,traj-1,linestyle,marker,colors,title) # Plot time sim
                  traj+=1
              if traj > 1:
                  self.plot.plotnum+=1
          except Exception, ex:                
              print ex
              print "Error: Matplotlib is probably not available\nInfo: Use the Export2File() function"
 
  def PrintTimeSim(self):
      """ Print time simulation output for each generated trajectory"""
      IsPrint = True
      if not self.IsSimulationDone: 
          print  "Before printing time simulation results first do a stochastic simulation"
          IsPrint = False
      if IsPrint:
          traj = 1
          while traj <= self.n_trajectories_simulated:
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(traj)
              print 'Time\t',
              for species in self.data_stochsim.species_labels:
                  print '%s\t' % (species),
              print ''
              for timepoint in self.data_stochsim.getSpecies():
                  for value in timepoint:
                      print '%s\t' % (value),
                  print ''
              traj+=1

  def PlotPropensities(self,n_events2plot = 10000,rates2plot = True,linestyle = 'solid',marker = '',colors = None,title = 'StochPy Propensities Plot'):
      """
      PlotPropensities(n_events2plot = 10000,rates2plot = True,linestyle = 'solid',marker = '',colors = None,title = 'StochPy Propensities Plot')
      
      Plot time simulation output for each generated trajectory

      Default: PlotPropensities() plots propensities for each species

      Input:
       - *n_events2plot* [default = 10000] (integer)
       - *rates2plot* [default = True]: species as a list ['S1','S2']
       - *marker* [default = ''] ('v','o','*',',')
       - *linestyle* [default = 'solid']: dashed, dotted, and solid (string)
       - *colors* [default = None] (list)
       - *title* [default = 'StochPy Propensities Plot'] (string)
      """
      IsPlot = True
      if not self.IsTrackPropensities or not self.IsSimulationDone:
          print  "Error: before plotting propensities first do a stochastic simulation with tracking propensities (use the IsTrackPropensities flag in DoStochSim)"
          IsPlot = False
      else:
          if rates2plot  == True:
              rates2plot = self.SSA.rate_names
          if type(rates2plot) == str:
              rates2plot = [rates2plot]    
          for r in rates2plot:
              if r not in self.SSA.rate_names:
                  print "Error: species %s is not in the model" % r
                  IsPlot = False
      if IsPlot:
           if str(n_events2plot).lower() == 'all':
               n_events2plot = self.data_stochsim.simulation_timesteps           
           traj = 1
           try:
               while traj <= self.n_trajectories_simulated:	
                   if self.n_trajectories_simulated > 1:
                       self.GetTrajectoryData(traj)
                   self.plot.Propensities(self.data_stochsim.getPropensities(),n_events2plot,rates2plot,traj-1,linestyle,marker,colors,title)
                   traj+=1
               if traj > 1:
                   self.plot.plotnum+=1
           except Exception, ex:                
               print ex
               print "Error: Matplotlib is probably not available\nInfo: Use the Export2File() function"

  def PrintPropensities(self):
      """ Print time simulation output for each generated trajectory"""
      IsPrint = True
      if not self.IsTrackPropensities or not self.IsSimulationDone:
          print  "Error: before plotting propensities first do a stochastic simulation with tracking propensities (use the IsTrackPropensities flag in DoStochSim)"
          IsPrint = False
      if IsPrint:
          traj = 1
          while traj <= self.n_trajectories_simulated:	
              if self.n_trajectories_simulated > 1:        
                  self.GetTrajectoryData(traj)
              print 'Time\t',
              #for rate in self.data_stochsim.propensities_labels:
              for rate in self.SSA.rate_names: 
                  print '%s\t' % (rate),
              print ''
              for timepoint in self.data_stochsim.getPropensities():    
                  for value in timepoint:
                       print '%s\t' % (value),
                  print ''
              traj+=1

  def PlotDistributions(self,species2plot = True, linestyle = 'dotted',colors=None,title = 'StochPy Probability Density Function',bin_size=1):
      """
      PlotDistributions(species2plot = True, linestyle = 'dotted',colors=None,title = 'StochPy Probability Density Function',bin_size=1)
      
      Plots the PDF for each generated trajectory
      Default: PlotDistributions() plots PDF for each species

      Input:
       - *species2plot* [default = True] as a list ['S1','S2']

       - *linestyle* [default = 'dotted'] (string)

       - *colors* (list)
       - *title* [default = 'StochPy Probability Density Function'] (string)     
       - *bin_size* [default=1] (integer)
      """
      IsPlot = True
      if not self.IsSimulationDone: 
          print "Error: Before plotting distributions first do a stochastic simulation"
          IsPlot = False
      else:
          if species2plot == True: species2plot = self.data_stochsim.species_labels
          if type(species2plot) == str: species2plot = [species2plot]        
          for species in species2plot:
              if species not in self.data_stochsim.species_labels:
                  print "Error: species %s is not in the model" % species
                  IsPlot = False
      if IsPlot:
          try:
              traj = 1
              while traj <= self.n_trajectories_simulated:    
                  if self.n_trajectories_simulated > 1:
                      file_in = open(os.path.join(self.temp_dir,self.model_file+str(traj)+'.dat'),'r')	# Open dumped output
                      self.data_stochsim = cPickle.load(file_in)
                  self.plot.Distributions(self.data_stochsim.distributions,species2plot,traj-1,linestyle,colors,title,bin_size)	# Plot dist
                  traj+=1      
              if traj > 1: 
                  self.plot.plotnum += 1
          except Exception, ex:                
              print ex
              print "Error: Matplotlib is probably not available\nInfo: Use the Export2File() function"

  def PrintDistributions(self):
      """ Print obtained distributions for each generated trajectory """
      IsPrint = True
      if not self.IsSimulationDone: 
          print  "Error: Before printing distributions first do a stochastic simulation"
          IsPrint = False
      if IsPrint:
          traj = 1
          while traj <= self.n_trajectories_simulated:    
              if self.n_trajectories_simulated > 1:  
                  self.GetTrajectoryData(traj)  

              for species in self.data_stochsim.distributions:
                  print "Position\tProbability"            
                  for i in xrange(len(species[0])):
                      print "%s\t%s" % (species[0][i],species[1][i])
              traj+=1

  def GetWaitingtimes(self):
      """ Get for each reaction the waiting times """ 
      IsGetWaitingtimes = True   
      if not self.IsSimulationDone:
          print "Error: before getting waiting times first do a stochastic simulation (and do not use the Tau-Leaping method)"
          IsGetWaitingtimes = False
      if self.IsTauLeaping:
          print "Error: Tau-Leaping method does not allow for calculation of waiting times"
          IsGetWaitingtimes = False
      elif self.IsFrameMethod:
          print "Error: Frame-based implementations do not allow for calculation of waiting times"
          IsGetWaitingtimes = False        
      if IsGetWaitingtimes:
          traj = 1
          waitingtimes = []
          while traj <= self.n_trajectories_simulated:
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(traj)
              waitingtimes = Analysis.ObtainWaitingtimes(self.data_stochsim,self.SSA.n_reactions)
              self.data_stochsim.setWaitingtimes(waitingtimes)
              if self.n_trajectories_simulated > 1:
                  self.DumpTrajectoryData(traj)           
              traj+=1
          self.HasWaitingtimes = True  
    
  def PlotWaitingtimes(self,rates2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Waitingtimes Plot'):
      """
      PlotWaitingtimes(rates2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Waitingtimes Plot')
      
      default: PlotWaitingtimes() plots waiting times for all rates
    
      Input:
       - *rates2plot* [default = True]  as a list of strings ["R1","R2"]
       - *linestyle* [default = 'None'] dashed, dotted, dash_dot, and solid (string)
       - *marker* [default = 'o'] ('v','o','*',',')
       - *colors* [default =  None] (list)
       - *title* [default = 'StochPy Waitingtimes Plot'] (string)
      """    
      IsPlot = True
      if not self.HasWaitingtimes and not self.IsTauLeaping: self.GetWaitingtimes() # If not calculated 
      if self.IsTauLeaping:
          print "Error: Tau-Leaping method does not allow for calculation of waiting times"
          IsPlot = False
        
      if rates2plot  == True: rates2plot = self.SSA.rate_names
      if type(rates2plot) == str: rates2plot = [rates2plot]
      for r in rates2plot:
          if r not in self.SSA.rate_names:
              print "Error: reaction %s is not in the model" % r
              IsPlot = False

      if IsPlot and self.HasWaitingtimes:
          try:
              traj = 1
              while traj <= self.n_trajectories_simulated:
                  if self.n_trajectories_simulated > 1:
                      self.GetTrajectoryData(traj)
                  self.plot.Waitingtimes(self.data_stochsim.waiting_times,rates2plot,traj-1,linestyle,marker,colors,title)              
                  traj+=1
              self.plot.plotnum+=1
          except Exception, ex:                
              print ex
              print "Error: Matplotlib is probably not available\nInfo: Use the Export2File() function"

  def PrintWaitingtimes(self):
      """ Print obtained waiting times """
      IsPrint = True
      if not self.HasWaitingtimes and not self.IsTauLeaping: 
          self.GetWaitingtimes()
      if self.IsTauLeaping:
          print "Error: Tau-Leaping method does not allow for calculation of waiting times"
          IsPrint = False
      if IsPrint and self.HasWaitingtimes:
          traj = 1
          while traj <= self.n_trajectories_simulated:
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(traj)
              waiting_times = self.data_stochsim.waiting_times
              for r in waiting_times:
                  print "Waiting times\t%s" % self.SSA.rate_names[int(r)-1]
                  waiting_times_r = waiting_times[r]
                  for time in waiting_times_r: 
                      print time
              traj+=1

  def GetMeanWaitingtimes(self):
      """ Get the mean waiting times for the selected trajectory """
      if not self.HasWaitingtimes: 
          self.GetWaitingtimes()      
      if self.HasWaitingtimes:          
          traj = 1
          while traj <= self.n_trajectories_simulated:
              if self.n_trajectories_simulated > 1:
                      self.GetTrajectoryData(traj)          
              self.data_stochsim.setMeanWaitingtimes(self.data_stochsim.waiting_times)
              if self.n_trajectories_simulated > 1:
                  self.DumpTrajectoryData(traj) 
              traj+=1    
          self.HasMeanWaitingtimes = True

  def PrintMeanWaitingtimes(self):
      """ Print the mean waiting times for the selected trajectory """
      IsPrint = True
      if not self.HasMeanWaitingtimes and not self.IsTauLeaping: 
          self.GetMeanWaitingtimes()
      if self.IsTauLeaping:
          print "Error: Tau-Leaping method does not allow for calculation of waiting times"
          IsPrint = False
      
      if IsPrint and self.HasMeanWaitingtimes:    
          traj = 1
          while traj <= self.n_trajectories_simulated:  
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(traj)
              print "Reaction\tMean Waiting times"    
              i=0
              for rate in self.SSA.rate_names: 
                  print "%s\t%s" % (rate,self.data_stochsim.mean_waitingtimes[i])              
                  i+=1
              traj+=1

  def GetInterpolatedData(self,frames=51):
      """
      GetInterpolatedData(frames=51)
      
      Perform linear interpolation for each generated trajectory. Linear interpolation is done for all integer time points, between the start time (0) end the end time.
     
      Input:
       - *frames* (integer)
      """    
      if not self.IsSimulationDone: 
          print  "Error: before getting interpolated data first  do a stochastic simulation (with multiple trajectories)"         
      else:
          self.data_stochsim_interpolated = InterpolatedDataObj()    
          n_species = len(self.data_stochsim.species_labels)          
          self.data_stochsim_interpolated.species = [[] for i in xrange(n_species)]      
      
          if self.sim_mode == 'time':
              self.data_stochsim_interpolated.points = np.linspace(0,self.sim_end,frames)
          else:    
              simulation_endtimes = []
              traj = 1
              while traj <= self.n_trajectories_simulated:
                  if traj > 1: self.GetTrajectoryData(traj)
                  simulation_endtimes.append(self.data_stochsim.simulation_endtime)        
                  traj+=1
              min_simulation_endtime = min(simulation_endtimes)        
              self.data_stochsim_interpolated.points = np.linspace(0,min_simulation_endtime,frames)    
          traj = 1
          while traj <= self.n_trajectories_simulated:
              if self.n_trajectories_simulated > 1:
                  self.GetTrajectoryData(traj)        
              interpolated_output = np.zeros([len(self.data_stochsim_interpolated.points),n_species])
              i = 0
              for time_point in self.data_stochsim_interpolated.points:
                  time_index = bisect.bisect(self.data_stochsim.time,time_point)-1 # last time event before change
                  interpolated_output[i] = self.data_stochsim.species[:][time_index]
                  i+=1
              for i in xrange(n_species):
                  self.data_stochsim_interpolated.species[i].append(interpolated_output[:,i])
              traj+=1
          self.data_stochsim_interpolated.means,self.data_stochsim_interpolated.standard_deviations = Analysis.ObtainInterpolationResults(self.data_stochsim_interpolated.species,self.data_stochsim_interpolated.points)
          self.data_stochsim_interpolated.time = copy.deepcopy(self.data_stochsim_interpolated.points)
          self.HasInterpol = True

  def PrintInterpolatedData(self):    
      """ Analyse the interpolated output for each generated trajectory """
      if not self.HasInterpol:
          self.GetInterpolatedData()
      if self.HasInterpol:
          print "t",
          for species in self.data_stochsim.species_labels:              
              print "\t%s (Mean)\t%s (SD)" % (species,species),             
          print
          means = np.transpose(self.data_stochsim_interpolated.means)
          sds = np.transpose(self.data_stochsim_interpolated.standard_deviations)
          t=0
          for time_point in self.data_stochsim_interpolated.time: 
              print time_point,"\t",
              for i in xrange(len(self.data_stochsim_interpolated.means)): 
                  print "%s\t%s\t" % (means[t][i],sds[t][i]),
              print ""
              t+=1

  def PlotInterpolatedData(self,species2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Interpolated Time Plot (# of trajectories = )'): 
      """
      PlotInterpolatedData(species2plot = True,linestyle = 'None',marker = 'o',colors = None,title = 'StochPy Interpolated Time Plot (# of trajectories = )')
      
      Plot the averaged interpolation result. For each time point, the mean and standard deviation are plotted 
      
      Input:
       - *species2plot* [default = True] as a list ['S1','S2']
       - *linestyle* [default = 'dotted'] dashed, solid, and dash_dot (string)
       - *marker* [default = ','] ('v','o','*')
       - *colors* [default =  None] (list)
       - *title* [default = StochPy Interpolated Time (# of trajectories = ... ) ] (string)
      """      
      if not self.HasInterpol: 
          self.GetInterpolatedData()
      if self.HasInterpol:
          IsPlot = True     
          if species2plot == True: species2plot = self.data_stochsim.species_labels
          if type(species2plot) == str: species2plot = [species2plot]
          for species in species2plot:
              if species not in self.data_stochsim.species_labels:
                  print "Error: species %s is not in the model" % (species)
                  IsPlot = False      
          if title == 'StochPy Interpolated Time Plot (# of trajectories = )':
              title = title.replace('= ','= %s' % self.n_trajectories_simulated)
      if self.HasInterpol and IsPlot:      
          try:
              self.plot.AverageTimeSimulation(self.data_stochsim_interpolated.means,self.data_stochsim_interpolated.standard_deviations,self.data_stochsim_interpolated.time,species2plot,linestyle,marker,colors,title)
          except Exception, ex:                
              print ex
              print "Error: Matplotlib is probably not available\nInfo: Use the Export2File() function"
          self.plot.plotnum+=1

  def ShowMeans(self):
      """ Print the means of each species for the selected trajectory"""
      if not self.IsSimulationDone: 
          print "Before showing the means, do a stochastic simulation first"
      else:
          print "Species\tMean"   
          for species in self.data_stochsim.species_labels:         
              print "%s\t%s"  % (species,self.data_stochsim.means[species])

  def ShowStandardDeviations(self):
      """ Print the standard deviations of each species for the selected trajectory"""  
      if not self.IsSimulationDone: 
          print "Before showing the standard deviations, do a stochastic simulation first"
      else:          
          print "Species\t","Standard Deviation"
          for species in self.data_stochsim.species_labels:          
              print "%s\t%s"  % (species,self.data_stochsim.standard_deviations[species])
             
  def Write2File(self,what='TimeSim',directory=None):
      """
      Write2File(what='TimeSim',directory=None)
      
      Old Function: New function is Export2File
      Export output to a file

      Input:
       - *what* [default = TimeSim] TimeSim, Propensities, Distributions, Waitingtimes, and Interpol (string)
       - *directory* [default = None] (string)
      """
      self.Export2File(what, directory)
    
  def Export2File(self,what='TimeSim', directory=None):
    """    
    Export2File(what='TimeSim', directory=None)    

    Input:
     - *what* [default = TimeSim] TimeSim, Propensities, Distributions, Waitingtimes, and Interpol (string)
     - *directory* [default = None] (string)
    """
    IsExport2File = True
    if directory == None:
        directory = os.path.join(self.output_dir,self.model_file+'_' + what)
    else:
        if not os.path.exists(directory):
            os.makedirs(directory)
        directory = os.path.join(directory,self.model_file+'_' + what)
    if what.lower() == 'timesim':
        if not self.IsSimulationDone:
            print  "Before writing the time simulation to a file first do a stochastic simulation"
            IsExport2File = False
        if IsExport2File:
            traj = 1
            while traj <= self.n_trajectories_simulated:
                if self.n_trajectories_simulated > 1:
                    self.GetTrajectoryData(traj)
                file_path = directory+str(traj)+'.txt'	# Dir/Filename
                file_out = open(file_path,'w')
                for timepoint in self.data_stochsim.getSpecies():                    
                    slist = [str(value) for value in timepoint]
                    line = "\t".join(slist) 
                    line += '\n'
                    file_out.write(line)
                traj+=1
                file_out.close()
                print "Time simulation output is successfully saved at: %s" % file_path
    elif what.lower() == 'propensities':
        IsExport2File = True
        if not self.IsTrackPropensities or not self.IsSimulationDone:
            print  "Before writing propensities to a file first do a stochastic simulation with tracking propensities (use the IsTrackPropensities flag in DoStochSim)"
            IsExport2File = False
        if IsExport2File:
            traj = 1
            while traj <= self.n_trajectories_simulated:
                if self.n_trajectories_simulated > 1:
                    self.GetTrajectoryData(traj)
                file_path = directory+str(traj)+'.txt'
                file_out = open(file_path,'w')        
                for timepoint in self.data_stochsim.getPropensities(): 
                    slist = [str(value) for value in timepoint]
                    line = "\t".join(slist) 
                    line += '\n'
                    file_out.write(line)
                traj+=1
                file_out.close()
                print "Propensities output is successfully saved at: %s" % file_path
    elif what.lower() == 'distributions':
        if not self.IsSimulationDone:
            print  "Before writing distributions to a file first do a stochastic simulation"
            IsExport2File = False
        if IsExport2File:
            traj = 1 
            while traj <= self.n_trajectories_simulated:    
                if self.n_trajectories_simulated > 1:
                    self.GetTrajectoryData(traj)
                file_path = directory+str(traj)+'.txt'
                file_out = open(file_path,'w')  
                for species in self.data_stochsim.distributions:
                    file_out.write("Position\tProbability\n")
                    for i in xrange(len(species[0])):                         
                        file_out.write("%s\t%s\n" % (species[0][i],species[1][i]))               
                traj+=1 
                file_out.close()
                print "Distributions output is successfully saved at: %s" % file_path
    elif what.lower() == 'waitingtimes':
        IsPrint = True
        if not self.HasWaitingtimes and not self.IsTauLeaping: 
            self.GetWaitingtimes()
        if self.IsTauLeaping:
            print "Error: Tau-Leaping method does not allow for calculation of waiting times"
            IsPrint = False
        if IsPrint and self.HasWaitingtimes:              
            traj = 1
            while traj <= self.n_trajectories_simulated:
                if self.n_trajectories_simulated > 1:
                    self.GetTrajectoryData(traj)
                file_path = directory+str(traj)+'.txt'
                file_out = open(file_path,'w')  
                for r in self.data_stochsim.waiting_times:
                    file_out.write("Waitingtimes\t%s\n"  % (self.SSA.rate_names[int(r)-1]))
                    waiting_times_r = self.data_stochsim.waiting_times[r]
                    for time in waiting_times_r:
                        file_out.write("%s\n" % time)
                traj+=1
                file_out.close()
                print "Waiting times output is successfully saved at: %s" % file_path
    elif what.lower() == 'meanwaitingtimes':
        IsPrint = True
        if not self.HasMeanWaitingtimes and not self.IsTauLeaping: 
            self.GetMeanWaitingtimes()
        if self.IsTauLeaping:
            print "Error: Tau-Leaping method does not allow for calculation of waiting times"
            IsPrint = False
        if IsPrint and self.HasMeanWaitingtimes:        
            traj=1            
            while traj <= self.n_trajectories_simulated:            
                if self.n_trajectories_simulated > 1:
                    self.GetTrajectoryData(traj)
                file_path = directory+str(traj)+'.txt'
                file_out = open(file_path,'w')                      
                file_out.write("Reaction\tMean Waiting times\n")
                i=0
                for rate in self.SSA.rate_names: 
                    file_out.write("%s\t%s\n" % (rate,self.data_stochsim.mean_waitingtimes[i]))              
                    i+=1
                traj+=1
                file_out.close()
                print "Mean waiting times output is successfully saved at: %s" % file_path                
    elif what.lower() == 'interpol':
        if not self.HasInterpol:
            self.GetInterpolatedData()
        if self.HasInterpol:
            file_path = directory + '.txt'
            file_out = open(file_path,'w')
            file_out.write("t")
            for species in self.data_stochsim.species_labels:
                file_out.write("\t%s (Mean)\t%s (SD)" % (species,species))   
            file_out.write("\n")
            means = np.transpose(self.data_stochsim_interpolated.means)
            sds = np.transpose(self.data_stochsim_interpolated.standard_deviations)       
            t=0        
            for time_point in self.data_stochsim_interpolated.time: 
                file_out.write("%s\t" % time_point)
                for i in xrange(len(self.data_stochsim_interpolated.means)):
                    file_out.write("%s\t%s\t" % (means[t][i],sds[t][i]))                   
                file_out.write("\n")
                t+=1  
            print "Interpolation output is successfully saved at: %s" % file_path
    else:
        print "Error: The only valid options are: 'TimeSim', 'Propensities', 'Distributions', 'Waitingtimes', 'MeanWaitingtimes', and 'Interpol'"
        print "Info: smod = stochpy.SSA()\nInfo: smod.Export2File('Distributions')"

  def ShowSpecies(self):
      """ Print the species of the model """
      print self.data_stochsim.species_labels

  def ShowOverview(self):
      """ Print an overview of the current settings """
      print "Current Model:\t%s" % self.model_file
      if self.sim_mode == "steps": 
          print "Number of time steps:\t%s" % self.sim_end
      elif self.sim_mode == "time":
          print "Simulation end time:\t%s" % self.sim_end
      print "Current Algorithm:\t%s" % self.sim_method
      print "Number of trajectories:\t%s" % self.sim_trajectories
      if self.IsTrackPropensities:
           print "Propensities are tracked"
      else:
           print "Propensities are not tracked"

  def DeleteTempfiles(self):
      """ Deletes all .dat files """
      for line in self.sim_dump: os.remove(line)

  def DoTestsuite(self,epsilon_ = 0.01,sim_trajectories=1000):
      """
      DoTestsuite(epsilon_ = 0.01,sim_trajectories=1000)
      
      Do "sim_trajectories" simulations until t=50 and print the interpolated result for t = 0,1,2,...,50
      
      Input:
       - *epsilon_* [default = 0.01]: useful for tau-Leaping simulations (float)
       - *sim_trajectories* [default = 1000]
      """
      self.sim_end = 50
      self.sim_mode = "time"
      self.sim_trajectories = sim_trajectories
      self.DoStochSim(epsilon = epsilon_) 
      self.PrintInterpolatedData()    
      self.sim_end = 1000 # Reset settings to default values
      self.sim_mode = "steps"
      self.sim_trajectories = 1
      
  def GetDistributions(self):
      """ Get means, standard deviations, and the probability at each species amount value""" 
      dist = []
      means = {}
      sds = {}
      moments = {}
      for i in xrange(self.SSA.n_species):          
          x_i = np.array(sorted(self.SSA.distributions[i]),dtype=int)                     
          y_i = np.array([self.SSA.distributions[i][value]  for value in sorted(self.SSA.distributions[i])])/self.SSA.sim_t                     
                 
          mean = (x_i*y_i).sum()
          mean_sq = (x_i*x_i*y_i).sum()
          var = mean_sq - mean*mean
          sd = var**0.5                    
          dist.append([x_i,y_i])
          species = self.SSA.species[i]
          means[species] = mean
          sds[species] = sd
          moments[species] = {}
          moments[species]['1'] = mean
          moments[species]['2'] = mean_sq
          moments[species]['3'] = (x_i*x_i*x_i*y_i).sum()
          moments[species]['4'] = (x_i*x_i*x_i*x_i*y_i).sum()          
      return dist,means,sds,moments

  def FillDataStochsim(self):
      """ Put all simulation data in the data object data_stochsim"""
      (dist, means, sds,moments) = self.GetDistributions()  
      sim_dat = np.array(self.SSA.sim_output,'d')      
      self.data_stochsim = IntegrationStochasticDataObj()      
      self.data_stochsim.setTime(sim_dat[:,0])      
      self.data_stochsim.setDist(dist,means,sds)      
      all_species = copy.copy(self.SSA.species)      
      all_species += [species for species in self.SSA.fixed_species]         
      if self.IsTauLeaping:
          self.data_stochsim.setSpecies(sim_dat[:,1:],all_species)           # no 'firing' column  
      else:
          self.data_stochsim.setSpecies(sim_dat[:,1:-1],all_species)
      self.data_stochsim.setFiredReactions(sim_dat[:,-1][1:])
      if self.SSA.IsTrackPropensities: 
          self.data_stochsim.setPropensitiesLabels(self.SSA.rate_names)
          self.data_stochsim.setPropensities(self.SSA.propensities_output)
      self.data_stochsim.setSimulationInfo(self.SSA.timestep,self.SSA.sim_t,self.traj)
