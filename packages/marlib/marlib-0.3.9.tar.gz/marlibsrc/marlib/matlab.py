# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#    matlab.py
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
import matplotlib.pyplot as plt
import marlib.audiofile as AF
from marlib import eps


def imshow(x):
    """
    Simple MATLab-like wrapper around Matplotlib's image plotting 
    functionality.
    
    """
    
    fig = plt.figure()
    ax = fig.gca()
    ax.imshow(x.transpose(),interpolation='nearest',aspect='auto')
    plt.show()
    
wavread = AF.wavread
wavwrtie = AF.wavwrite


def shingle(x,N,hopsize):
    """
    Shingle (or alternatively, buffer), a signal with a given 
    length and hopsize.
    
    Parameters
    ----------
    x : array_like
        Signal to buffer.
    
    N : int
        length of shingle
    
    hopsize : float
        stride between shingled vectors
    
    Returns
    -------
    X : np.ndarray
        buffered signal with shape (M,N,C), where M is the number
        of shingles, N is the length provided to the function, and C
        is the second dimenion of x. If x.ndim=1, X is a 2d matrix.
    
    """
    M = int(np.ceil(x.shape[0] / float(hopsize)))
    X = np.zeros([M,N] + list(x.shape[1:]),dtype=x.dtype)
    for m in range(M):
        idx = int(np.round(hopsize*m))
        x_m = x[idx:idx+N]
        X[m,:x_m.shape[0]] = x_m
    
    return X

def spectrogram(x,framesize,hopsize,window=None,nfft=None):
    """
    Parameters
    ----------
    x : array_like
        N-length signal; if multichannel, averages to a single channel 
    
    framesize : int
        length of short-time observations of x; if nfft is None,
        this will also be the length of the FFT
        
    hopsize : int
        number of samples to advance each frame
    
    window : [vector, None]
        optional window to shape each frame. If not None, must
        be the same length as framesize
    
    nfft : [int, None]
        length of the FFT; must be greater-than or equal to framesize
    
    Returns
    -------
    X : np.ndarray
        log-magnitude spectra of the input signal, x, in dB
    """
    x = np.asarray(x)
    
    # Input Dim Check
    if x.ndim==2:
        x = x.mean(axis=1)
    
    # Window Sanity Check
    if window is None:
        window = np.ones(framesize)
    elif window.shape[0] != framesize:
        raise ValueError("Window length must equal %d (nfft)."%nfft)
    
    # NFFT check
    if not nfft is None:
        if nfft < framesize:
            raise ValueError("nfft must be >= framesize")
    
    X = [np.fft.rfft(window*x_m,nfft) for x_m in shingle(x,framesize,hopsize)]
    return 20.0*np.log10(np.abs(np.asarray(X)) + eps) 
    
def loadmat(fin):
    """
    Convenience wrapper around scipy's loadmat function.
    
    fin : string
        matfile to load
    """
    return scipy.matlab.loadmat(fin)

def flatmat(X):
    """
    reduce a tensor to a matrix, such that the first
    dimension is preserved and all others are collapsed.
    """
    assert X.ndim>=2
    shp = X.shape
    return X.reshape(shp[0], np.prod(shp[1:]))