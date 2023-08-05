#! /usr/bin/env python
import random,re
"""
Direct Method
=============
This module performs the Direct Stochastic Simulation Algorithm from Gillespie (1977) [1].

This algorithm is used to generate exact realizations of the Markov jump process. Of course, the algorithm is stochastic, so these realizations are different for each run.

Only molecule populations are specified. Positions and velocities, such as in Molecular Dynamics (MD) are ignored. This makes the algorithm much faster, because non-reactive molecular collisions can be ignored.different
Still, this exact SSA is quite slow, because it insists on simulating every individual reaction event, which takes a lot of time if the reactant population is large. Furthermore, even larger problems arise if the model contains distinct processes operating on different time scales [2].

[1] Gillespie D.T (1977), "Exact stochastic simulation of coupled chemical reactions", J.Phys. Chem. 81:2340-2361
[2] Wilkinson D.J (2009), "Stochastic Modelling for quantitative description of heterogeneous biological systems", Nat Rev Genet; 0(2):122-133 

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: July 4, 2012
"""

__doc__ = """
          Direct Method
          =============
          This program performs the direct Stochastic Simulation Algorithm from Gillespie (1977) [1].This algorithm is used to generate exact realizations of the Markov jump process. Of course, the algorithm is stochastic, so these realizations are different for each run.
          Only molecule populations are specified. Positions and velocities, such as in Molecular Dynamics (MD) are ignored. This makes the algorithm much faster, because non-reactive molecular collisions can be ignored.
          Still, this exact SSA is quite slow, because it insists on simulating every individual reaction event, which takes a lot of time if the reactant population is large. Furthermore, even larger problems arise if the model contains distinct processes operating on different time-scales [2].
          
          [1] Gillespie D.T (1977), "Exact stochastic simulation of coupled chemical reactions", J.Phys. Chem. 81:2340-2361
          [2] Wilkinson D.J (2009), "Stochastic Modelling for quantitative description of heterogeneous biological systems", Nat Rev Genet; 0(2):122-133
          """
############################# IMPORTS ####################################

import sys,copy,time,cPickle,os
from stochpy import model_dir

try: 
    import numpy as np
    np.seterr(divide = 'ignore') # catch the divide by zero error if species start at zero
except:
    print "Make sure that the NumPy module is installed"  
    print "This program does not work without NumPy"
    print "See http://numpy.scipy.org/ for more information about NumPy"
    sys.exit()

from stochpy.modules.PyscesMiniModel import PySCeS_Connector

########################### END IMPORTS ##################################
  
############################# Classes ####################################

class Species():
  def __init__(self):
    """ Object that is created to store the species amounts """
    pass
    
__species__ = Species()

class DirectMethod(PySCeS_Connector):
  """ 
  Direct Stochastic Simulation Algorithm from Gillespie (1977) [1].

  This algorithm is used to generate exact realizations of the Markov jump process. Of course, the algorithm is stochastic, so these realizations are different for each run.

  [1] Gillespie D.T (1977), "Exact stochastic simulation of coupled chemical reactions", J.Phys. Chem. 81:2340-2361

  Input:  
   - *File* filename.psc
   - *dir* /home/user/Stochpy/pscmodels/filename.psc
   - *OutputDir* /home/user/Stochpy/ 
   - *TempDir*
  """
  def __init__(self,File,dir,OutputDir,TempDir):
      self.OutputDir = OutputDir
      self.TempDir = TempDir
      self.IsExit = False
      self.Parse(File,dir)
      #if self.IsExit: 
      #   sys.exit()

  def Parse(self,File,dir):
      """
      Parses the PySCeS MDL input file, where the model is desribed
 
      Input:
       - *File* filename.psc
       - *dir*  /home/user/Stochpy/pscmodels/filename.psc
      """
      self.ModelFile = File
      self.ModelDir = dir           
      try:
          self.parse = PySCeS_Connector(self.ModelFile,self.ModelDir)	# Parse model  
          if self.parse.IsConverted:
              self.ModelFile += '.psc'
              self.ModelDir = model_dir
          self.N_matrix = copy.deepcopy(self.parse.N_matrix.transpose()) # June 5th 2012
          self.X_matrixinit = copy.deepcopy(self.parse.X_matrix.transpose()[0])
          self.n_species = len(self.X_matrixinit)
          self.propensities = copy.deepcopy(self.parse.propensities)
          self.species_stochmatrix = copy.deepcopy(self.parse.species)
          self.reagents = copy.deepcopy(self.parse.reagents)
          self.rate_names = copy.deepcopy(self.parse.reactions)          
          self.fixed_species = copy.deepcopy(self.parse.fixed_species)
          self.fixed_species_amount = copy.deepcopy(self.parse.fixed_species_amount)
          self.aDict = copy.deepcopy(self.parse.Mod.__aDict__)
          self.eDict = copy.deepcopy(self.parse.Events)
          self.species = copy.deepcopy(self.species_stochmatrix)
          self.species += [species for species in sorted(self.aDict)]
          self.species_pos = {}
          i=0
          for species in self.species:
              self.species_pos[species] = i                      # Determine once for each species
              i+=1    
          self.n_reactions = len(self.propensities)              # Number of reactions
      except:
          self.IsExit = True
          print "Error: It is impossible to parse the input file:", self.ModelFile, "from directory" , self.ModelDir    

  def Execute(self,settings):       
    """
    Generates T trajectories of the Markov jump process.

    Input:
     - *settings* (class object)   
    """
    self.IsInit = True
    self.X_matrix = copy.deepcopy(settings.X_matrix)
    self.IsTrackPropensities = copy.copy(settings.IsTrackPropensities)
    self.sim_t = copy.copy(settings.starttime)
    self.GetEventAtTime()
    self.GetEventAtAmount()    
    self.Propensities()
    if not self.sim_t:        
        self.timestep = 1       
        self.Initial_Conditions()  
    
    #####################
    if self.aDict != {} and not self.sim_t:
        self.AssignmentRules()
        i=0
        for value in self.aDict_species:
            self.sim_output[-1][self.aDict_indices[i]] = value
            i+=1    
    #####################       
    while self.sim_t < settings.endtime and self.timestep < settings.timesteps:           
            self.sim_a_0 = self.sim_a_mu.sum()
            if self.sim_a_0 <= 0:                                        # All reactants got exhausted
                 if settings.endtime < settings.timesteps:
                     last_output = self.sim_output[-1]
                     last_output[0] = settings.endtime
                     self.sim_output.append(last_output)                 
                 break
            
            self.RunTimeEvent(settings)           # Run direct SSA
            if self.event_time != None and self.sim_t > self.event_time: # Time Event
                self.DoEvent()
                self.sim_t = copy.copy(self.event_time)
                self.event_time = None
          
            if self.event_amount != None:                                # Amount Event
                if self.X_matrix[self.event_amount_index] > self.event_amount: 
                    self.DoEvent()
                    
            for i in xrange(self.n_species):                              # Add 'dt' to a species amount:                
                try:                    
                    self.distributions[i][self.sim_output[-1][i+1]] += self.sim_t - self.sim_output[-1][0]
                except KeyError: 
                    self.distributions[i][self.sim_output[-1][i+1]] = self.sim_t - self.sim_output[-1][0]                 
          
            ### Start output Generation ###
            event_output = list(self.X_matrix)            
            event_output += [amount for amount in self.fixed_species_amount]                
            if self.aDict != {}:
                self.AssignmentRules()
                event_output += [value for value in self.aDict_species]
                                 
            event_output.append(self.reaction_index+1)
            event_output.insert(0,self.sim_t)
            self.sim_output.append(event_output)
            # Update Propensities
            if self.sim_t < settings.endtime:   
                self.to_update = self.reagents[self.reaction_index]          # Determine vars to update
                self.Propensities()  
            if self.IsTrackPropensities:
                a_ravel = list(self.sim_a_mu.ravel())
                a_ravel.insert(0,self.sim_t)
                self.propensities_output.append(a_ravel)
            ###  End output Generation  ###  
                                              
                

  def Initial_Conditions(self):              
      """ This function initiates the output format with the initial concentrations """
      self.sim_output = []
      if self.IsTrackPropensities:
         self.propensities_output = []
         a_ravel = list(self.sim_a_mu.ravel())
         a_ravel.insert(0,self.sim_t)
         self.propensities_output.append(a_ravel)

      output_init = [self.sim_t]
      for init in self.X_matrix:                                         # Output at t = 0 
          if init < 0:
              print "Error: There are initial negative concentrations!"
              sys.exit()
          output_init.append(int(init))

      for amount in self.fixed_species_amount:
          output_init.append(amount)
      self.aDict_indices = []
      if self.aDict != {}:
           for species in sorted(self.aDict):
               output_init.append(self.parse.Mod.__pDict__[species]['initial'])
               self.aDict_indices.append(len(output_init)-1)
      output_init.append(np.NAN)
      self.sim_output.append(output_init)      
      self.distributions = [{} for i in xrange(self.n_species)]

  def GetEventAtTime(self):
      """ Get times where events happen"""
      self.event_time = None
      if 'reset' in sorted(self.eDict):
          if 'TIME' in self.eDict['reset']['trigger']:
              m = re.search(', *\d+\.\d*',self.eDict['reset']['trigger'])
              if not m:
                 m = re.search(', *\d+',self.eDict['reset']['trigger'])
              self.event_time = float(m.group(0)[1:])

  def GetEventAtAmount(self):
      """ Get amount where events happen"""
      self.event_amount = None
      if 'reset' in sorted(self.eDict):
          i=0
          for species in self.species_stochmatrix:              
              if re.search('\( *'+species+' *,',self.eDict['reset']['trigger']):
                  m = re.search(', *\d+\.\d*',self.eDict['reset']['trigger'])
                  if not m:
                     m = re.search(', *\d+',self.eDict['reset']['trigger'])
                  self.event_amount = float(m.group(0)[1:])
                  self.event_amount_index = i
                  break
              i+=1

  def DoEvent(self): 
      """ Do the event of the model """
      i=0
      for species in self.species_stochmatrix:
          if species in self.eDict['reset']['assignments']:
              self.X_matrix[i] = float(self.eDict['reset']['assignments'][species])                     
              if i not in self.to_update: 
                  self.to_update.append(i)      # Update species value for propensities for next reaction fire
          i+=1 

  def AssignmentRules(self):
       """ Builds the assignment rules """ 
       code_string = """"""
       if self.sim_t == 0:
           self.aDict_species_labels = []
           for species in self.species_stochmatrix:
               for aDict_species in sorted(self.aDict):
                   if species in self.aDict[aDict_species]['formula']:
                       self.aDict_species_labels.append(species)

       for i in xrange(len(self.aDict_species_labels)):
           species_value = self.X_matrix[i]            
           code_string += "%s=%s\n" % (self.species_stochmatrix[i],species_value)
       self.aDict_species = np.zeros(len(self.aDict))
       i=0
       for species in sorted(self.aDict):
           code_string += "self.aDict_species[%s]=%s\n" % (i,self.aDict[species]['formula'])
           i+=1
       self.rateFunc(code_string,self.aDict_species)

  def rateFunc(self,rate_eval_code,r_vec):
      """
      Calculate propensities from the compiled rate equations
     
      Input:
       - *rate_eval_code* compiled rate equations
       - *r_vec* output for the calculated propensities
      """
      try:
          exec(rate_eval_code)     
      except Exception,er:
          print er
          print "Error: It is impossible to determine the propensities. Check if all variable concentrations are initialized"
          sys.exit()

  def Propensities(self):
      """ Determines the propensities to fire for each reaction at the current time point. At t=0, all the rate equations are compiled. """   
      if self.IsInit:                                                       # Compile rate-eqs
          code_str = """"""          
          self.sim_a_mu = np.zeros([self.n_reactions])                      # Initialize a(mu)
          for i in xrange(self.n_reactions):
              code_str += "r_vec[%s]=%s\n" % (i,self.propensities[i])             
          self.req_eval_code = compile(code_str,"RateEqEvaluationCode","exec")         
          [setattr(__species__,self.species_stochmatrix[s],self.X_matrix[s]) for s in xrange(self.n_species)] # Set species quantities
          self.IsInit = False
      else:          
          [setattr(__species__,self.species_stochmatrix[s],self.X_matrix[s]) for s in self.to_update]
      self.rateFunc(self.req_eval_code,self.sim_a_mu)                       # Calc. Propensities 
            
      if self.sim_a_mu.min() < 0:         
          print "Error: Negative propensities are found"
      else:
          self.sim_a_mu = abs(self.sim_a_mu)                                # -0 to 0
        
  def RunTimeEvent(self,settings):
      """ Calculates a time step of the Direct Method """ 
      #np.random.seed(5)   
      if self.sim_t == 0:
          randoms = np.random.random(1000) 
          self.randoms_log = np.log(randoms)*-1
          self.randoms = np.random.random(1000)
          self.count = 0
       
      elif self.count == 1000:
          randoms = np.random.random(1000) 
          self.randoms_log = np.log(randoms)*-1
          self.randoms = np.random.random(1000)    
          self.count = 0    
  
      self.sim_r2 = self.randoms[self.count]                                # Draw random number 2 [0-1]
      self.sim_tau = self.randoms_log[self.count]/float(self.sim_a_0)       # reaction time generation         
      if (self.sim_t + self.sim_tau) < settings.endtime:
          self.sim_t += self.sim_tau                                        # Time update
          self.count +=1

          self.reaction_index = 0
          sum_of_as = self.sim_a_mu[self.reaction_index]
          criteria = self.sim_r2*self.sim_a_0
          while sum_of_as < criteria:                                       # Use r2 to determine which reaction will occur
              self.reaction_index += 1	                                    # Index
              sum_of_as += self.sim_a_mu[self.reaction_index]      

          try:
              self.X_matrix += self.N_matrix[self.reaction_index]
              self.timestep += 1
          except MemoryError,ex:
              print ex
              sys.exit()
      else: 
          self.sim_t = settings.endtime
          self.reaction_index = np.nan
