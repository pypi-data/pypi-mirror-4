#! /usr/bin/env python
"""
Stochastic Nucleosome Modification Simulations
==============================================

Performs nucleosome modification simulations based on stochastic simulation algorithms (SSA).

Hard coded for one trajectory

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: September 19, 2011
"""

############################## IMPORTS ###################################

import os,sys,getopt,re,copy
try: import numpy as np
except:
    print "Make sure that the NumPy module is installed"  
    print "This program does not work without NumPy"
    print "See http://numpy.scipy.org/ for more information about NumPy"
    sys.exit()

import stochpy.modules.StochSim as StochSim
import  stochpy.modules.Analysis as Analysis			# installed  

############################# END IMPORTS #################################

class NucSim():
  """
  Performs Stochastic Nucleosome Modification Simulations.  

  >>> sim = stochpy.NucSim()
  >>> sim.DoStochSim()
  >>> sim.Model(File = 'filename.psc', dir= '/.../.../filename.psc)
  >>> sim.PlotGlobalTimeSim()
  >>> sim.Timesteps(1000)
  >>> sim.Endtime(100)
  >>> sim.PlotPattern()
  >>> sim.PlotGlobalDistributions()
  >>> sim.Write2File()
  >>> sim.ShowOverview()
  >>> sim.ShowSpecies()
  """
  def __init__(self,Method = 'Direct',File = None,dir = None,Mode = 'steps',End = 1000,Trajectories=1,IsInteractive = True):
    print "Welcome to the nucleosome modification simulation module"
    if os.sys.platform != 'win32':
        output_dir = os.path.join(os.path.expanduser('~'),'Stochpy',)
        if File == dir == None:
            dir = os.path.join(os.path.expanduser('~'),'Stochpy','pscmodels')
            File = "ThreeNucleosome.psc"
    else:
        output_dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy',)
        if File == dir == None:
            dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','pscmodels')
            File = "model1.psc"

    self.output_dir = output_dir
    self.model_dir = dir
    self.ssa_mod = StochSim.SSA(Method,File,dir,Mode,End,Trajectories,IsTestsuite=False,IsInteractive=True,IsTrackPropensities=False,IsRun=False)    
    self.IsInteractive = IsInteractive
    self.Is_RunDone = False
    if self.IsInteractive:
        try: Analysis.plt.ion()                             # Set on interactive pylab environment
        except: pass                                        # Error message is already shown        

  def Method(self,method):
    """
    Input:
     - *method*: (string)

    Select one of the four methods:
     - *Direct*
     - *FirstReactionMethod*
     - *NextReactionMethod*
     - *TauLeaping*
    """   
    self.ssa_mod.Method(method)

  def Run(self):
    """ old version """
    self.DoStochSim()

  def DoStochSim(self):
    """ Perform a SSA run and merge the output to global M, U and A modification results """
    self.IsGlobal = False
    self.HasGlobalDist = False
    self.IsMerge = False
    self.HasStates = False
    self.ssa_mod.DoStochSim()
    self.data_nucsim = copy.deepcopy(self.ssa_mod.data_stochsim)
    self.GetNucleosomeOutput()
    self.plot = Analysis.DoPlotting(self.modifications,'')
    self.MergeModifications()
    self.Is_RunDone = True    

  def Timesteps(self,s):
    """
    Set the number of time steps to be generated for each trajectory

    Input:
     - *s*: Number of time steps (integer)
    """
    self.ssa_mod.Timesteps(s)

  def Endtime(self,t):
    """
    Set the end time of exact realization of the Markov jump process

    Input:
     - *t*: endtime*(float) 
    """  
    self.ssa_mod.Endtime(t)

  def Reload(self):
    """ Reload the entire model again. Usefull if the model file has changed"""
    self.ssa_mod.Reload()

  def Model(self,File,dir = None): 
    """
    Give the model, which is used to do stochastic simulations on

    Input:
     - *File* = 'filename.psc'
     - *dir*: [default = None] the directory where File lives"
    """   
    self.ssa_mod.model_file = File
    if dir != None: self.ssa_mod.model_dir = dir
    self.ssa_mod.Reload()

  def ShowSpecies(self):
    """ Print the species of the model """
    print self.ssa_mod.ShowSpecies()

  def ShowOverview(self):
    """ Print an overview of the current settings """
    self.ssa_mod.ShowOverview()

  def GetNucleosomeOutput(self):
    """ 
    Besides nucleosome results, enzyme quantities can be simulated, which are ignored in the output analysis. So, E(type)M[i] and M[i] are both from M[i], both the first one carries an enzyme. Therefore, these results are merged to obtain the output per nucleosome modification position.
    """
    self.modifications = ['M','U','A']
    line = 1
    self.data_nucsim.nucleosome_output_labels = []  

    self.HasEm = False
    self.HasEa = False
    for species in self.ssa_mod.SSA.species:      
        if re.search('^[M|U|A]+\d+$',species):              # Use REGEX to find ModificationType(integer)
            self.data_nucsim.nucleosome_output_labels.append((line,species))	
            line+=1
        else:
            line+=1       
    if re.search('Em',species):                             # Use REGEX to search for enzyme type M
        self.HasEm = True
        self.modifications.append('Em')
    if re.search('Ea',species):                             # Use REGEX to search for enzyme type A
        self.HasEa = True
        self.modifications.append('Em')

    #self.data_nucsim.nucleosome_output = []
    time = self.ssa_mod.data_stochsim.time.flatten()
    self.data_nucsim.nucleosome_output = np.zeros((len(time),len(self.data_nucsim.nucleosome_output_labels)+1))
    self.data_nucsim.EnzymeDict = {"Em": np.zeros(len(time),dtype =int), "Ea": np.zeros(len(time),dtype =int)}
    self.data_nucsim.nucleosome_output[:,0] = time
    n=1
    for nuc in self.data_nucsim.nucleosome_output_labels:   # M[i], A[i], or U[i]
      index_no_enz = self.ssa_mod.data_stochsim.species_labels.index(nuc[-1])         
      temp = copy.deepcopy(self.ssa_mod.data_stochsim.species[:,index_no_enz])
      if self.HasEm:                                         # EmM[i],EmA[i], or EmU[i]
          index_enz = self.ssa_mod.data_stochsim.species_labels.index('Em'+nuc[-1])
          b = copy.deepcopy(self.ssa_mod.data_stochsim.species[:,index_enz])
          self.data_nucsim.EnzymeDict["Em"] += b
          temp += b         
      if self.HasEa:                                         # EaM[i],EaA[i], or EaU[i]
          index_enz  = self.ssa_mod.data_stochsim.species_labels.index('Ea'+nuc[-1])
          c = copy.deepcopy(self.ssa_mod.data_stochsim.species[:,index_enz])
          self.data_nucsim.EnzymeDict["Em"] += c
          temp += c       
      self.data_nucsim.nucleosome_output[:,n] = temp
      n+=1

  def MergeModifications(self):      
    """
    There are multiple modifications possible for each nucleosome, which gives a enormous number of "species". Examples are [A1],[M1], and [U1], while this describes only nucleosome 1.
    Further, it is interesting to see the modifcation effects for the whole model in stead of for single nucleosomes. Therefore, this function 'merges' the modifications of each nucleosome to the total number of certain modifications at each time point. 
    For instance, imagine a 60 Nucleosome model with 3 possibile modifications (M, U, and A), which contains 180 different 'species'. This model is then reduced to the three modification levels (M, U and A) at each timepoint.

    Hardcoded for three possible modifications: M, U, and A (/28/07/10/)
    """ 
    M_cols = []
    U_cols = []
    A_cols = []  
    col = 1  
    for label in self.ssa_mod.data_stochsim.species_labels:
      if 'M' in label:                                      # M modification column
          M_cols.append(col)
      elif 'U' in label:                                    # U modification column
          U_cols.append(col)	
      elif 'A' in label:                                    # A modification column
          A_cols.append(col)
      col+=1    

    #print M_cols,U_cols,A_cols
    merged_output_labels = ["M","U","A"]                    # Possible Nucleosome  modifications
    if self.HasEm: merged_output_labels.append("Em")
    if self.HasEa: merged_output_labels.append("Ea")
    
    merged_output = np.zeros((len(self.ssa_mod.data_stochsim.species),len(merged_output_labels)+1))

    temp = []
    n=0                      
    for output in self.ssa_mod.data_stochsim.getSpecies():  # Start to Merge the output
        t = output[0]      
        M = 0
        U = 0
        A = 0
        for m in M_cols: 
            M+=output[m]
        for u in U_cols:
            U+=output[u]
        for a in A_cols:
            A+=output[a]    
        temp = [t,M,U,A]
        if self.HasEm: temp.append(self.data_nucsim.EnzymeDict["Em"][n])
        if self.HasEa: temp.append(self.data_nucsim.EnzymeDict["Ea"][n])
        #print sum([M,U,A])                                 # Check: sum has to be identical to the number of nucleosomes
      
        m=0
        for value in temp:
            merged_output[n,m]=value
            m+=1        
        n+=1

    self.data_nucsim.species = merged_output[:,1:]
    self.data_nucsim.species_labels = merged_output_labels
    self.IsMerge = True

  def GetStateTimes(self):
    """
    Each nucleosome in this model can have 3 different modifications (M,U, or A). This function determines for each nucleosome in the model the distribution of times that it stays in a particular modification.
    """ 
    if not self.Is_RunDone: self.Run()
    self.data_nucsim.state_times = {}  
    time = self.data_nucsim.time.flatten()                  # Time points at which reactions occur

    N = len(self.data_nucsim.nucleosome_output_labels)      # Number of nucl.* 3 (M1,U1,A1, ...)
    i=0	
    while i<N:
      CopyNumbers = self.data_nucsim.nucleosome_output[:,i+1] # M1,U1,A1,M2,U2,...
      n=1
      t1 = None
      t2 = None
      temp = []
      if CopyNumbers[0]: t1=0                               # Certain modification is present at t=0
      while n<len(CopyNumbers):                             # Number of timesteps (n)
        if CopyNumbers[n] and not CopyNumbers[n-1]:         # Certain modification not present at t-1, but it is at t
            t1 = time[n]          
        elif CopyNumbers[n-1] and not CopyNumbers[n]:       # Certain modification is present at t-1, but not at t
            t2 = time[n]          
            try:
                state_time = t2-t1
                temp.append(state_time)				
            except: pass                                    # [0,0,0......,1] 09/09/2010
        n+=1  
      self.data_nucsim.state_times[self.data_nucsim.nucleosome_output_labels[i][1]] = temp
      i+=1
    self.HasStates = True

  def PrintStateTimes(self):
    """ Print the mean and std of the state times for each nucleosome modification. """
    if not self.Is_RunDone: self.Run()
    print "Name\t","Normalized Mean\t","Mean\t","Standard Deviation"
    if not self.HasStates: self.GetStateTimes()
    N = len(self.data_nucsim.state_times)/3.0               # Number of nucleosomes   
    nuc_vector = []
    i=1
    while i<=N:
        nuc_vector.append('M'+str(i))
        nuc_vector.append('U'+str(i))
        nuc_vector.append('A'+str(i))
        i+=1

    for species in nuc_vector:    
        mean = np.mean(self.data_nucsim.state_times[species])
        if species[0] == 'M': mean_norm = mean/0.90	        # Normalisation
        elif species[0] =='U': mean_norm = mean/0.45        # Normalisation
        elif species[0] =='A': mean_norm = mean/0.90        # Normalisation
        sd = np.std(self.data_nucsim.state_times[species])
        print species,"\t",mean_norm,"\t",mean,"\t",sd

  def PlotStateTimes(self,who):      
    """
    Plot the state times for a given nucleosome modification. 

    Input:
     - *who*: a certain modification (M5 or A2 for instance)*
    """
    if not self.Is_RunDone: self.Run()
    if not self.HasStates: self.GetStateTimes()
    try:      
        Analysis.plt.figure()
        Analysis.plt.hist(self.data_nucsim.state_times[who])
        Analysis.plt.xlabel("Time" )
        Analysis.plt.ylabel("Frequency")
        Analysis.plt.title("State time distribution of "+who)
        self.plot.plotnum+=1
    except: print "No state times plot is created, because",who,"is not the uploaded model"
  
  def PrintGlobalTimeSim(self):
    """ Print the time simulation of the merged output """
    if not self.Is_RunDone: self.Run()
    if not self.IsMerge: self.MergeModifications()

    for timepoint in self.data_nucsim.getSpecies():
      for value in timepoint:
          print value,"\t",    
      print ''

  def PlotGlobalTimeSim(self,species=None,linestyle = 'dotted',marker = '',colors = None,title = 'StochPy Time Simulation Plot'): 
    """
    Plot the time simulation of the merged output

    Default: PlotGlobalTimeSim() plots time simulation for each species

    Input:
     - *species*: [default = None] as a list ['S1','S2']
     - *linestyle*: [default = 'dotted'] dotted, dashed, and solid
    """
    if species == None: species = self.modifications 
    if type(species) == str: species = [species]
 
    IsPlot = True
    for s in species:
        if s not in self.modifications:
            print "Error: species",s,"is not in the model"
            IsPlot = False

    if not self.Is_RunDone: self.Run()
    if not self.IsMerge: self.MergeModifications()    
    if IsPlot: self.plot.TimeSimulation(self.data_nucsim.getSpecies(),species,1,linestyle,marker,colors,title)

  def GetGapMeasure(self):
    """
    Calculates a 'gap' measure, which is the abs. difference between the number of M and A modifications averaged over a long simulation time.
    (from  Dodd et al. 2007,'Theoritical Analysis of Epigenetic Cell Memory by Nucleosome Modification', Cell 129,813-822).
    """
    if not self.Is_RunDone: self.Run()
    M_index = self.data_nucsim.species_labels.index('M')  # All the matrix entrees that contain M modifications
    A_index = self.data_nucsim.species_labels.index('A')  # All the matrix entrees that contain A modifications
    gap_scores = []
    for line in self.data_nucsim.species:
        M = line[M_index]                                 # M modification pattern
        A = line[A_index]                                 # A modification pattern
        if M == 0 and A == 0:
            score = 0
        else:
            score = abs(M-A)/float(M+A)                   # Abs. difference	
        gap_scores.append(score)  
    self.gapmeasure = np.mean(gap_scores)                 # Average over all abs. differences
    print "Gap Measure\t",self.gapmeasure

  def GetGlobalModification(self):
    """
    Determine for each modification (M, U or A) the modification frequency at each position.
    So, it gives for example that position i is over time almost always in a M-modified state.
    """
    if not self.Is_RunDone: self.Run()       

    N = len(self.data_nucsim.nucleosome_output_labels)/3  # Number of nucleosomes    
    self.data_nucsim.pattern = {"M":[],"U":[],"A":[]}     # Init. modification means per nucl. pos.
    self.data_nucsim.enzyme_pattern = {"Em":np.zeros(N),"Ea":np.zeros(N)}			# March 19 2011
    self.data_nucsim.positions = range(1,N+1)             # Modification positions (1-N)
    for i in self.data_nucsim.positions:
      for name in self.modifications[0:3]:         
        value = self.ssa_mod.data_stochsim.means[name+str(i)] # Extract mean modification value per nucl. pos
        if self.HasEm:					
            value += self.ssa_mod.data_stochsim.means['Em'+name+str(i)]       
            self.data_nucsim.enzyme_pattern["Em"][i-1] += self.ssa_mod.data_stochsim.means['Em'+name+str(i)]  		# March 19 2011
        if self.HasEa:
            value += self.ssa_mod.data_stochsim.means['Ea'+name+str(i)]    
            self.data_nucsim.enzyme_pattern["Ea"][i-1] += self.ssa_mod.data_stochsim.means['Ea'+name+str(i)] 		# March 19 2011
        self.data_nucsim.pattern[name].append(value)
    self.IsGlobal = True

  def PrintPattern(self):
    """ Print the average nucleosome modification for each nucleosome pos."""
    if not self.Is_RunDone: self.Run()
    if not self.IsGlobal: self.GetGlobalModification()
    print "Global pattern\n"
    print "\t",
    for modification in self.modifications:
        print modification,"\t",
    print
    for pos in self.data_nucsim.positions:
      print pos,"\t",
      for modification in self.modifications:
          if modification == "M" or modification == "U" or modification == "A":
              print self.data_nucsim.pattern[modification][pos-1],"\t",
      if self.HasEm: print self.data_nucsim.enzyme_pattern["Em"][pos-1],			# March 19 2011
      if self.HasEm: print self.data_nucsim.enzyme_pattern["Ea"][pos-1],			# March 19 2011      
      print

  def PlotPattern(self,species = None,linestyle = 'dotted',title = 'StochPy Pattern Plot'):    
    """
    Plot the average nucleosome modification for each nucleosome position
    Default: PlotPattern() plots the pattern (position specific distribution) for each species

    Input:
     - *species*: [default = None] as a list ['S1','S2']
     - *linestyle*: [default = 'dotted'] dotted, dashed, and solid
     - *title*: [default = 'StochPy Pattern Plot']
    """
    if species == None: species = copy.copy(self.modifications)
    if type(species) == str: species = [species]

    IsPlot = True
    for s in species:     
        if s not in self.modifications:
            print "Error: species",s,"is not in the model"
            IsPlot = False
 
    if IsPlot:     
      try:
        if not self.Is_RunDone:
            self.Run()
        if not self.IsGlobal:
            self.GetGlobalModification()
        Analysis.plt.figure()  
        for modification in species:
            if modification == "M" or modification == "U" or modification == "A":
                Analysis.plt.step(np.array(self.data_nucsim.positions)+0.5,self.data_nucsim.pattern[modification],ls=linestyle)  # Create the plot  for each modification        
        if self.HasEm:
            Analysis.plt.step(np.array(self.data_nucsim.positions)+0.5,self.data_nucsim.enzyme_pattern["Em"],ls=linestyle)	# March 19 2011
        if self.HasEa:
            Analysis.plt.step(np.array(self.data_nucsim.positions)+0.5,self.data_nucsim.enzyme_pattern["Ea"],ls=linestyle)	# March 19 2011

        Analysis.plt.legend(species)
        Analysis.plt.title(title)
        Analysis.plt.xlabel('Nucleosome Position')
        Analysis.plt.ylabel('Frequency')   
        self.plot.plotnum+=1
      except: print "Error: MatPlotLib is not available. Use PrintPattern()"
 
  def GetGlobalDistributions(self):
    """ Determine the distribution patterns of all modification types """    
    if not self.Is_RunDone: self.Run()    
    self.HasGlobalDist = True
 
  def PlotGlobalDistributions(self,species=None,linestyle='dotted',marker = '',colors = None,title = "StochPy Distribution Plot"):   
    """
    Plot the distributions patterns of all modification types
    Default: PlotGlobalDistributions() plots distribution for each species

    Input:
     - *species*: [default = None] as a list ['S1','S2']
     - *linestyle*: [default = 'dotted'] dotted, dashed, and solid
     - *title*: [default = StochPy Distribution Plot]
    """
    if species == None: species = self.modifications
    if type(species) == str:  species = [species]
    IsPlot = True
    for s in species:
        if s not in self.modifications:
            print "Error: species",s,"is not in the model"
            IsPlot = False
  
    if IsPlot:
      if not self.Is_RunDone:
           self.Run()
      if not self.IsGlobal:
          self.GetGlobalModification()
      if not self.HasGlobalDist:
          self.GetGlobalDistributions()
      self.plot.Distributions(self.data_nucsim.distributions,species,1,linestyle,marker,colors,title)    

  def PrintGlobalDistributions(self):
    """ Print the distributions patterns of all modification types """
    if not self.Is_RunDone:
        self.Run()
    if not self.IsGlobal:
        self.GetGlobalModification()
    if not self.HasGlobalDist:
        self.GetGlobalDistributions()
    i=0
    for line in self.data_nucsim.distributions:
        #print self.modifications[i]
        i+=1
        for Type in line:
            for value in Type:
                print value,"\t",
            print

  def Write2File(self,what = 'TimeSim', to=None ):
    """
    Write output to a file

    Input:
     - *what*: [default = TimeSim] TimeSim, GlobalDistributions, Pattern
     - *to*: Directory/outputname (optional)

    Default of the first argument is: TimeSim
    """
    if to == None:
        to  =  self.output_dir+'/'+ self.ssa_mod.model_file +'_' + what

    if what == 'TimeSim':    
      if not self.Is_RunDone: self.Run()
      if not self.IsMerge: self.MergeModifications()

      Dir = to+'.txt'				# Dir/Filename
      f = open(Dir,'w')
      for timepoint in self.data_nucsim.getSpecies():
          line = ''
          for value in timepoint:
              line += str(value)
              line += '\t'
          line += '\n'
          f.write(line)        
      f.close()
      print "TimeSim output is succesfully saved at:\t",Dir

    elif what == 'GlobalDistributions':
      if not self.Is_RunDone: self.Run()
      if not self.IsGlobal: self.GetGlobalModification()
      if not self.HasGlobalDist: self.GetGlobalDistributions()
      Dir = to+'.txt'				# Dir/Filename
      f = open(Dir,'w')
      i=0
      for line in self.data_nucsim.distributions:
          f.write(self.modifications[i]+"\n")
          i+=1
          for Type in line:
              for value in Type:
                  f.write(str(value)+"\t")
              f.write("\n")
      print "GlobalDistributions output is succesfully saved at:\t",Dir

    elif what == 'Pattern':
      if not self.Is_RunDone: self.Run()
      if not self.IsGlobal: self.GetGlobalModification()
      Dir = to+'.txt'				# Dir/Filename
      f = open(Dir,'w')

      f.write("Global pattern\n")
      f.write("\t")
      for name in self.modifications:
          f.write(name+"\t")
      f.write("\n")
      for pos in self.data_nucsim.positions:
          f.write(str(pos)+"\t")
          for name in self.modifications:
              f.write(str(self.data_nucsim.pattern[name][pos-1])+"\t")
          f.write("\n")
      print "Pattern output is succesfully saved at:\t",Dir

    else:
        print "Error: The only valid options are: TimeSim, GlobalDistributions and Pattern"
