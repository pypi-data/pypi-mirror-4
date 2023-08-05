#! /usr/bin/env python
"""
StochPy - Stochastic Modeling in Python (http://stompy.sourceforge.net)

Copyright (C) 2010-2012 T.R Maarlveld, B.G. Olivier all rights reserved.

Timo R. Maarleveld (tmd200@users.sourceforge.net)
VU University, Amsterdam, Netherlands

Permission to use, modify, and distribute this software is given under the
terms of the StochPy (BSD style) license. 

NO WARRANTY IS EXPRESSED OR IMPLIED.  USE AT YOUR OWN RISK.
"""

__doc__ =   """        
            StochPy: Stochastic Modeling in Python
            =====================================
            
            StochPy (Stochastic modelling in Python) is an easy-to-use package, which provides several stochastic simulation algorithms (SSAs), which can be used to simulate a biochemical system in a stochastic manner. Further, several unique and easy-to-use analysis techniques are provided by StochPy.

            Actually, StochPy is an extension of PySCeS. PySCeS - the Python Simulator for Cellular Systems - is an extendable toolkit for the analysis and investigation of cellular systems. It is available for download from: http://pysces.sourceforge.net

            
            Options:
            --------
            - Stochastic Simulations
            - Variety of stochastic simulation output analysis:
              --> Time Simulation
              --> Distribution
              --> Waiting times
              --> Propensities
            - Cell Division simulations
            - SBML and PSC MDL input format.

            StochPy can be used in an interactive Python shell:

            Usage
            -----            
            >>> import stochpy
            >>> utils = stochpy.Utils()
            >>> utils.doExample1()
            >>> utils.doExample(2)
            >>> smod = stochpy.SSA()   # stochastic simulation algorithm module            
            >>> help(smod)
            >>> help(stochpy.SSA)      # (some windows versions)
            >>> stochpy?
            >>> smod.DoStochSim()
            >>> cmod = stochpy.CellDivision()
            >>> cmod.DoCellDivisionStochSim() 
            >>> converter = stochpy.SBML2PSC()
            >>> converter?
            >>> help(stochpy.SBML2PSC) # (some windows versions)                        
            ...
            ...
            """

__version__ = '1.0.9'

import os,shutil,readline,sys

try:
    from numpy.distutils.core import setup, Extension
except Exception, ex:
    print ex
    print "StochPy requires NumPy\n"
    print "See http://numpy.scipy.org/ for more information about NumPy"
    os.sys.exit(-1)

try:
    import matplotlib.pyplot as plt
    import pylab
except:
    print "Warning: The Matplotlib module is not available, so it is impossible to create plots"
    print "Info: See http://matplotlib.sourceforge.net/ for more information about Matplotlib"

def InitiateModels(directory):
    """
    Build several models written in PSC MDL and SBML
    
    Input:
     - *directory* (string)
    """
    import pscmodels
    import stochpy.pscmodels.Burstmodel as Burstmodel
    import stochpy.pscmodels.BirthDeath as BirthDeath
    import stochpy.pscmodels.ImmigrationDeath as ImmigrationDeath
    import stochpy.pscmodels.DecayingDimerizing as DecayingDimerizing
    import stochpy.pscmodels.Autoreg as autoreg
    import stochpy.pscmodels.Autoreg_xml as autoreg_xml
    import stochpy.pscmodels.CellDivision as celldivision
    import stochpy.pscmodels.dsmts_001_01 as dsmts_001_01
    import stochpy.pscmodels.dsmts_001_11 as dsmts_001_11
    import stochpy.pscmodels.dsmts_001_19 as dsmts_001_19 
    import stochpy.pscmodels.dsmts_002_10 as dsmts_002_10     
    import stochpy.pscmodels.dsmts_003_03 as dsmts_003_03
    import stochpy.pscmodels.dsmts_003_04 as dsmts_003_04
    import stochpy.pscmodels.chain5 as chain5
    import stochpy.pscmodels.chain50 as chain50
    import stochpy.pscmodels.chain500 as chain500
    import stochpy.pscmodels.chain1500 as chain1500  
    import stochpy.pscmodels.OneNucleosome as OneNucleosome
    import stochpy.pscmodels.TwoNucleosome as TwoNucleosome
    import stochpy.pscmodels.ThreeNucleosome as ThreeNucleosome

    models = {}
    models['Burstmodel'] = Burstmodel.model
    models['ImmigrationDeath'] = ImmigrationDeath.model
    models['BirthDeath'] = BirthDeath.model
    models['DecayingDimerizing'] = DecayingDimerizing.model
    models['Autoreg'] = autoreg.model
    models['Autoreg.xml'] = autoreg_xml.model
    models['CellDivision'] = celldivision.model
    models['dsmts-001-01.xml.psc'] = dsmts_001_01.model
    models['dsmts-001-11.xml.psc'] = dsmts_001_11.model
    models['dsmts-001-19.xml.psc'] = dsmts_001_19.model
    models['dsmts-002-10.xml.psc'] = dsmts_002_10.model
    models['dsmts-003-03.xml.psc'] = dsmts_003_03.model
    models['dsmts-003-04.xml.psc'] = dsmts_003_03.model
    #models['OneNucleosome'] = OneNucleosome.model
    #models['TwoNucleosome'] = TwoNucleosome.model
    #models['ThreeNucleosome'] = ThreeNucleosome.model  
    models['chain5'] = chain5.model
    models['chain50'] = chain50.model
    models['chain500'] = chain500.model
    models['chain1500'] = chain1500.model

    model_names = sorted(models)
    dir_models = os.listdir(directory)
    for mod_name in model_names:        
        if '.xml' in mod_name:            
            if mod_name not in dir_models: 
                print "Model %s copied to %s" % (mod_name ,directory)              
                file = open(os.path.join(directory,mod_name),'w')
                file.write(models[mod_name])  
                file.close()
        else:
            if mod_name+'.psc' not in dir_models: 
                print "Model %s copied to %s" % (mod_name+'.psc' ,directory)                    
                file = open(os.path.join(directory,mod_name+'.psc'),'w')
                file.write(models[mod_name])
                file.close()
    del Burstmodel,ImmigrationDeath,DecayingDimerizing,chain5,chain50,chain500,chain1500,autoreg,autoreg_xml,dsmts_001_01,dsmts_003_04

output_dir = None
model_dir = None
Initiate = False
if os.sys.platform != 'win32':
    if not os.path.exists(os.path.join(os.path.expanduser('~'),'Stochpy')):
        os.makedirs(os.path.join(os.path.expanduser('~'),'Stochpy'))
    if not os.path.exists(os.path.join(os.path.expanduser('~'),'Stochpy', 'pscmodels')):
        os.makedirs(os.path.join(os.path.expanduser('~'),'Stochpy','pscmodels'))        
    if not os.path.exists(os.path.join(os.path.expanduser('~'),'Stochpy', 'temp')):
        os.makedirs(os.path.join(os.path.expanduser('~'),'Stochpy','temp'))

    output_dir = os.path.join(os.path.expanduser('~'),'Stochpy')
    model_dir = os.path.join(os.path.expanduser('~'),'Stochpy','pscmodels')
    temp_dir = os.path.join(os.path.expanduser('~'),'Stochpy','temp')
    InitiateModels(model_dir)
else:
    if not os.path.exists(os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy')):
        os.makedirs(os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy'))
    if not os.path.exists(os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','pscmodels')):
        os.makedirs(os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','pscmodels'))        
    if not os.path.exists(os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','temp')):
        os.makedirs(os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','temp'))
        
    output_dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy',)
    model_dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','pscmodels')
    temp_dir = os.path.join(os.getenv('HOMEDRIVE')+os.path.sep,'Stochpy','temp')
    InitiateModels(model_dir)
 
import modules
import lib
import implementations
from modules.SBML2PSC import SBML2PSC
from modules.StochSim import SSA
#from modules.NucleosomeModel import NucModel
#from modules.NucleosomeSimulations import NucSim
from modules.StochPyUtils import Utils
from modules.StochPyCellDivision import CellDivision
from modules.StochPyDemo import Demo

def DeletePreviousOutput(path,type):
    """
    Delete output of earlier simulations
    
    Input:
     - *path* (string)
     - *type* (string)
    """
    for filename in os.listdir(path):
        if filename.endswith(type):
            filename_path = os.path.join(path,filename)
            os.remove(filename_path)
            
def DeleteExistingData(path):
    """
    Delete all existing StochKit simulation data
    
    Input:
     - *path* (string)
    """
    if os.path.exists(path):
        for maps in os.listdir(path):
            dir2delete = os.path.join(path,maps)
            shutil.rmtree(dir2delete, ignore_errors=True)
            
def SaveInteractiveSession(filename='interactiveSession.py',path=output_dir): 
    """
    Save the interactive session
    
    Input:
     - *filename*: [default = interactiveSession.py'] (string)
     - *path*: (string)
    """   
    historyPath = os.path.join(path,filename)
    if os.path.exists(path):
        readline.write_history_file(historyPath)
        file_in = open(historyPath,'r')
        history_list = file_in.readlines()
        n_import_statement = 0
        for command in history_list:            
            if 'import stochpy' in command:
               n_import_statement +=1
       
        n = 0
        file_out = open(historyPath,'w')
        for command in history_list:
            if "import stochpy" in command:             
               n+=1
            if n==n_import_statement:     
                file_out.write(command)
        file_out.close()
        print "Info: Interactive session successfully saved at", historyPath
        print "Info: use 'ipython", filename+"' to restart modelling with this interactive session"        
    else:
        print "Error: directory does not exist" 
        
    
DeletePreviousOutput(temp_dir,'.dat')
DeletePreviousOutput(temp_dir,'.xml')
DeletePreviousOutput(temp_dir,'.txt')
DeletePreviousOutput(temp_dir,'temp_parse_module')
DeleteExistingData(temp_dir)
#readline.clear_history()

print """
#######################################################################
#                                                                     #
#            Welcome to the interactive StochPy environment           #
#                                                                     #
#######################################################################
#  StochPy: Stochastic modelling in Python                            #
#  http://stompy.sourceforge.net                                      #
#  Copyright(C) T.R Maarleveld, B.G. Olivier, F.J Bruggeman 2010-2012 #
#  Email: tmd200@users.sourceforge.net                                #
#  VU University, Amsterdam, Netherlands                              #
#  Centrum Wiskunde Informatica, Amsterdam, Netherlands               #
#  StochPy is distributed under the BSD licence.                      #
#######################################################################
"""
print "Version",__version__
print "Output Directory:",output_dir
print "Model Directory:", model_dir

del Initiate
