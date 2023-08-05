"""
Det2Stoch
=========
Converts Deterministic Rate Equations to Stochastic Rate Equations
Note: This is only done for mass action kinetics

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: 16 September, 2011
"""

import re,sys

def MassActionKinetics(reaction,parameters,reactants):
    """
    Determines if a reaction is of the type: mass-action kinetics
  
    Input:
     - *reaction*: as a string
     - *parameters*: as a list
     -  *reactants*: as a list
  
    Output:
     - *Boolean*
    """ 
    IsMassActionKinetic = True
    #if '/' in reaction:
    #    IsMassActionKinetic = False
    if '+' in reaction:
        IsMassActionKinetic = False
    #if len(parameters) != 1:  16 September 2011
    #    IsMassActionKinetic = False
    #    print 3
    if len(reactants) > 3:
        IsMassActionKinetic = False
    return IsMassActionKinetic

def Stochastic(reaction):
    """
    Checks if mass action kinetic reactions are Stochastic
   
    Input:
     - *reaction*: as a string

    Output:
     - * boolean*
    """
    IsStochastic = False
    if '-' in reaction:
        IsStochastic = True
    return IsStochastic

def DetermineReaction2Change(rate_vector,reactants): 
  """
  Determines for each reaction if it contains deterministic rate equations, which has to be changed.

  Input:
   - *rate vector*: list
   - *reactants of each reaction*: nested list  
  Output:
   - *Information*

  """
  orders   = []
  hors     = []
  HO_info  = []
  
  hor_info = ''
  Information = {}
  j = 0 
  for r in rate_vector:
    reaction = r['RateEq']   
    parms = r['Params']
    reaction_reactants = reactants[j]    
    IsMassAction = MassActionKinetics(reaction,parms,reaction_reactants)
    IsStochastic = Stochastic(reaction)
    IsChange = False
    if IsMassAction and not IsStochastic:
      print 
      n   = -1
      HOR = 0      
      for var in reaction_reactants:
        if re.search(var+ '\*',reaction) or re.search(var+'$',reaction): # REGEX
          count = len(re.findall(var+ '\*',reaction)) + len(re.findall(var+ '$',reaction))
        elif "pow" in reaction: 		              		# Example: k1*S1**2 as input --> k1*pow(S1,2)
            m = re.search(var+'\,\d\)',reaction)		    # pow(S1,2) --> 2
            print m.group(0)
            try:
              count = int(m.group(0)[len(var)+1:-1]) 		# count = 2 (for this example)
            except:
              pass
        if count > HOR:
            HOR = count            
            if count > 1:
              Information[j] = {"highest order":"self."+var,"parm":parms[0][5:],"order": None,'hor':HOR}
              IsChange = True
            n+=1   
      order = n+HOR
    if IsChange:
        Information[j]["order"] = order
    j+=1  
  return Information

def Det2StochPropensities(props,parm_info,rate_vector,reactants):
    """
    Determines for each reaction the propensities to fire at the current time point. 

    Input:
     - *props*: propensities (in a deterministic way)*
     - *parm_info* parameter info
     - *rate_vector*: list
     - *reactants*: nested list  
    Output:
     - *propensities of each reaction*: list
    """
    Information =  DetermineReaction2Change(rate_vector,reactants)
    IsPrint = False
    j=0
    deter_reactions = Information.keys()				# Possible Determistic Eq. indices
    print deter_reactions
    for j in deter_reactions:    
        var = Information[j]['parm']    
        c = parm_info[var]['initial']     
        orders_j = Information[j]['order']
        x_i = Information[j]['highest order']
        hors_j = Information[j]['hor']
        if orders_j == 2:	
            if hors_j == 2:					# v = c*X[i]^2        
                a_j = str(0.5*c)+'*'+x_i+'*('+x_i+'-1)'
                props[j] = a_j
                IsPrint  = True
        elif orders_j == 3:
            if hors_j == 2:		       			# v = c*X[i]^2*X[j]        
                for reactant in reactants[j]:
                    if reactant != x_i: x_j = reactant
                a_j = str(0.5*c)+'*'+x_i+'*('+x_i+'-1)*'+x_j        
                IsPrint = True
            elif hors_j == 3:					# v = c*X[i]^3        
                a_j = str(c/6.0)+'*'+x_i+'*('+x_i+'-1)*('+x_i+'-2)'        
                IsPrint = True
        j+=1
    if IsPrint: print "Deterministic rate equations are succesfully converted into stochastic rate equations"  
    return props
