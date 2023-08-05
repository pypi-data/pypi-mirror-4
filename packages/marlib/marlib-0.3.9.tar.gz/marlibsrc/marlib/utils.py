# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#    utils.py
#    MARLib - Copyright MARL@NYU 2012
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#
#    License information
#    -------------------
#    
#    Copyright (c) 2010-2012 MARL@NYU.
#    All rights reserved.
#    
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions are met:
#    
#      a. Redistributions of source code must retain the above copyright notice,
#         this list of conditions and the following disclaimer.
#      b. Redistributions in binary form must reproduce the above copyright
#         notice, this list of conditions and the following disclaimer in the
#         documentation and/or other materials provided with the distribution.
#      c. Neither the name of MARL, NYU nor the names of its contributors
#         may be used to endorse or promote products derived from this software
#         without specific prior written permission.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#    ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR
#    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#    DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
#    OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
#    DAMAGE.
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

import numpy as np
import subprocess
import wave
import os
import tempfile as tmp
from marlib import _tempdir, _kWAVE_EXT

def temp_wavfile():
    """
    Returns
    -------
    tmpfile : string    
        A writeable wavefile path.
    """
    
    return tmp.mktemp(suffix='.'+_kWAVE_EXT,dir=_tempdir)

def trim(fin, fout, tstart, tstop, VERBOSE = False):
    """
    Excerpt a clip from a sound file, given a set of time points.
    
    Parameters
    ----------
    fin : str
        sound file to excerpt
    
    fout : str
        file to save output as
    
    tstart : float
        clip start time in fin
    
    tstop : float
        clip stop time in fin
        
    VERBOSE : boolean (opt)
        toggle console printing
    
    
    Returns
    -------
    None
    """
    sox_list = ['sox', fin, fout, 'trim',
                '%0.3f'%tstart,'%0.3f' % (tstop - tstart)]
    try:
        if VERBOSE:
            print("Executing: " + " ".join(sox_list))
        p = subprocess.Popen(sox_list)
        sts = p.wait()
        if VERBOSE:
            print sts    
    except OSError, e:
        print('SoX execution failed: %s'%e)
    

def convert(filename, fout=None, samplerate=None, channels=None, bitdepth=None):
    """
    Convert a given file to a temporary wave object.
    
    Parameters
    ----------
    filename : str
        file to convert
        
    fout : str (optional)
        filename to use... if none is provided, a timestamped
        temp name is created. Note: whatever this filename ends up
        being, it is saved as a object member obj._abspath
    
    samplerate : float (optional)
    channels : int (optional)
    bitdepth : int (optional)
    
    
    Returns
    -------
    wavefile : wave object
        note that this object is already opened
    
    """
    
    sox_list = ['sox','--no-dither',filename]
    
    if samplerate:
        sox_list += ['-r %f'%samplerate]
    if bitdepth:
        sox_list += ['-b %d'%bitdepth]
    if channels :
        sox_list += ['-c %d'%channels]
    if fout is None:
        fout = temp_wavfile()
        
    sox_list += [fout]
    
    try:
        p = subprocess.Popen(sox_list)
        sts = p.wait()
        wavefile = wave.open(fout, 'r')
    except OSError, e:
        print('SoX failed! %s'%e)
    except TypeError, e:
        print("Error executing: %s"%" ".join(sox_list))
        raise TypeError(e)
    
    wavefile._abspath = fout
    return wavefile


def is_valid_sox_format(ext, VERBOSE=False):
    """
    Check to see if SoX supports a given file extension.
    
    Parameters
    ----------
    ext : str
        audio file extension to verify
        
    VERBOSE : boolean (opt)
        toggle console printing
    
    
    Returns
    -------
    valid : boolean
        format compatibility
    """
    
    valid = False
    msg = os.popen('sox -h').readlines()
    for m in msg:
        if m.count('AUDIO FILE FORMATS')>0:
            valid = ext in m
            if VERBOSE:
                print m
    
    return valid


def is_valid_format(filename, VERBOSE=False):
    """
    Check to see if a given file type is supported.
    
    Parameters
    ----------
    filename : str
        audio file to verify for support
        
    VERBOSE : boolean (opt)
        toggle console printing
    
    
    Returns
    -------
    valid : boolean
        compatibility flag
    """
    
    fext = os.path.splitext(filename)[-1][1:]
    
    # Pure wave support
    if fext == 'wav':
        return True
    
    # Otherwise, SoX?
    else:
        valid = is_valid_sox_format(ext=fext, VERBOSE=VERBOSE) 
        if VERBOSE and not valid:
            print("Sorry, SoX currently doesn't support conversion to / from '%s' files." % fext)
        return valid


def tri_flat(array, UPPER=True):
    """
    Flattens the upper/lower triangle of a square matrix.
    
    Parameters
    ----------
    array : np.ndarray
        square matrix
        
    UPPER : boolean
        Upper or lower triangle to flatten (defaults to upper). If
        the matrix is symmetric, this parameter is unnecessary.
    
    Returns
    -------
    array : np.ndarray
        vector representation of the upper / lower triangle
    """
    
    C = array.shape[0]
    if UPPER:
        mask = np.asarray(np.invert(np.tri(C,C,dtype=bool)),dtype=float)
    else:
        mask = np.asarray(np.invert(np.tri(C,C,dtype=bool).transpose()),dtype=float)
        
    x,y = mask.nonzero()
    return array[x,y]

def sox_call(sox_list, VERBOSE=False):
    try:
        if VERBOSE:
            print("Executing: " + " ".join(sox_list))
        p = subprocess.Popen(sox_list)
        sts = p.wait()
        if VERBOSE:
            print sts    
    except OSError, e:
        print('SoX execution failed: %s'%e)