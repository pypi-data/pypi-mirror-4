#encoding:UTF-8
"""
MARLib - Music Signal Processing and Analysis Library
  Under development by the Music and Audio Research Lab (MARL) at NYU
  http://marl.smusic.nyu.edu
  
=====

Provides
    1. Abstracted audio file reading & writing (internal buffering)
    2. Integration with SoX for various CODEC support

Under Development
    1. Basic time-frequency transforms
    2. 

How to use the documentation
----------------------------
Documentation is available inline as docstrings provided within the code. In 
time, it is our intention to host a Sphynx-like online reference to facilitate
ease of use.
     

Examples provided assume that each module has been imported as its first
characters in uppercase::

  >>> import marlib.audiofile as AF
  >>> import marlib.timefreq as TF
      ...

...where code snippets are indicated by three greater-than signs.

Use the built-in ``help`` function to view a function's docstring::

  >>> help(TF.mel)

Available subpackages
---------------------
audiofile
timefreq
signal
utils


Dependencies
-----------------------------------
This package builds upon freely available Python libraries at various
stages of maturity:

- NumPy: Numerical Computing in Python
- SciPy: Scientific Computing in Python

Additionally, this library takes advantage of SoX, a command
line utility for non-wave file support and audio file conversion.
If you do not currently have SoX, it can be obtained here:
    
    http://sox.sourceforge.net
    
SoX functionality is currently supported under Unix-like OS's only,
(sorry, Windows). However, extending this library should be straightforward
if necessary. Note that SoX is required only for file conversions and
non-wave file formats, so - while strongly encouraged - SoX is not
truly mandatory."""

import os
import logging
import tempfile as tmp
import glob

eps = 2.0**(-16.0)

__version__ = '0.3.9'
__tempprefix = 'marlib-'

_kWAVE_EXT = 'wav'

# Check for a pre-existing temp directory
tempdirs = glob.glob(os.path.join(tmp.gettempdir(),__tempprefix+'*'))
if len(tempdirs):
    _tempdir = tempdirs[0]
else:
    _tempdir = tmp.mkdtemp(prefix=__tempprefix)


#print('Temporary files will be created at %s'%_tempdir)

# Test for numpy
try:
    import numpy as np
except(ImportError):
    print """MARLib depends on NumPy to function properly.
    
    If you don't have NumPy, proceed here:
     - - - http://numpy.scipy.org/ - - -
     
    If you do (should) have NumPy, double-check your
    path variables."""
    raise ImportError("No module named numpy")

class Hell(BaseException):
    pass

def _sox_check():
    """
    Test for sox functionality
    """
    
    SOX = True
    if len(os.popen('sox -h').readlines())==0:
        logging.warning("""
        SoX could not be found!
        As a result, only wave files are supported.
        
        If you don't have SoX, proceed here:
         - - - http://sox.sourceforge.net/ - - -
         
        If you do (should) have SoX, double-check your
        path variables.""")
        SOX = False
    return SOX

_sox_check()
