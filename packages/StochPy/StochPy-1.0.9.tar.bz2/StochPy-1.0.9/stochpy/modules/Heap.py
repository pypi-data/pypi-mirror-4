#! /usr/bin/env python
"""
Indexed Priority Queue (IPQ)
============================

This module builds a index priority queue (IPQ) - Heap - which contains a lot of usefull functions that can manipulate this heap so that it is not necessary to rebuild the whole heap if something changes. 

The Next Reaction Method from Gibson&Bruck uses such a heap to optimize the speed of the exact stochastic simulation algorithm, which goes to log2(number of reactions) if the heap is sparse.

Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: January 22, 2010
"""
import math,copy,heapq,sys
from cStringIO import StringIO

def show_tree(tree, total_width=36, fill=' '):
  """
  Prints a tree

  Input:
   - *tree*
   - *total_width* [default = 36]
   - *fil* [default = ' ']
  """
  output = StringIO()
  last_row = -1
  for i, n in enumerate(tree):
    if i:
      row = int(math.floor(math.log(i+1, 2)))
    else:
     row = 0
    if row != last_row:
      output.write('\n')
    columns = 2**row
    col_width = int(math.floor((total_width * 1.0) / columns))
    output.write(str(n).center(col_width, fill))
    last_row = row
  print output.getvalue()
  print '-' * total_width
  print
  return

class BinaryHeap():
  """ This class builds and manipulates a binary tree"""
  def __init__(self,taus):
   """
   Build initial binary tree
   Input: 
    - *taus*: list that contains for each reaction the time to fire 
   """
   self.taus = taus
   self.heap = copy.copy(taus)
   heapq.heapify(self.heap)
   self.heap_size = len(self.heap)   
   self.index = []
   self.dict = {}
   j = 0
   for pair in self.taus:
     location = self.heap.index(pair)
     self.index.append(location)      
     self.dict[location] = j
     j+=1

  def Print(self):
    """Print binary tree"""
    show_tree(self.heap)  

  def GetParent(self):
    """ Determine the parents from a certain node. Note that it returns the indices of the parents """    
    if self.pos == 0:			# top node has no parent. 
      self.ParentPos = 0
    elif self.pos % 2 == 0:		
      self.ParentPos = (self.pos-2)/2
    else:
      self.ParentPos = (self.pos-1)/2    

  def GetChildren(self):
    """ Determine the possible children from a certain node. It returns the indices of the children """
    if self.heap_size <= (2*self.pos+1):
      self.Children = []
    elif self.heap_size == (2*self.pos+1):
      self.Children = [2*self.pos+1]
    else:
      self.Children = [2*self.pos+1,2*self.pos+2]    

  def Swap(self,r1,r2): 
    """ Swaps two nodes in the binary tree with indices r1 and r2"""         
    temp = self.heap[r1]
    self.heap[r1] = self.heap[r2]
    self.heap[r2] = temp
    
    a = self.dict[r1]
    b = self.dict[r2]

    temp = self.dict[r1]
    self.dict[r1] = self.dict[r2]
    self.dict[r2] = temp
    
    temp = self.index[a]
    self.index[a] = self.index[b]
    self.index[b] = temp  
  
  def Update_AUX(self,tau_node,j):
    """
    Update the binary tree. This function uses GetParent,GetChildren and Swap to change the positions of nodes in the tree, so it does not build a new tree, but updates some of the nodes, which is an advantage if the tree is sparse.
    
    Input: 
     - *tau*: updated tau value
     - *j*: reaction number

    Note: This function is far from optimized
    """      
    ##self.pos  = self.heap.index((tau_node,j)) 
    self.pos = self.index[j]		# 22/01/11
    self.GetParent()
    self.GetChildren() 
    
    tau_parent = self.heap[self.ParentPos][0]       
    tau_children_min = 1000e1000
    for i in self.Children:    
      try:
        possible_min = self.heap[i][0]   	# lowest tau value
        if possible_min < tau_children_min:
          tau_children_min = possible_min
          min_children_index = i
      except: pass

    ##print self.heap
    ##print tau_node, tau_parent,tau_children_min
    r2 = self.pos
    self.Done = 0    
    if tau_node < tau_parent:
      r1 = self.ParentPos
      self.Swap(r1,r2) 
    elif tau_node > tau_children_min:      
      r1 = min_children_index      
      self.Swap(r1,r2)
    else: self.Done = 1     
    
 
############################ Main ########################

if __name__ == "__main__":
  init = [(4.2,1),(3.7,2),(1000e1000,3),(5.5,4),(9.1,5),(2.0,6),(8.9,7),(1.3,8),(7.3,9),(10.1,10)]
  tree = BinaryHeap(init)    
  show_tree(tree.heap)
