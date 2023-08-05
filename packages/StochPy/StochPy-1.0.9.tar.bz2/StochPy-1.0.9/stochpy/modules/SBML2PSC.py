"""
Written by TR Maarleveld, Amsterdam, The Netherlands
E-mail: tmd200@users.sourceforge.net
Last Change: February 23, 2012
"""

class SBML2PSC():
  """
  Module that converts SBML models into PSC models if libxml and libsbml are installed

  Usage:
  >>> converter = stochpy.SBML2PSC()
  >>> converter.SBML2PSC('Burstmodel.xml','/home/user/Stochpy/pscmodels/') 
  """   
  def __init__(self):
      pass

  def SBML2PSC(self,sbmlfile, sbmldir=None, pscfile=None, pscdir=None):
      """
      Converts a SBML file to a PySCeS MDL input file.

      Input:
       - *sbmlfile*: the SBML file name
       - *sbmldir*: [default = None] the directory of SBML files (if None current working directory is assumed)
       - *pscfile*: [default = None] the output PSC file name (if None *sbmlfile*.psc is used)
       - *pscdir*: [default = None] the PSC output directory (if None the pysces.model_dir is used)
      """
      import stochpy.modules.PyscesInterfaces as module
      module.Core2interfaces().convertSBML2PSC(sbmlfile,sbmldir,pscfile,pscdir, netStoich=True)
