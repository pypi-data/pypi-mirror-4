 #! /usr/bin/env python
"""
Cain/StochSkit Output to StochPy
================================

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: March 13, 2012
"""

import numpy as np

class Species():
    def __init__(self):
        """ Object that is created to store the species amounts """
        pass
        
def GetCainTimeSim(species_amounts,sim_time,n_frames,n_species): 
    """
    get cain time simulation output
    
    Input:
     - *species_amounts* (list)
     - *sim_time* (float)
     - *n_frames* (int)
     - *n_species* (int)
    """   
    sim_output = []
    n=0     
    species_amounts = map(int,species_amounts)
    for frame in xrange(n_frames):            
        time_event = [sim_time[frame]]        
        #for m in xrange(n_species): 
        #    time_event.append(species_amounts[n+m])
        time_event += [species_amounts[n+m] for m in xrange(n_species)]
        n+=n_species         
        sim_output.append(time_event)   
    return sim_output

def GetStochKitTimeSim(file_in,sim_time):
    """
    get stochkit time simulation output
    
    Input:
     - *file_in* (file)
     - *sim_time* (float)     
    """   
    sim_output = []
    IsInit = True
    frame_id = 0       
    for line in file_in:
        line = line.strip()
        dat = line.split('\t')
        if IsInit and dat[0] == 'time':
            time_event_len = len(dat)
            species = dat[1:]                 
            IsInit = False                
        else:         
            time_event = map(int,dat[1:])
            time_event.insert(0,sim_time[frame_id])        
            sim_output.append(time_event)
            frame_id +=1
    return sim_output,species

def GetDistributions(sim_output,species):   
    """
    Get distributions,  means, and standard deviations
    
    Input:
     - *sim_output* (list)
     - *species* (list)
    """    
    n_species = len(species)
    distributions = [{} for i in xrange(n_species)]
    endtime = sim_output[-1][0]        

    for timestep in xrange(len(sim_output)-1):
        for i in xrange(n_species):
            try:
                distributions[i][sim_output[timestep][i+1]] += sim_output[timestep+1][0] - sim_output[timestep][0]        
            except KeyError:
                distributions[i][sim_output[timestep][i+1]] = sim_output[timestep+1][0] - sim_output[timestep][0]
    dist = []
    means = {}
    sds = {}
    for i in xrange(n_species):
        x_i = np.array(sorted(distributions[i]),dtype=int)
        y_i = np.array(distributions[i].values())/endtime     # probability = dt/T
        mean = sum(x_i*y_i)
        mean_sqrt = sum(x_i*x_i*y_i)
        var = mean_sqrt - mean*mean
        sd = var**0.5
        dist.append([x_i,y_i])
        means[species[i]] = mean
        sds[species[i]] = sd
    return dist,means,sds
    
def GetPropensities(SSAmodule,sim_output):
    """
    get Propensities
    
    Input:
     - *SSAmodule* (python object)
     - *sim_output* (list)
    """
    code_str = """"""
    for i in xrange(SSAmodule.n_reactions):                    
        code_str += "prop_vec[%s]=%s\n"  % (i,SSAmodule.propensities[i])
    req_eval_code = compile(code_str,"RateEqEvaluationCode","exec")
    __species__ = Species()                          
    propensities_output = []
    for i in xrange(len(sim_output)):
        prop_vec = np.zeros(SSAmodule.n_reactions)
        [setattr(__species__,SSAmodule.species_stochmatrix[s],sim_output[i][s+1]) for s in xrange(SSAmodule.n_species)]
        try: 
            exec(req_eval_code)    
        except Exception, er:
            print er
        
        prop_vec = list(prop_vec)            
        prop_vec.insert(0,sim_output[i][0])                  
        propensities_output.append(prop_vec)    
    return propensities_output
