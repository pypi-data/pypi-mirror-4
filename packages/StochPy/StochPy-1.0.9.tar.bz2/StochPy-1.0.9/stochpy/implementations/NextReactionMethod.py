"""
Next Reaction Method
====================
This module performs the Next Reaction Method from Gibson and Bruck [1]. Therefore, it is also called the Gibson and Bruck algorithm.

[1] M.A. Gibson and J. "Bruck Efficient Exact Stochastic Simulation of Chemical Systems with Many Species and Many
Channels", J. Phys. Chem., 2000,104,1876-1889

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: July 4, 2012
"""

from stochpy import model_dir
import sys,copy,time,heapq,cPickle,os,re
try: 
    import numpy as np
    np.seterr(divide = 'ignore') # catch the divide by zero error if species start at zero
except:
    print "Make sure that the NumPy module is installed"  
    print "This program does not work without NumPy"
    print "See http://numpy.scipy.org/ for more information about NumPy"
    sys.exit()

from stochpy.modules.Heap import * 
from stochpy.modules.PyscesMiniModel import PySCeS_Connector
from stochpy.modules.PyscesMiniModel import IntegrationStochasticDataObj

#############################################################

class Species():
  def __init__(self):
      """ Object that is created to store the species amounts """
      pass
    
__species__ = Species()

class NextReactionMethod(PySCeS_Connector):
  """ 
  Next Reaction Method from Gibson and Bruck 2000 [1]. 

  [1] M.A. Gibson and J. "Bruck Efficient Exact Stochastic Simulation of Chemical Systems with Many Species and Many Channels", J. Phys. Chem., 2000,104,1876-1889 

  Input:  
   - *File* filename.psc
   - *dir* /home/user/Stochpy/pscmodels/filename.psc
   - *Outputdir* /home/user/Stochpy/
  """
  def __init__(self,File,dir,OutputDir,TempDir):
      self.OutputDir = OutputDir
      self.TempDir = TempDir
      self.IsExit = False
      self.Parse(File,dir)
      #if self.IsExit: sys.exit()  

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
          self.parse = PySCeS_Connector(self.ModelFile,self.ModelDir,IsNRM = True)	# Parse model      
          if self.parse.IsConverted:
              self.ModelFile += '.psc'
              self.ModelDir = model_dir
  
          self.N_matrix = copy.deepcopy(self.parse.N_matrix.transpose())   # June 5th 2012
          self.X_matrixinit = copy.deepcopy(self.parse.X_matrix.transpose()[0])	 # 22/01/11   
          self.reactants = copy.deepcopy(self.parse.reactants)
          self.species_stochmatrix = copy.deepcopy(self.parse.species)
          self.n_species = len(self.X_matrixinit)
          self.reagents = copy.deepcopy(self.parse.reagents)
          self.rate_names = copy.deepcopy(self.parse.reactions)
          self.propensities = copy.deepcopy(self.parse.propensities)
          self.fixed_species= copy.deepcopy(self.parse.fixed_species)
          self.fixed_species_amount = copy.deepcopy(self.parse.fixed_species_amount)
          self.affects = copy.deepcopy(self.parse.affects)
          self.dep_graph = copy.deepcopy(self.parse.dep_graph)          
          self.aDict = copy.deepcopy(self.parse.Mod.__aDict__)
          self.eDict = copy.deepcopy(self.parse.Events)
          self.species = copy.deepcopy(self.species_stochmatrix)
          self.species += [species for species in sorted(self.aDict)]
          self.species_pos  = {}
          i=0
          for species in self.species:
              self.species_pos[species] = i # Determine once for each species the position in the X-matrix
              i+=1
          self.sim_dump = []
          self.n_reactions = len(self.propensities) # Number of reactions
          self.sim_a_mu = np.zeros(self.n_reactions)  
      except:
          self.IsExit = True
          print "Error: It is impossible to parse the input file:", self.ModelFile, "from directory" , self.ModelDir


  def Execute(self,settings):       
    """
    Generates T trajectories of the Markov jump process.

    Input:
     - *settings* (class object)   
    """
    self.settings=settings
    self.IsInit = True
    self.X_matrix = copy.deepcopy(settings.X_matrix)
    self.IsTrackPropensities = copy.copy(settings.IsTrackPropensities)
    self.sim_t = copy.copy(settings.starttime)
    self.GetEventAtTime()
    self.GetEventAtAmount()
    self.BuildInits()
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
        if self.sim_a_0 <= 0:                               # All reactants got exhausted
             if settings.endtime < settings.timesteps:
                 last_output = self.sim_output[-1]
                 last_output[0] = settings.endtime
                 self.sim_output.append(last_output)                
             break            
                 
              
        self.RunTimeEvent(settings)                         # Run next reaction method
        if self.sim_t > self.event_time and self.event_time != None:
            self.DoEvent()                                  # Time event
            self.sim_t = copy.copy(self.event_time)
            self.event_time = None          
        if self.event_amount != None:                       # Amount Event
            if self.X_matrix[self.event_amount_index] > self.event_amount:
                self.DoEvent()
            
        for i in xrange(self.n_species):                    # Add 'dt' to a species amount:
            try:
                self.distributions[i][self.sim_output[-1][i+1]] += self.sim_t-self.sim_output[-1][0]
            except KeyError:     
                self.distributions[i][self.sim_output[-1][i+1]] = self.sim_t-self.sim_output[-1][0]                

        ### Start output Generation ###            
        event_output = list(self.X_matrix)            
        event_output += [amount for amount in self.fixed_species_amount]                
        if self.aDict != {}:
            self.AssignmentRules()
            event_output += [value for value in self.aDict_species]
        event_output.append(self.reaction_index+1)	
        event_output.insert(0,self.sim_t)
        self.sim_output.append(event_output)
        ###  End output Generation  ###
        if self.sim_t < settings.endtime and self.timestep < settings.timesteps:
            self.sim_a_mu_prev = copy.copy(self.sim_a_mu)                 
            self.to_update = self.reagents[self.reaction_index] # Determine vars to update
            self.Propensities()                                 # Update Propensities    
            t_prev = self.sim_output[self.timestep-1][0]        
            for j in self.prop_to_update:
                if self.count == 999:
                    randoms = np.random.random(1000)            # Create M random numbers
                    self.randoms_log = np.log(randoms)*-1
                    self.count = 0          
                if (self.sim_a_mu_prev[j] > 0 and self.sim_a_mu[j] >= 0):
                    if j == self.reaction_index:
                        tau_alpha = self.randoms_log[self.count]/self.sim_a_mu_prev[j]+self.sim_t
                        self.count+=1
                        self.sim_a_mu_zero[j] = {'t1':self.sim_t,'a_alpha_old':self.sim_a_mu_prev[j],'tau_alpha':tau_alpha}
                    else:           
                        tau_alpha = self.sim_taus[j]               
                        self.sim_a_mu_zero[j] = {'t1':self.sim_t,'a_alpha_old':self.sim_a_mu_prev[j],'tau_alpha':tau_alpha}
            self.UpdateHeap()
            ##show_tree(self.tree.heap)  # //comment\\   
        if self.IsTrackPropensities:
            a_ravel = list(self.sim_a_mu.ravel())
            a_ravel.insert(0,self.sim_t)
            self.propensities_output.append(a_ravel)
                  

  def Initial_Conditions(self):                
      """ This function initiates the output format with the initial concentrations  """
      self.sim_output = []    
      if self.IsTrackPropensities: 
         self.propensities_output = []
         a_ravel = list(self.sim_a_mu.ravel())
         a_ravel.insert(0,self.sim_t)
         self.propensities_output.append(a_ravel) 

      output_init = [self.sim_t]      
      for init in self.X_matrix:                              # Output at t = 0 
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
             if i not in self.to_update: self.to_update.append(i)   # update species value for propensities for next reaction fire
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
           #code_string += str(self.species_stochmatrix[i]) + '=' + str(species_value) + '\n'   
           code_string += "%s=%s\n" % (self.species_stochmatrix[i],species_value)
       self.aDict_species = np.zeros(len(self.aDict))
       i=0
       for species in sorted(self.aDict):
           code_string += "self.aDict_species[%s]=%s\n" % (i,self.aDict[species]['formula'])
           #code_string += 'self.aDict_species[' + str(i)+']=' + str(self.aDict[species]['formula']) + '\n'
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
      """
      Determines the propensities to fire for each reaction at the current time point. At t=0, all the rate equations are compiled. 
      """   
      if self.IsInit:			                     # Compile rate-eqs
        code_str = """"""
        self.sim_a_mu = np.zeros([self.n_reactions])         # Initialize a(mu)
        for i in xrange(self.n_reactions):        
            code_str += "if self.rFire[%s]: r_vec[%s]=%s\n" % (i,i,self.propensities[i])
        self.req_eval_code = compile(code_str,"RateEqEvaluationCode","exec")
        [setattr(__species__,self.species_stochmatrix[s],self.X_matrix[s]) for s in xrange(self.n_species)] # Set species quantities
        self.IsInit = False
      else:
          [setattr(__species__,self.species_stochmatrix[s],self.X_matrix[s]) for s in self.to_update]
      self.rateFunc(self.req_eval_code,self.sim_a_mu)        # Calc. Propensities 
      if self.sim_a_mu.min() < 0:
          print "Error: Negative propensities are found"
      else: self.sim_a_mu = abs(self.sim_a_mu)

  def RunTimeEvent(self,settings):
      """ Perform a direct SSA time step and pre-generate M random numbers """ 
      #np.random.seed(5) 
      if self.sim_t == 0:       
          randoms = np.random.random(self.n_reactions) # Pre-generate for each time step M random numbers
          self.randoms_log_init = np.log(randoms)*-1
          self.InitialStep()
          self.count  = 0
          randoms = np.random.random(1000)                  # Create M random numbers
          self.randoms_log = np.log(randoms)*-1
          
      self.rFire= np.zeros(self.n_reactions) 
      minimum = self.tree.heap[0]
      self.reaction_index = minimum[1]                      # Pick reaction to executeO(1)
      tau = minimum[0]                                      # Pick tau O(1)     
      if tau < settings.endtime:
          self.sim_t = tau                                      # New time  
          self.prop_to_update = self.dep_graph[self.reaction_index] # Propensities to update      
          if self.reaction_index not in self.prop_to_update:
              self.prop_to_update.append(self.reaction_index)
      
          for pos in self.prop_to_update:
              self.rFire[pos] = 1
          try:
              self.X_matrix += self.N_matrix[self.reaction_index]
              self.timestep += 1
          except MemoryError,ex:
              print ex
              sys.exit()      
      
      else: 
          self.sim_t = settings.endtime
          self.reaction_index = np.nan

  def InitialStep(self): 
      """ Monte Carlo step to determine all taus and to create a binary heap """
      self.sim_taus = self.randoms_log_init[0:self.n_reactions]/self.sim_a_mu # Calculate all initial taus
      pairs = []
      j=0
      while j<self.n_reactions:
          temp = (self.sim_taus[j],j)
          pairs.append((self.sim_taus[j],j))
          j+=1 	
      self.tree = BinaryHeap(pairs)                         # Create binary tree    
      ##show_tree(self.tree.heap)      
      
  def UpdateHeap(self):       
    """ This function calculates new tau values for reactions that are changed. After this calculations, the binary heap is updated, which is much more efficient then rebuilding the entire heap. """
    for j in self.prop_to_update:
    #for j in xrange(self.n_reactions): 
      location = self.tree.index[j]
      if j == self.reaction_index:                          # alpha = mu
          if self.count == 999:
              randoms = np.random.random(1000)              # Create M random numbers
              self.randoms_log = np.log(randoms)*-1
              self.count = 0				
          if self.sim_a_mu[j] != 0:
              tau = self.randoms_log[self.count]/self.sim_a_mu[j] + self.sim_t
              self.count +=1
          else: tau = 1000e1000
          self.sim_taus[j] = tau
          self.tree.heap[location] = (tau,j)
      else:                                                 # alpha != mu
          last_pos_a_mu = self.sim_a_mu_zero[j]['a_alpha_old']
          t1 = self.sim_a_mu_zero[j]['t1']
          if self.sim_a_mu_prev[j] != 0 and last_pos_a_mu !=0: # a_j > 0
              tau_alpha = self.sim_taus[j]
              tau = (float(self.sim_a_mu_prev[j])/self.sim_a_mu[j])*(tau_alpha-self.sim_t)+self.sim_t
          elif self.sim_a_mu_prev[j] == 0 and last_pos_a_mu == 0 and t1 == 0:   # a_j zero from start
              tau = self.randoms_log_init[j]/self.sim_a_mu[j] + self.sim_t
          else:                                             # a_j became zero after some time t1
              tau_alpha = self.sim_a_mu_zero[j]['tau_alpha']          
              tau = (float(last_pos_a_mu)/self.sim_a_mu[j])*(tau_alpha-t1)+self.sim_t
          self.sim_taus[j] = tau
          self.tree.heap[location] = (tau,j)
      self.tree.Done = 0
      while not self.tree.Done: self.tree.Update_AUX(tau,j) 

  def BuildInits(self):
      """ Build initials that are necessary to generate a trajectory """    
      self.rFire= np.ones(self.n_reactions)
      self.sim_a_mu_zero = []
      for i in xrange(self.n_reactions):
          self.sim_a_mu_zero.append({'t1':0,'a_alpha_old':0,'tau_alpha':0})    
      self.sim_taus = None	 	 			            # necessary for iteration
      self.tree = None  					            # necessary for iteration
