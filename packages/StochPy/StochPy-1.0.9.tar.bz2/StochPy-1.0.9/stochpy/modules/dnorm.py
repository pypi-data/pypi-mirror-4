"""
DNORM
=====

Module which contains functions that can calculate the density for the normal distribution for given x-values and it has the ability to normalize these densities.

See http://mathworld.wolfram.com/NormalDistribution.html/ for more information about the normal distribution

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: Augustus 10, 2010
"""

from math import sqrt,pi,exp
import sys

def dnorm(X,mu=0,sigma=1.5):
  """
  Named after the dnorm function from programming language R.
  Density generation for the normal distribution with mean = mu and standard deviation = sigma.
  
  Input: 
   - *x* vector or integer of 'x-axis' values
   - *mu* [default = 0]
   - *sigma* [defaul = 1.5]
  Output: 
   - float or list with floats containing the calculated values
  """
  dnorm_list = []  
  constant = 1.0/sqrt(2.0*pi*sigma**2)		# Calc once
  denominator = (2.0*sigma**2)  		# Calc once
  if type(X) == list: 				# For a list of int/floats
    for x in X:
      value = constant*exp(-((x-mu)**2)/denominator)
      dnorm_list.append(value) 
    return dnorm_list    
  elif type(X) == int or float:			# For a single int/float
    value = constant*exp(-((x-mu)**2)/denominator)
    return value

  else:
    print "The first argument (X) must be a list with integers/floats or a single integer/float.\n"
    sys.exit()    

def normalized_dnorm(X,mu=0,sigma=1.5):
  """
  Generate normalized values based on the maximum of the bell-shaped normal distribution. 
  It uses the self defined dnorm function to calculate these values.
  
  Input: 
   - *x* : vector or integer of 'x-axis' values
   - *mu* [default = 0]
   - *sigma* [defaul = 1.5]
  Output: 
   - float or list with floats containing the calculated values
  """
  unnormalized = dnorm(X,mu,sigma)		# Do unnormalized dnorm
  max_ = 1.0/sqrt(2.0*pi*sigma**2)		# Max value at x = 0

  norm_dnorm_list = []
  if type(X) == list:				# For a list of int/floats
    for x in unnormalized:
      norm_dnorm_list.append(x/max_)
    return norm_dnorm_list
  elif type(X) == int or float:    		# For a single int/float
    return unnormalized/max_

####################### Example ##################
if __name__ == "__main__":
  mu = 0
  sigma = 2
  print normalized_dnorm(range(-5,5),mu,sigma)
  #print normalized_dnorm(range(-5,5))
  ## func(range(-neighbour,neighbour),mu=0,sigma=1  
