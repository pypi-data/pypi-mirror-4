 #! /usr/bin/env python
"""
N-nucleosome model builder
==========================

Used as input for Stochastic Simulation Algorithms. 

This model builder has several features:
- neighbour dependent reactions
- neighbour independent reactions
- initial modifications are randomly determined
- enzyme-landing-locations (23/08/10)

Output is automatically stored in a modelfile at /home/usr/Stochpy/pscmodels/

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: September 15, 2011
"""
import sys,random,copy,os

try:
    sys.path.append(os.getcwd()+'/modules/')
    from dnorm import *
except: from stochpy.modules.dnorm import *	# installed

class NucModel():  
  """
  Builds reactions for a N-nucleosome model, which can be used as input for SSAs. 
  
  Input: 
   - *N* number of nucleosomes (integer)
   - *ModelType* (1-8 or else)
   - *OnRate* (float)     U[i]  --> EU[i] 
   - *OffRate* (float)    EM[i] --> M[i] 
   - *DiffRate* (float)   EM[i] --> EM[i+-1]
   - *EnzymeRate* (float) EU[i] --> EM[i]
   - *Recruit* (float)    M[i]  --> EM[i]    
   - *LandingZones* dictionairy, where the keys are the enzyme types and the values the positions
   - *Booleans:* IsRecruit,IsNeighbours,IsLongRange, Threshold,IsDecay
  Each input argument has a default value and  it is possible to change them in a interactive manner.

  Usage (high-level functions):
  >>> help(model)
  >>> model.Build()
  The generated model is stored at /home/user/Stochpy/pscmodels/model1.psc
  >>> model.ChangeN(15)
  The number of nucleosomes is:		15
  >>> model.Recruitment()
  Info: Recruitment is activated
  >>> model.Neighbours()  
  >>> model.LongRangeInteractions()  
  >>> model.ChangeThreshold(5)
  >>> model.Decay()
  """
  def __init__(self,N=20,ModelType=1,OnRate=1.0,OffRate=0.10,DiffRate=0.6,EnzymeRate=5.0,Recruit=0.1,LandingZones={'M':[10]},IsRecruit=False, IsNeighbours=False,IsLongRange=False,Threshold=7,NeighbourRate=2.0,EnzNeighRate=10.0,IsDecay=False):    
    self.N = N                              # Number of nucleosome in the N-nucleosome model  
    self.Model = ModelType                  # Model to build
    self.IsRecruit = IsRecruit              # 1-3-5-7
    self.IsNeighbours = IsNeighbours        # 3-5-7
    self.IsLongRange = IsLongRange          # 5-6-7-8
    self.Threshold = Threshold			
    self.IsDecay = IsDecay                  # 7-8
    ###   Diffusion rates   ###
    self.OnRate = OnRate
    self.OffRate = OffRate
    self.DiffRate = DiffRate
    self.EnzymeRate	= EnzymeRate
    self.EnzNeighRate = EnzNeighRate
    self.Recruit = Recruit
    self.NeighbourRate = NeighbourRate
    ### End Diffusion rates ###
    self.BuildLandingZones(LandingZones)    
    self.species = ['M','U','A']            # Modification types   
    self.conversions = {'M':{'M':'M','U':'M','A':'U'},'U':{'M':'M','U':'U','A':'A'},'A':{'M':'U','U':'A','A':'A'}}

  def Build(self):
    """ Build one of the pre-defined models or a user-defined one """    
    try:    
      if not self.Model%2:
          self.IsRecruit = True             # 2-4-6-8
      else:
          self.IsRecruit = False
      if self.Model > 2:
          self.IsNeighbours = True          # 3-4-5-6-7-8
      else:
          self.IsNeighbours = False         # 1-2  
      if self.Model > 4:                    # 5-6-7-8
          self.IsLongRange = True        
      else:
          self.IsLongRange = False          # 1-2-3-4    
      if self.Model > 6:                    # 7-8
          self.IsDecay = True
      else:                                 # 1-2-3-4-5-6
          self.IsDecay = False    
    except: print "Info: Your model is not one of the pre-defined models."

    self.IsEnzymes = False
    self.IsEA = False
    self.IsEM = False
    for zone in self.landing_zones.keys():
      if zone == "A":
        self.IsEA = True                    # Ea is present
        self.IsEnzymes = True
      if zone == "M":
        self.IsEM = True                    # Em is present
        self.IsEnzymes = True    

    self.num = 0                            # Reaction number
    if os.sys.platform != 'win32':
        if not os.path.exists(os.path.join(os.path.expanduser('~'),'Stochpy')):    
            os.makedirs(os.path.join(os.path.expanduser('~'),'Stochpy'))    
            os.makedirs(os.path.join(os.path.expanduser('~'),'Stochpy','pscmodels'))  
        dir = os.path.join(os.path.expanduser('~'),'Stochpy','pscmodels')
    else:
        if not os.path.exists(os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy')):
            os.makedirs(os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy'))
            os.makedirs(os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','pscmodels'))      
        dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','pscmodels')
    if self.Model != 'own': self.filename =  dir +'/model'+str(self.Model)+'.psc'    
    else: self.filename = dir +'/model.psc'

    self.EntireModel()                      # N-nucleosome model

  def Initials(self):  
    """ Builds the initial concentrations of the nucleosome modifications. Each nucleosome starts with a certain modification (M, U or A), which is determined randomly. """
    file = open(self.filename,'a')
    file.write('\n# InitVar\n')
    numb = len(self.landing_zones)          # Number of different enzymes    
    if numb == 0:
        pos = [[1,0,0],[0,1,0],[0,0,1]]     # Possibilities (random)    
    elif numb == 1:
        pos = [[1,0,0,0,0,0],[0,1,0,0,0,0],[0,0,1,0,0,0],[0,0,0,1,0,0],[0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]]
    elif numb ==2 :
        pos = [[1,0,0,0,0,0,0,0,0],[0,1,0,0,0,0,0,0,0],[0,0,1,0,0,0,0,0,0],[0,0,0,1,0,0,0,0,0],[0,0,0,1,0,0,0,0,0],[0,0,0,0,1,0,0,0,0],[0,0,0,0,0,1,0,0,0],[0,0,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,0,1]]
    n=1
    while n<=self.N:
      values = random.choice(pos)           # Choice random pos      
      i=0
      for modification in self.species:
        file.write(modification+str(n)+'='+str(values[i])+'\n') 
        i+=1
        for enzyme_type in self.landing_zones:	# Enzyme position concentration = 0
            file.write('E'+enzyme_type.lower()+str(modification)+str(n)+'='+str(values[i])+'\n')          
            i+=1
      n+=1	
    file.close()

  def Kvalues(self):
    """ Builds to velocity-constants """
    self.K = [('knoise',1.0)]
    if self.IsNeighbours:
        self.K.append(('kneighbour',self.NeighbourRate))
    if self.IsEnzymes:      
        self.K.append(('kenz',self.EnzymeRate))
        self.K.append(('kon',self.OnRate))
        self.K.append(('koff',self.OffRate))
        self.K.append(('kdif',self.DiffRate))  
        if self.IsNeighbours:
            self.K.append(('kenz_neigh',self.EnzNeighRate))
    if self.IsRecruit:
        self.K.append(('krec',self.Recruit))    
     
  def WriteParms(self):
    """ Write the parameters that are used in the model to a file """     
    file = open(self.filename,'a')
    file.write('\n# InitPar\n')
    for name in self.K:      
        file.write(name[0]+" = "+str(name[-1])+'\n')
    file.close()

  def WriteLastReaction(self):
    """ Print the last created reaction """
    file = open(self.filename,'a')
    file.write(self.reaction_num+'\n'+self.reaction+'\n'+self.rate+'\n')
    file.close()

  def EnzPrevious(self,mod,i,x,n=1):
    """
    Builds in a multi-nucleosome model the interactions between nucleosome[i] and nucleosome[i-x], where enzymes are explicitly simulated.
    Ofcourse, Nucl[-1] does not exist, so it does not create interactions with non-existing nucleosomes
    .    
    Input:
     - *mod* modification type (string)
     - *i* Nucleosome number (integer)
     - *x* Nucleosome Neighbour number (integer)
     - *n* [default = 1] Decay value (float)
    """
    enz = 'E'+mod.lower()
    options = [('',enz),(enz,enz),(enz,'')] 

    if self.species_1 == 'U': k = 'kenz_neigh'
    else: k = 'kneighbour'
  
    if (i-x) > 0:                           # E(m)U[i] + M[i-x] --> E(m)M[i] + M[i-x]
        for option in options:
            self.num +=1
            self.reaction_num = 'R'+ str(self.num)+':'
            self.reaction = '    '+option[0]+self.species_1+str(i)+' + '+option[1]+mod+str(i-x)+' > '+option[0]+self.conversions[self.species_1][mod]+str(i)+ ' + '+option[1]+mod+str(i-x)
            if n!= 1:
                self.rate = '    '+str(n)+'*'+k+'*'+option[0]+self.species_1+str(i)+'*'+option[1]+mod+str(i-x)
            else:
                self.rate = '    '+k+'*'+option[0]+self.species_1+str(i)+'*'+option[1]+mod+str(i-x)
            self.WriteLastReaction()

  def EnzNext(self,mod,i,x,n=1):  
    """
    Builds in a multi-nucleosome model the interactions between nucleosome[i] and nucleosome[i+x], where enzymes are explicitly simulated.
    Ofcourse, Nucl[ N+5] does not exist, so it does not create interactions with non-existing nucleosomes.
    
    Input:
     - *mod* modification type (string)
     - *i* Nucleosome number (integer)
     - *x* Nucleosome Neighbour number (integer)
     - *n* [default=1] Decay value (float)
    """    
    enz = 'E'+mod.lower()    
    options = [('',enz),(enz,enz),(enz,'')] 

    if self.species_1 == 'U': k = 'kenz_neigh'
    else: k = 'kneighbour'

    if (i+x) <= self.N:
        for option in options:
            self.num +=1
            self.reaction_num = 'R'+ str(self.num)+':'
            self.reaction = '    '+option[0]+self.species_1+str(i)+' + '+option[1]+mod+str(i+x)+' > '+option[0]+self.conversions[self.species_1][mod]+str(i)+' + '+option[1]+mod+str(i+x)
            if n!= 1:
                self.rate = '    '+str(n)+'*' + k+'*'+option[0]+self.species_1+str(i)+'*'+option[1]+mod+str(i+x)
            else:
                self.rate = '    '+k+'*'+option[0]+self.species_1+str(i)+'*'+option[1]+mod+str(i+x)
            self.WriteLastReaction()

  def Next(self,Type,i,x,n=1):
    """
    Builds in a multi-nucleosome model the interactions between nucleosome[i] and nucleosome[i-x]
    Ofcourse, Nucl[-1] does not exist, so it does not create interactions with non-existing nucleosomes      
    
    Input:
     - *Type* modification enzyme (string)
     - *i* Nucleosome number (integer)
     - *x* Nucleosome Neighbour number (integer)
     - *n* [default = 1] Decay value (float)
    """
    if self.IsEnzymes:                  # Explicit simulation of enzymes
        enz = 'E'+Type.lower()
        if Type == 'M': mod = 'A'
        if Type == 'A': mod = 'M'
        options = [('',''),(enz,''),('',enz)]
        #options = [('',''),('',enz)]
    else:                               # No explicit simulation of enzymes
        options = [('','')]
        mod = Type         

    if (i+x) <= self.N:
        for option in options:
            self.num +=1
            self.reaction_num = 'R'+ str(self.num)+':'
            self.reaction = '    '+option[0]+self.species_1+str(i)+' + '+option[1]+mod+str(i+x)+' > '+option[0]+self.conversions[self.species_1][mod]+str(i)+ ' + '+option[1]+mod+str(i+x)
            if n!= 1: self.rate = '    '+str(n)+'*kneighbour*'+option[0]+self.species_1+str(i)+'*'+option[1]+mod+str(i+x)
            else: self.rate = '    kneighbour*'+option[0]+self.species_1+str(i)+'*'+option[1]+mod+str(i+x)
            self.WriteLastReaction()
    
  def Previous(self,Type,i,x,n=1):
    """
    Builds in a multi-nucleosome model the interactions between nucleosome[i] and nucleosome[i-x].
    Ofcourse, Nucl[-1] does not exist, so it does not create interactions with non-existing nucleosomes.
    
    Input:
     - *Type* modification enzyme (string)
     - *i* Nucleosome number (integer)
     - *x* Nucleosome Neighbour number (integer)
     - *n* [default = 1] Decay value (float)
    """    
    if self.IsEnzymes:                  # Explicit simulation of enzymes
        enz = 'E'+Type.lower()
        if Type == 'M':  mod = 'A'
        if Type == 'A':  mod = 'M'
        options = [('',''),(enz,''),('',enz)]
        #options = [('',''),('',enz)]
    else:                               # No explicit simulation of enzymes
        options = [('','')]
        mod = Type
    
    if (i-x) > 0:
        for option in options:
            self.num +=1
            self.reaction_num = 'R'+ str(self.num)+':'
            self.reaction = '    '+option[0]+self.species_1+str(i)+' + '+option[1]+mod+str(i-x)+' > '+option[0]+self.conversions[self.species_1][mod]+str(i)+ ' + '+option[1]+mod+str(i-x)
            if n!= 1: self.rate = '    '+str(n)+'*kneighbour*'+option[0]+self.species_1+str(i)+'*'+option[1]+mod+str(i-x)
            else: self.rate = '    kneighbour*'+option[0]+self.species_1+str(i)+'*'+option[1]+mod+str(i-x)
            self.WriteLastReaction()

  def Noisy1(self,i): 
    """
    Builds the noisy conversions from M --> U and from A --> U for each nucleosome in the model.
    
    Input:    
     - *i* Nucleosome number (integer)
    """
    self.num+=1
    self.reaction_num = 'R'+ str(self.num)+':'    
    self.reaction = '    '+self.species_1+str(i)+' > '+'U'+str(i)
    self.rate = '    knoise*'+self.species_1+str(i)
    self.WriteLastReaction()

    for Type in self.landing_zones:			  # If enzyme type M and/or A is explicitly simulated
        type_ = Type.lower()      
        self.num+=1
        ##if self.species_1 != Type:
        self.reaction_num = 'R'+ str(self.num)+':'    
        self.reaction = '    E'+type_+self.species_1+str(i)+' > '+'E'+type_+'U'+str(i)
        self.rate = '    knoise*E'+type_+self.species_1+str(i)
        self.WriteLastReaction()    
  
  def Noisy2(self,i): 
    """
    Builds the noisy conversions from U--> A and U--> M for each nucleosome in the model. Notice that these conversions are only made if there is no explicit simulation of the enzymes.
    
    Input:    
     - *i* Nucleosome number (int)
    """ 
    if not self.IsEM:
        self.num+=1
        self.reaction_num = 'R'+ str(self.num)+':'
        self.reaction = '    '+'U'+str(i)+' > M'+str(i)
        self.rate = '    knoise*U'+str(i)                   
        self.WriteLastReaction()
    if not self.IsEA:
        self.num+=1
        self.reaction_num = 'R'+ str(self.num)+':'
        self.reaction = '    U'+str(i)+' > A'+str(i)     
        self.rate = '    knoise*U'+str(i) 
        self.WriteLastReaction()
 
  def Enzyme(self,mod,i):
    """ 
    Build the reactions that are katalyzed by enzymes that are attached to the DNA chain: E(type)U[i] -->  E(type)M[i] etc
    
    Input:
     - *mod* modification enzyme (string)
     - *i* Nucleosome number (integer)
    """
    Type = mod.lower()
    enz = 'E'+Type
    self.num+=1
    self.reaction_num = 'R'+ str(self.num)+':'
    self.reaction = '    '+enz+'U'+str(i)+ ' > '+enz+mod+str(i)
    self.rate = '    kenz*'+enz+'U'+str(i)  
    self.WriteLastReaction()    

  def EnzymeLanding(self,i,Type,mod):
    """
    Enzyme landing  0 --> E[i]
    
    Input:
     - *i* Nucleosome number (integer)
     - *Type* enzyme type
     - *mod* modification (string)
    """        
    Type = Type.lower()
    enz = 'E'+Type
    self.num+=1
    self.reaction_num = 'R'+ str(self.num)+':'
    self.reaction = '    '+str(mod)+str(i)+' > '+enz+str(mod)+str(i)
    self.rate = '    kon*'+str(mod)+str(i)
    self.WriteLastReaction()

  def EnzymeDropping(self,mod,Type,i):
    """
    Build the dropping of enzymes from nucleosomes: E(type)M[i] --> M[i]
     - *mod* modification (string)
     - *Type* enzyme type
     - *i* Nucleosome number (integer)
    """    
    Type = Type.lower()
    enz = 'E'+Type
    self.num+=1
    self.reaction_num = 'R'+ str(self.num)+':'
    self.reaction = '    '+enz+str(mod)+str(i)+' > '+str(mod)+str(i)
    self.rate = '    koff*'+enz+str(mod)+str(i)
    self.WriteLastReaction()       

  def EnzymeMovement(self,Type):  
    """
    Build the diffusion of enzymes along the DNA-chain: E(type)[i] --> E(type)[i+1], E(type)[i] --> E(type)[i-1] 
    This is done for each modification type, so: E(type)M[i] --> E(type)M[i+1] or to E
(type)[A+1] etc.

    Input:
     - *Type* enzyme type
    """
    Type = Type.lower()
    enz_M = 'E'+Type+'M'		
    enz_U = 'E'+Type+'U'
    enz_A = 'E'+Type+'A'     

    options = [(enz_M,enz_M,'M','M'),(enz_M,enz_U,'U','M'),(enz_M,enz_A,'A','M'),(enz_U,enz_M,'M','U'),(enz_U,enz_U,'U','U'),(enz_U,enz_A,'A','U'),(enz_A,enz_M,'M','A'),(enz_A,enz_U,'U','A'),(enz_A,enz_A,'A','A')]
    i=1 
    while i<self.N:   					# E(type)[i] --> E(type)[i+1]
      for option in options:
        self.num+=1
        self.reaction_num = 'R'+ str(self.num)+':'
        self.reaction = '    '+option[0]+str(i)+' + ' +option[2]+str(i+1)+' > '+ option[3]+str(i)+' + ' +option[1]+str(i+1)  
        self.rate = '    kdif*'+ option[0]+str(i)+'*' + option[2]+str(i+1)
        self.WriteLastReaction()
      i+=1
    i=2
    while i<=self.N:    				# E(type)[i] --> E(type)[i-1]
      for option in options:
        self.num+=1
        self.reaction_num = 'R'+ str(self.num)+':'
        self.reaction = '    '+option[0]+str(i)+' + ' +option[2]+str(i-1)+' > ' +option[3]+str(i)+' + ' +option[1]+str(i-1)
        self.rate = '    kdif*'+option[0]+str(i)+'*' + option[2]+str(i-1)
        self.WriteLastReaction()
      i+=1    

  def RecruitEnzymes(self,mod,i):
    """
    Build reactions, which can recruit enzymes if a nucleosome carries a certain modification.
    M[i] --> EmM[i], if the model simulates M enzymes explicitly
    A[i] --> EaA[i], if the model simulates A enzymes explicitly
    
    Input:
     - *mod* modification enzyme (string)
     - *i* Nucleosome number (int)
    """
    Type = mod.lower()
    if self.IsRecruit:
      self.num+=1
      self.reaction_num = 'R'+ str(self.num)+':'
      self.reaction = '    '+mod+str(i)+' > E'+Type+mod+str(i)
      self.rate = '    krec*'+mod+str(i)
      self.WriteLastReaction()      

  def EntireModel(self):
    """ Uses all the pre-defined functions in this class to build the entire model. """   
    file = open(self.filename,'w')
    self.Kvalues()   
    for i in range(1,self.N+1):	      
      for self.species_1 in self.species:        
          if self.species_1 == 'M' or self.species_1 =='A':
              self.Noisy1(i)                            # M[i] --> U[i] and A[i] --> U[i] and/or EM[i] --> EU[i] ...
          elif self.species_1 == 'U':
              self.Noisy2(i)                            # U[i] --> M[i] and U[i] --> A[i]

      ##################### Start Explicit simulation of enzymes ###############################
      for enzyme_type in self.landing_zones:		
        for enzyme in self.species:
          self.EnzymeDropping(enzyme,enzyme_type,i)	    # E(type)M[i] --> M[i]
        self.Enzyme(enzyme_type,i)                      # E(type)U[i] --> E(type)Type[i] 

        if self.IsRecruit:                              # Model 2-4-6-8
            self.RecruitEnzymes(enzyme_type,i)          # Type[i] -->  E(type)Type[i], such as M[i] --> EM[i]
	
	if self.IsNeighbours or self.IsLongRange:           # Model 3-4-5-6-7-8
          for self.species_1 in self.species:                    
            if enzyme_type == 'M': cont = 'A'
            elif enzyme_type == 'A': cont = 'M'  
            if self.species_1 != enzyme_type:# and self.species_1 != cont:	# 1-NN
              self.EnzNext(enzyme_type,i,1)  
              self.EnzPrevious(enzyme_type,i,1)
              if self.IsLongRange and not self.IsDecay:	# 1-NN + fixed distance NN                
                  self.EnzNext(enzyme_type,i,self.Threshold)  
                  self.EnzPrevious(enzyme_type,i,self.Threshold)    
              if self.IsLongRange and self.IsDecay:	    # 1-NN + fixed distance NN + decay n
                n=0
                gaus= normalized_dnorm(range(-3,4))
                for pos in range(self.Threshold-3,self.Threshold+3):	# TODO automatic
                  self.EnzNext(enzyme_type,i,pos,gaus[n])  
                  self.EnzPrevious(enzyme_type,i,pos,gaus[n])  
                  n+=1				# decay value (fixed)

      enzymes = self.landing_zones.keys()      
      if self.IsNeighbours or self.IsLongRange:         # Model 3-4-5-6-7-8
        if self.IsEnzymes and len(enzymes) ==1:           
          enz_type = enzymes[0]
          for enz_type in enzymes:                      # if enzyme(s) are explicitly simulated            
            for self.species_1 in self.species:             
              if self.species_1 == enz_type or self.species_1 == 'U':
                self.Previous(enz_type,i,1)
                self.Next(enz_type,i,1)
                if self.IsLongRange and not self.IsDecay:# 1-NN + fixed distance NN                  
                  self.Next(enz_type,i,self.Threshold)  
                  self.Previous(enz_type,i,self.Threshold)  
                if self.IsLongRange and self.IsDecay:	#  1-NN + fixed distance NN + decay n
                  n=0
                  gaus= normalized_dnorm(range(-3,4))
                  for pos in range(self.Threshold-3,self.Threshold+4):
                    self.Next(enz_type,i,pos,gaus[n])
                    self.Previous(enz_type,i,pos,gaus[n])  
                    n+=1

        ####################### End Explicit simulation of enzymes ################################


        ####################### Start No Explicit simulation of enzymes ###########################
        if not self.IsEnzymes:				# No explicit simulation of enzymes
          for self.species_1 in self.species:                           
            for enz_type in self.species:
              if enz_type != self.species_1 and enz_type != 'U':
                self.Previous(enz_type,i,1)
                self.Next(enz_type,i,1)
                if self.IsLongRange and not self.IsDecay:# 1-NN + fixed distance NN                  
                  self.Next(enz_type,i,self.Threshold)  
                  self.Previous(enz_type,i,self.Threshold)  
                if self.IsLongRange and self.IsDecay:	#  1-NN + fixed distance NN + decay n
                  n=0
                  gaus= normalized_dnorm(range(-3,4))
                  for pos in range(self.Threshold-3,self.Threshold+4):  
                    self.Next(enz_type,i,pos,gaus[n])  
                    self.Previous(enz_type,i,pos,gaus[n])  
                    n+=1
                    
         ######################## End No Explicit simulation of enzymes ##########################
   
    ########################### Start Enzyme diffusion part #####################################
    for enzyme_type in self.landing_zones:
      self.EnzymeMovement(enzyme_type)			# E(type)M[i] --> E(type)M[i+-1]
      enzyme_type_zones = self.landing_zones[enzyme_type]
      if enzyme_type_zones == 'all':  enzyme_type_zones = range(1,self.N+1)

      for landing_zone in enzyme_type_zones:	
        if landing_zone <= self.N:
            for species in self.species:
                self.EnzymeLanding(landing_zone,enzyme_type,species)# U[i] --> E(type)U[i]
        else: print "Warning: you have specified a DNA element position -", landing_zone,"- outside the number of nucleosomes:",self.N
    ########################### End Enzyme diffusion part #####################################

    self.WriteParms()
    self.Initials()
    self.num = 0    
    file.close()
    print "Info: The generated model is stored at", self.filename

  def ChangeN(self,n):
    """
    Change the number of nucleosomes
    
    Input:
     - *n* desired number of nucleosomes (integer)
    """
    try:     
        self.N = int(n)
        self.Model = 'own'
        print "Info: The number of nucleosomes is:\t",self.N
    except: print "Error: The number of nucleosomes must be a integer"

  def ModelType(self,num):    
    """
    Choose a build-in model (1-8)
    
    Input:
     - *num* (integer) 1-8
    """
    try: 
        self.Model = int(num) 
        self.N=20
        self.OnRate=1.0
        self.OffRate=0.10
        self.DiffRate=0.6
        self.EnzymeRate=5.0
        self.Recruit=0.1
        self.IsRecruit = False
        self.LandingZones={'M':[10]}
        self.IsNeighbours=False
        self.IsLongRange=False
        self.Threshold=7
        self.NeighbourRate=2.0
        self.EnzNeighRate=10.0
        self.IsDecay=False
        print "Info: ModelType is:\t",self.Model
    except: print "Error: ModelType argument must be an integer between 1 and 8"

  def BuildLandingZones(self,landing_zones):
    """
    Builds the landing zones: locations where enzymes can bind to the DNA
    
    Input:
     - *LandingZones* (dictionairy) The keys are the enzyme types and the values the positions, such as: {'M':[10]}
    """
    if landing_zones != {'M':[10]}:
          self.Model = 'own'

    self.landing_zones  = landing_zones
    if type(self.landing_zones) == dict: pass
    else:
        print "Error: The landing zones input must be a dictionary, like: {'M':[10,11]}"
        print "Error: Here, M is the enzyme type and 10 and 11 are the locations"
        sys.exit()
    if self.landing_zones != {}:
        if type(self.landing_zones.values()[0]) == list: pass
        else:
            print "Error: The landing zones input must be like: {'M':[10]}"
            print "Error: Make sure that the locations are given in a list also if it is only one position"
            sys.exit()     

  def Recruitment(self,IsRecruit = True):
    """
    Activate or deactivate recruitment
    
    Input:
     - *IsRecruit (boolean)*
    """
    self.Model = 'own'
    if IsRecruit == False:
        self.IsRecruit = False
        print "Info: Recruitment is deactivated"         
    else:
        self.IsRecruit = True
        print "Info: Recruitment is activated"
   
  def Neighbours(self,IsNeighbours=True):
    """
    Activate or deactivate neighbour interactions
    
    Input:
     - *IsNeighbours (boolean)*
    """
    self.Model = 'own'
    if IsNeighbours == False:
        self.IsNeighbours = False
        print "Info: Neighbour interactions are deactivated"         
    else:
        self.IsNeighbours = True
        print "Info: Neighbour interactions are activated"
         
  def LongRangeInteractions(self,IsLongRange=True):
    """
    Activate or deactivate long range neighbour interactions
    
    Input:
     - *IsLongRange* (boolean)
    """
    self.Model = 'own'
    if IsLongRange == False:
      self.IsLongRange = False
      print "Info: Long range neighbour interactions are deactivated"         
    else:
      self.IsNeighbours = True
      self.IsLongRange = True
      print "Info: (Long range) neighbour interactions are activated"
      print "Info: The default threshold is 7. Use Threshold(value) to change the threshold."

  def ChangeThreshold(self,threshold):
    """
    Determine the threshold for long range neighbour interactions"
    
    Input:
     - *threshold* (integer)
    """
    try:
      self.Threshold = int(threshold)
      if self.Threshold < self.N:
          pass
          print "Info: The threshold is:\t",self.Threshold
      else:
          print "Error: the threshold is larger then the number of nucleosomes in the model"
          print "Info: the threshold is changed to the number of nucleosomes - 1"
          self.Threshold = self.N-1
      self.Model = 'own'
    except: print "Error: The threshold must be a integer"

  def Decay(self,IsDecay=True):
    """
    Determine if the long range interactions are at one or multiple locations.
    
    Example:    
    Threshold = 7 
    U[i] + M[i+7]  --> M[i] + M[i+7]     k = kneighbour
    U[i] + M[i+6]  --> M[i] + M[i+6]     k = kneighbour * 0.80
    U[i] + M[i+8]  --> M[i] + M[i+8]     k = kneighbour * 0.80
    U[i] + M[i+5]  --> M[i] + M[i+5]     k = kneighbour * 0.41
    U[i] + M[i+9]  --> M[i] + M[i+9]     k = kneighbour * 0.41
    U[i] + M[i+4]  --> M[i] + M[i+4]     k = kneighbour * 0.135
    U[i] + M[i+10] --> M[i] + M[i+10]    k = kneighbour * 0.135

    Input:
     - *IsDecay* (boolean)
    """     
    self.Model = 'own'
    if IsDecay == False:
        self.IsDecay = False
        print "Info: Decay is deactivated"
    else:
        self.IsNeighbours = True
        self.IsLongRange = True
        self.IsDecay = True
        print "Info: (Long range) neighbour interactions are activated"
        print "Info: The default threshold is 7. Use Threshold(value) to change the threshold."
        print "Info: Decay effect is activated"  


if __name__ == "__main__":
  ##################### Main ###################
  n = 20 					# Number of nucleosomes
  modeltype = 2
  #landingzones = {'M':[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]}
  landingzones = {'M':[7],'A':[14]}
  #landingzones = {}
  #landingzones = {'M':[],'A':[]}
  #landingzones = {'M':[10]}

  model = NucModel(N=n,ModelType = modeltype,LandingZones = landingzones)
  model.Build()
  #build = Build(N=n,ModelType = modeltype,LandingZones = landingzones,IsRecruit = 1,IsLongRange=1,IsDecay =1)

