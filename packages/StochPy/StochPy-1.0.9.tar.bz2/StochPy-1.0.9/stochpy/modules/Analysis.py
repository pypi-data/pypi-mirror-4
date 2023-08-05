#! /usr/bin/env python
"""
Analysis
========

This module provides functions for Stochastic Simulation Algorithms Analysis (SSA). Implemented SSAs import this module to perform their analysis. It plots time simulations, distributions and waiting times.

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: July 09, 2012
"""

import copy
try:
    import matplotlib.pyplot as plt  
except: 
    print "Matplotlib module is not available, so it is impossible to create plots"

try: 
    import numpy as np
except:
    print "Error: NumPy module is not available. "
    sys.exit()

import copy
from math import ceil,log,sqrt

def getDataForTimeSimPlot(data,n_events2plot = 10000):
    """
    getDataForTimeSimPlot(data,n_events2plot = 10000)
    
    Input:
     - *data* (numpy array)
     - *n_events2plot* [default = 10000] (integer)
    """
    
    len_data = len(data)    
    if len_data > 100000: # use n_events2plot only if datasets become too large     
        data2plot = [data[0]]
        step_size = len_data/int(abs(n_events2plot))        
        for i in xrange(step_size,len_data,step_size):
            t = data[i][0]            
            data_point = copy.deepcopy(list(data2plot[-1][1:]))
            data_point.insert(0,t)
            data2plot.append(data_point)
            data2plot.append(data[i])
        print "Info: Plotting", n_events2plot, "out of", len_data,"points.\nUse the argument 'n_events2plot' to alter the number of plotted events.\nUse n_events2plot='All' to plot all the data points."  
    else: 
        data2plot = copy.deepcopy(list(data))
        j=1       
        for i in xrange(1,len_data):
            t = data[i][0]
            data_prev = copy.deepcopy(data[i-1])
            data_prev[0] = t            
            data2plot.insert(j,data_prev)   
            j+=2              
    return np.array(data2plot)

def Count(data_,edges_):
    """
    Count(data_,edges_)
    
    Input:
     - *data_*
     - *edges_*
    """
    n_edges = len(edges_)
    output = np.zeros(n_edges)
    for value in data_:    
        for i in xrange(n_edges-1):
            if (value >= edges_[i]) and (value < edges_[i+1]):
                output[i]+=1  
    return np.array(output)   
    
def Binning(x,y,bin_size):
    """
    Binning(x,y,bin_size)
    
    Binning of the PDF
    
    Input:
     - *x* list of x-values
     - *y* list of probabilities for each x[i]
     - *bin_size* (integer)     
    """
    temp = []
    number_of_prob = len(x)
    if bin_size > number_of_prob or bin_size < 1:
        print "Bin Size is negative or too large and therefore re-setted to 1"
        bin_size = 1
    if bin_size > 1:
        dif = x[1]-x[0]
        if dif>1 and not bin_size%2:
            bin_size /= dif
        elif dif>1 and bin_size%2:
           n=0
           for i in xrange(x[0],x[-1]):
               if i not in x:
                    for j in xrange(dif-1):
                        x.insert(i-x[0],i)
                        y.insert(i-x[0],y[n])
                    n+=dif
        number_of_prob = len(x)
        max_index = y.index(max(y)) # maximum prob index
        ### Get interval around the maximum value ###
        interval = xrange(int(max_index-(bin_size/2.0)+1),max_index+int(round(bin_size/2.0)+1)) # Get interval around maximum prob
        min_value = min(interval)
        while min_value < 0:
            interval.remove(min_value)
            interval.append(interval[-1]+1)
            min_value = min(interval)
        while interval[-1] > (number_of_prob-1):
            interval.pop()
            interval.insert(0,interval[0]-1)
        
        #############################################   
        temp.append([x[interval[-1]]+0.5,sum(y[interval[0]:interval[-1]+1])/float(bin_size)])        
        individuals = []                                  # locations with bin_size = 1
        if interval[0]:
            nbins1 = (interval[0]-1)/bin_size             # nbins before interval around max prob
            start1 = interval[0]-1 - nbins1*bin_size      # start location of binning before interval
            if interval[0] == 1:
                individuals.append(0)
        else:                                             # interval around max goes until the first species amount
            temp.append([x[interval[0]]+0.5,sum(y[interval[0]:interval[-1]+1])/float(bin_size)]) 
            nbins1 = 0
            start1 = 0
            individuals.append(0)
        start2 = interval[-1]                             # start location of binning after interval
        nbins2 = (number_of_prob-1 - start2)/bin_size     # nbins after interval around max prob
        individuals += [i for i in xrange(0,start1)]        
        individuals += [i for i in xrange(start2+1+(bin_size*nbins2),number_of_prob)]
        x_ = np.array(x)
        y_ = np.array(y)
        for i in xrange(nbins1):            
            temp.append([x_[start1+bin_size]+0.5,sum(y_[start1:start1+bin_size])/float(bin_size)])
            start1+=bin_size   
        for i in xrange(nbins2):  
            temp.append([x[start2+bin_size]+0.5,sum(y[start2:start2+bin_size])/float(bin_size)]) 
            start2+=bin_size
        for i in individuals:
            temp.append([x[i],y[i]])
        data = np.array(sorted(temp))       
    else:
        data = np.array([x,y]).transpose()
        data[:,0]+=0.5
    return data

def LogBin(data,factor):  
    """
    LogBin(data,factor)
    
    Function that creates log bins  

    Input: 
     - *data* (list)
     - *factor* (float) determines the width of the bins
    Output: 
     - *x* (list)
     - *y* (list)
     - *nbins* (integer)
    """
    xmin = float(min(data))    
    nbins = int(ceil(log(max(data)/xmin)/log(factor)))  
    edges = np.zeros(nbins)
    edges[0] = xmin     
    for i in xrange(1,nbins):
        edges[i] = edges[i-1]*factor
  
    x  = edges[0:(nbins-1)]+np.diff(edges)/2  
    dp = Count(data,edges)
    ry = np.array(dp[0:(nbins-1)])  
    dedges = np.array(np.diff(edges))  
    y = ry/(sum(ry)*dedges) 
    return(x,y,nbins)

def ObtainWaitingtimes(data_stochsim,num_reactions):
    """    
    ObtainWaitingtimes(data_stochsim,num_reactions)
    
    This function extracts the waiting times for each reaction of the model from the used SSA output.

    Input:
     - *data_stochsim* (python data object) that stores all simulation data
     - *num_reactions* (integer)
    output:
     - *waiting times* (nested list) 
  
    Note: It is impossible to use this function in combination with the Tau-leaping method, because the Tau-Leaping results are not exact!
    """
    time = data_stochsim.time.flatten()
    fired_reactions = data_stochsim.fired_reactions             # Reactions that fired at some time point
    waiting_times = {}
    last_fire_time = {}
    unique_fired_reactions = np.unique(fired_reactions)
    for reaction in xrange(1,num_reactions+1):     
        waiting_times[reaction] = []

    for (current_time,reaction) in zip(time,fired_reactions):
        for i in xrange(1,num_reactions+1): 
            if reaction == i:        
                try:       
                    last_fire_time[reaction]                    # A previous firing time is necessary
                    waiting_times[reaction].append(current_time-last_fire_time[reaction]) # Add inter-arrival time
                    last_fire_time[reaction] = current_time     # Update last firing time
                except:
                    last_fire_time[reaction] = current_time     # Initial firing time
    return waiting_times

def ObtainInterpolationResults(interpolated_output,points):
    """
    ObtainInterpolationResults(interpolated_output,points)
    
    Gets the interpolated output after interpolation

    Input: 
     - *interpolated_output* (nested list)
     - *points* (list) of integer time points of interpolation
    """
    means = []
    sds = []
    i=0
    for species in interpolated_output:
        j=0
        for trajectory_amounts in species:
            interpolated_output[i][j] = trajectory_amounts
            j+=1
        i+=1
   
    for interpolated_species_output in interpolated_output:
        means.append(np.mean(interpolated_species_output,0))
        sds.append(np.std(interpolated_species_output,0))    
    return means,sds

class DoPlotting():
  """
  This class initiates the plotting options.

  Input: 
   - *species_labels* (list) [S1,S2, ..., Sn]
   - *rate_labels* (list) [R1, R2, ..., Rm] 
  """
  def __init__(self,species_labels,rate_labels,plotnum=1):
      self.species_labels = species_labels
      self.rate_labels = rate_labels
      self.number_of_rates = len(rate_labels)
      self.plotnum  = plotnum      
      self.colors = ['#0000FF','#00CC00','#FF0033','#FF00CC','#6600FF','#FFFF00','#000000','#CCCCCC','#00CCFF','#99CC33','#FF6666','#FF99CC','#CC6600','#003300','#CCFFFF','#9900FF','#CC6633']
    
  def ResetPlotnum(self):
      """ Reset figure numbers if trajectories > 1 """
      self.plotnum = 1 
  
  def TimeSimulation(self,data,n_events2plot,species2plot,traj_index,linestyle,marker,colors,title):
      """
      TimeSimulation(data,n_events2plot,species2plot,traj_index,linestyle,marker,colors,title)

      Input:
       - *data* (array)
       - *n_events2plot* (integer)
       - *species2plot* (list) 
       - *traj_index* (integer)       
       - *linestyle* (string)
       - *marker* string)
       - *colors* (list)
       - *title* (string)
      """
      plt.figure(self.plotnum)
      species2plot_indices = [self.species_labels.index(species) for species in species2plot]
      if len(species2plot) == 1:
          j = traj_index
      else:
          j=0      

      data = getDataForTimeSimPlot(data,n_events2plot)      
      time = data[:,0]
      for i in species2plot_indices:         
          if colors == None:              
              if j >= len(self.colors):                  
                  j=0                  
          elif j == len(colors):
             j=0
          y = data[:,i+1]          
          if colors == None:
              plt.plot(time,y,marker,ls = linestyle,color = self.colors[j])
          else:   
              try: 
                  plt.plot(time,y,marker,ls = linestyle,color = colors[j])
              except:
                  plt.plot(time,y,marker,ls = linestyle,color = self.colors[j]) 
                  colors = None
          j+=1  
 
      plt.legend(species2plot,numpoints=1,frameon=True)      
      plt.title(title)
      plt.xlabel('Time') 
      plt.ylabel('Species Amounts')   
 
  def Distributions(self,distributions,species2plot,traj_index,linestyle,colors,title,bin_size):
      """
      Distributions(distributions,species2plot,traj_index,linestyle,colors,title,bin_size)
      
      Plots the distributions of the simulated metabolites/molecules.

      Input:
       - *distributions* (nested list)
       - *species2plot* (list)
       - *traj_index* (integer)
       - *colors* (list)
       - *title* (string)
      """ 
      plt.figure(self.plotnum)
      species2plot_indices = [self.species_labels.index(species) for species in species2plot]      
      if len(species2plot) == 1:
          j = traj_index
      else:
          j=0

      for i in species2plot_indices: 
          x = list(copy.copy(distributions[i][0]))
          y = list(copy.copy(distributions[i][1]))
          data = Binning(x,y,bin_size)
          if colors == None:              
              if j >= len(self.colors):                  
                  j=0                  
          elif j == len(colors):
             j=0          
          
          if colors == None:
              plt.step(data[:,0],data[:,1],ls = linestyle,color = self.colors[j])	# Plot
          else:
              try: 
                  plt.step(data[:,0],data[:,1],ls = linestyle,color = colors[j])
              except: 
                  plt.step(data[:,0],data[:,1],ls = linestyle,color = self.colors[j])
                  colors = None
          j+=1

      plt.legend(species2plot,numpoints=1,frameon=True)
      plt.title(title)
      plt.xlabel('Number of Molecules')
      plt.ylabel('Probability Density')


  def Propensities(self,data,n_events2plot,rates2plot,traj_index,linestyle,marker,colors,title):
      """
      Propensities(data,n_events2plot,rates2plot,traj_index,linestyle,marker,colors,title)
      
      Tracks the propensities through time

      Input: 
       - *data* (array)
       - *n_events2plot* (integer)
       - *rates2plot* (list)
       - *traj_index* (integer)
       - *linestyle* (string)
       - *title* (string)
      """
      plt.figure(self.plotnum)      
      rates2plot_indices = [self.rate_labels.index(rates) for rates in rates2plot]      
      data = getDataForTimeSimPlot(data,n_events2plot)
      time = data[:,0]   
      if len(rates2plot) == 1:
          j = traj_index
      else:
          j=0

      for i in rates2plot_indices:
          y = data[:,i+1]
          if colors == None:              
              if j >= len(self.colors):                  
                  j=0                  
          elif j == len(colors):
              j=0
          if colors == None:
              plt.plot(time,y,marker,ls = linestyle,color = self.colors[j])
          else:
              try:
                  plt.plot(time,y,marker,ls = linestyle,color = colors[j])
              except:
                  plt.plot(time,y,marker,ls = linestyle,color = self.colors[j])
                  colors = None
          j+=1

      plt.legend(rates2plot,numpoints=1,frameon=True)
      plt.title(title)
      plt.xlabel('Time')
      plt.ylabel('Propensities')

  def Waitingtimes(self,waiting_times,rates2plot,traj_index,linestyle,marker,colors,title):
      """
      Waitingtimes(waiting_times,rates2plot,traj_index,linestyle,marker,colors,title)
      
      Plots the waiting times for each reaction in the model. Makes use of ObtainWaitingtimes to derive the waiting times out of the SSA output.
 
      Input: 
       - *waiting_times* (dict)
       - *rates2plot* (list)
       - *traj_index* (integer)
       - *linestyle* (string)
       - *title* (string)
      """
      plt.figure(self.plotnum)
      rates2plot_indices = [self.rate_labels.index(rates) for rates in rates2plot]          
      if len(rates2plot) == 1:
          j = traj_index
      else:
          j=0

      legend_names = []
      for i in rates2plot_indices:                        
              waiting_time = waiting_times[i+1]
              if len(waiting_time) > 1:			        # At least 2 waiting times are necessary per reaction
                  (x,y,nbins) = LogBin(waiting_time,1.5) 	# Create logarithmic bins
                  
                  if colors == None:              
                      if j >= len(self.colors):                  
                          j=0                  
                  elif j == len(colors):
                      j=0                  
                  if colors == None:
                      plt.loglog(x,y,marker,ls = linestyle,color = self.colors[j])              
                  else:
                      try: 
                          plt.loglog(x,y,marker,ls = linestyle,color = colors[j])
                      except:
                          plt.loglog(x,y,marker,ls = linestyle,color = self.colors[j])
                          colors = None
                            
                  legend_names.append(self.rate_labels[i])
                  j+=1


      plt.title(title)
      plt.xlabel('Interarrival time t')
      plt.ylabel('Probability Mass')
      plt.legend(legend_names,numpoints=1,frameon=True)
         
  def AverageTimeSimulation(self,means_set,sds_set,time,species2plot,linestyle,marker_,colors,title):
      """
      AverageTimeSimulation(means_set,sds_set,time,species2plot,linestyle,marker_,colors,title)
      
      Plots the interpolated time simulation results. Makes use of the ObtainInterpolationResults function, which determines the input for this function out of the SSA output.

      Input:
       - *means_set* (nested list)
       - *sds_set* (nested list)
       - *time* (list)
       - *linestyle* (string)
       - *title* (string)
      """
      plt.figure(self.plotnum)
      species2plot_indices = [self.species_labels.index(species) for species in species2plot] 
      j=0
      for i in species2plot_indices:
          means = means_set[i]
          sds = sds_set[i]
          if colors == None:              
              if j >= len(self.colors):                  
                  j=0                  
          elif j == len(colors):
             j=0
          if colors == None:
              plt.errorbar(time,means,yerr = sds,color = self.colors[j],ls = linestyle,marker = marker_,label = species2plot[i]) # plot with y-axis error bars
          else:
              try:
                  plt.errorbar(time,means,yerr = sds,color = colors[j],ls = linestyle,marker = marker_,label = species2plot[i])
              except:
                  plt.errorbar(time,means,yerr = sds,color = colors[j],ls = linestyle,marker = marker_,label = species2plot[i])
                  colors = None
          j+=1
      plt.legend(numpoints=1,frameon=True)
      plt.title(title)
      plt.xlabel('Time')
      plt.ylabel('Species Amounts')
