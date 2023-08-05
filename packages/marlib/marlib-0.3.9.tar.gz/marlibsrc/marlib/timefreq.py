# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#	 timefreq.py
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
import marlib.audiofile as AF
from marlib import eps

import logging
from scipy.signal import lfilter
from scipy.stats import beta
from numpy.fft.fftpack import rfft
from numpy.core.numeric import isscalar
from marlib.signal import hwr, princarg, max_peak_pick
from marlib.core import FrameBuffer
from scipy.signal.windows import gaussian

kMFCC_MIN_VAL = -5.0

# --- Convenience Methods ---
def update_buffered_params(default_params, **kwargs):
    """
    Expect errors here ... haven't made this bullet-proof yet because
    there simply isn't time right now. Just don't use it wrong.
    
    default_params : dict
        dictionary to modify in-place
    """
    
    default_params.update(kwargs)
    if not (default_params.get('framerate') is None) and not (default_params.get('samplerate') is None):
        default_params['hopsize'] = default_params['sample_rate'] / float(default_params.get('framerate'))
    elif not (default_params.get('overlap') is None) and (not default_params.get('framesize') is None):
        default_params['hopsize'] = default_params.get('framerate')*(1.0 - default_params.get('overlap'))
    



# --- Module params ---
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
_Mel_fmin = 20.
_Mel_fmax = 11025.

kDIV_BY_ZERO_THRESH = np.power(2.0,-6.0)

# --- Functions ---
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def hz_to_midi(x, QUANTIZE = True):
    """
    Convert frequency to midi note number
    
    Parameters
    ----------
    x : array-like
        frequency value(s)
    QUANTIZE : boolean=True
        round midi note values to integers
    
    Returns
    -------
    notes : np.ndarray / scalar
        midi note value(s)
    """
    
    n = 12 * np.log2(x / 440. + eps) + 57
    if QUANTIZE:
        n = np.round(n)
    return n

def midi_to_hz(n, QUANTIZE = False):
    """
    Convert midi note number to frequency, in Hertz
    
    Parameters
    ----------
    n : array-like
        midi note value(s)
    QUANTIZE : boolean (default False)
        round midi note values to integers first
        
    Returns
    -------
    freqs : np.ndarray / scalar
        frequency value(s)
    """
    if QUANTIZE:
        n = np.round(n)
    return 440.0 * np.power(2.0, (n - 57.0) / 12.0)

def hz_to_mel(f):
    """
    frequency, in Hertz, to mel scale
    
    Parameters
    ----------
    freq : scalar, array_like
        frequency in Hertz
    
    Returns
    -------
    phi : same as input
        frequency in melscale
    
    """
    return 2595.0 * np.log10(f / 700.0 + 1.0)  

def mel_to_hz(phi):
    """
    mel scale to Hertz
    
    Parameters
    ----------
    phi : scalar, array_like
        frequency in melscale
    
    Returns
    -------
    freq : same as input
        frequency in Hertz
    
    """
    if not isscalar(phi):
        phi = np.asarray(phi)
    
    return 700.0 * (np.power(10.0, phi / 2595.0) - 1.0)
     

def gammafreq(bins):
    """
    gammatone channel center freq
    currently based on 70 channels
    
    Parameters
    ----------
    bins : scalar, array_like
        Band number to computer center freq
    
    Returns
    -------
    freq : same as input
        center frequency
    
    """
    if not isscalar(bins):
        bins = np.asarray(bins)
    
    xi0 = 2.3
    xi1 = 0.39
    return 229.0 * (np.power(10.0, (xi1 * bins + xi0) / 21.4) - 1.0)

def reson_params(fc, fs, sections):
    """
    Parameters
    ----------
    fc : float
        center frequency
    fs : float
        sampling frequency
    sections : int
        number of sections in the filter
    
    Returns
    -------
    A : float
        gain parameter
    rho_1 : float
        1st order pole coeff
    rho_2 : float
        2nd order pole coeff
    theta_1 : float
        1st order zero coeff
    theta_2 : float 
        2nd order zero coeff
    
    """
    nu = 4.0
    J = sections
    fs = float(fs)
    B = 1.019 * (0.108 * fc + 24.7)
    wc = 2 * np.pi * fc / fs
    
    num = 2 * np.pi * B * np.sqrt(np.power(2.0, 1.0 / nu) - 1.0)
    den = fs * np.sqrt(np.power(2.0, 1.0 / J) - 1.0)
    A = np.exp(-num / den)
    
    theta_1 = np.arccos((1.0 + A ** 2) / (2.0 * A) * np.cos(wc))
    theta_2 = np.arccos((2.0 * A) / (1.0 + A ** 2) * np.cos(wc))
    
    rho_1 = 0.5 * (1.0 - A ** 2)
    rho_2 = (1.0 - A ** 2) * np.sqrt(1.0 - np.cos(theta_2) ** 2)
    return A, rho_1, rho_2, theta_1, theta_2

def df_auditory_bank(filters, samplerate):
    """
    Parameters
    ----------
    filters : list
        center frequencies of a gammatone bank
    samplerate : float
        samplerate of the analysis
    
    Returns
    -------
    b : list
        packed list of b coefficients for Digital Filter class
    a : list
        packed list of a coefficients for Digital Filter class
    """
    b = []
    a = []
    sections = 4
    f_c = gammafreq(np.arange(filters))
    for f in f_c:
        A, p_1, p_2, o_1, o_2 = reson_params(fc=f, fs=samplerate, sections=sections)
        H1_b = np.array([1.0, 0.0, -1.0])
        H1_a = np.array([1.0, -2.0 * A * np.cos(o_1), A ** 2])
        H2_b = np.array([1.0])
        H2_a = np.array([1.0, -2.0 * A * np.cos(o_2), A ** 2])
        b.append([H2_b, H1_b, H1_b, H2_b * (p_1 ** 2) * (p_2 ** 2)])
        a.append([H2_a, H1_a, H1_a, H2_a])
    
    return b, a
    
def mel_warp(frame, w_n, melfb):
    """
    Parameters
    ----------
    frame : array_like
    
    w_n : array_like
    
    melfb : np.ndarray
    
    Returns
    -------
    X : np.ndarray
    
    """
    assert frame.shape == w_n.shape
    assert melfb.shape[1] == frame.shape[0] / 2 + 1
    X = np.abs(rfft(frame * w_n, axis=0))
    return np.dot(melfb, np.abs(X))

def cq_warp(frame, w_n, complexfb):
    """
    Parameters
    ----------
    frame : array_like
    
    w_n : array_like
    
    complexfb : np.ndarray
    
    Returns
    -------
    X : np.ndarray
    """
    assert frame.shape == w_n.shape
    assert complexfb.shape[1] == (frame.shape[0] / 2 + 1)
    X = rfft(frame * w_n, axis=0)
    return np.log10(1.0 + 100.0*np.abs(np.dot(complexfb, X)))

def fb_warp(frame, w_n, fb):
    """
    Parameters
    ----------
    frame : array_like
    
    w_n : array_like
    
    melfb : np.ndarray
    
    Returns
    -------
    X : np.ndarray
    """
    assert frame.shape == w_n.shape
    assert fb.shape[1] == frame.shape[0] / 2 + 1
    return abs(np.dot(fb, rfft(frame * w_n)))

# --- Filterbanks ---
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def cqfb(samplerate, nfft, fmin=None, fmax=None, bpo=12, scale=1.0, NORMALIZE=False):
    """
    Create a Filterbank matrix to combine FFT bins to form the constant Q
    transform.
    
    Based on B. Blankertz, "The Constant Q Transform"
    http://ida.first.fhg.de/publications/drafts/Bla_constQ.pdf
    Refactored from routines implemented by Ron Weiss.
    
    Parameters
    ------
    samplerate : int
        Sampling rate of the incoming signal.
    nfft : int
        FFT length to use.
    fmin : float (default = lowest given the parameters)
        Frequency in Hz of the lowest edge of the constant-Q bands
    fmax : float (default = samplerate / 2)
        Frequency in Hz of the upper edge of the constant-Q bands
    bpo : int (default = 12)
        Number of bins per octave.
    scale : float
        Value to scale the relative energies of each filter
    NORMALIZE : bool
        max-scale each filter to unity
    
    Returns
    -------
    weight_matrix : 2-D nd.array
        M x (nfft/2 + 1) matrix of constant-Q coefficients
        
    """
    Q = 1. / (2. ** (1. / bpo) - 1)
    # Compute minimum fmin from nfft.
    if fmin is None or (fmin < (Q * samplerate / nfft)):
        fmin = Q * samplerate / nfft
        logging.warning('fmin too small for nfft, increasing to %.2f' % fmin)
    
    if fmax is None:
        fmax = samplerate / 2.

    K = np.ceil(bpo * np.log2(float(fmax) / fmin))
    tempkernel = np.zeros(nfft, dtype = complex)
    kernel = np.zeros((K, nfft / 2 + 1), dtype = np.complex)
    for k in np.arange(K - 1, -1, -1, dtype = np.float):
        ilen = np.ceil(Q * samplerate / (fmin * 2.0 ** (k / bpo)))
        if((ilen % 2) == 0):
            # calculate offsets so that kernels are centered in the
            # nfft'th windows
            start = nfft / 2 - ilen / 2
        else:
            start = nfft / 2 - (ilen + 1) / 2        
        
        tempkernel = np.zeros(nfft, dtype = complex)
        tempkernel[start:start + ilen] = (np.hamming(ilen) / ilen * np.exp(2 * np.pi * 1j * Q * np.r_[:ilen] / ilen))
        temp = np.fft.rfft(tempkernel)
        kernel[k] = np.power(np.abs(temp),scale)*np.exp(1j*np.angle(temp))
        
    if NORMALIZE:
        maxval = -float('inf')
        for k in kernel:
            if np.abs(k).max()>maxval:
                maxval = np.abs(k).max()
            
        kernel = (np.abs(kernel) / maxval)*np.exp(1j*np.angle(kernel))
        
    return kernel,fmin

def cqfb2(samplerate, nfft, fmin=55.0, fmax=None, bpo=12, scale=1.0, NORMALIZE=False):
    """
    Create a Filterbank matrix to combine FFT bins to form the constant Q
    transform by taking the FFT of a complex-valued impulse response.
    
    Parameters
    ------
    samplerate : float
        Sampling rate of the incoming signal.
    nfft : int
        FFT length to use.
    fmin : float (default = lowest freq, given the parameters)
        Frequency in Hz of the lowest edge of the constant-Q bands
    fmax : float (default = samplerate / 2)
        Frequency in Hz of the upper edge of the constant-Q bands
    bpo : int (default = 12)
        Number of bins per octave.
    scale : float=1.0
        Value to scale the relative energies of each filter
    NORMALIZE : bool
        max-scale each filter to unity
    
    Returns
    -------
    weight_matrix : 2-D nd.array
        M x (nfft/2 + 1) matrix of constant-Q coefficients
    fmin : scalar
        actual fmin
    """
    oct_low = np.log2(fmin/440.0)
    if fmax is None:
        fmax = samplerate/2.0
        
    oct_high = np.log2(fmax/440.0)
    num_steps = int((oct_high-oct_low)*bpo + 0.5)+1
    f_basis = np.logspace(start=oct_low,
                          stop=oct_high,
                          num=num_steps,
                          base=2)*440.0
    kernel = np.asarray([np.exp(2j*np.pi*f/samplerate*np.arange(nfft)) for f in f_basis],
                        dtype=np.complex)
    return np.fft.fft(np.hamming(nfft)[np.newaxis,:]*kernel,axis=1)[:,:nfft/2+1],fmin
    

# Mel Filterbank
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def melfb(samplerate, nfft, nfilts=40, width=1.0, fmin=0, fmax=None, norm_type=1):
    """Create a Filterbank matrix to combine FFT bins into Mel-frequency bins.
    Refactored from routines implemented by Ron Weiss.
    
    Parameters
    ------
    samplerate : int
        Sampling rate of the incoming signal.
    nfft : int
        FFT length to use.
    nfilts : int
        Number of MFCC coefficients to keep
    width : float
        The constant width of each band relative to standard Mel. Defaults 1.0.
    fmin : float
        Frequency in Hz of the lowest edge of the Mel bands. Defaults to 0.
    fmax : float
        Frequency in Hz of the upper edge of the Mel bands. Defaults
        to `samplerate` / 2.
    norm_type : int, [1,2]
        normal (1) or energy-scaled (2)
    
    Returns
    -------
    wts : np.ndarray
        filterbank coefficients
    """
    valid_types = [1,2]
    if not norm_type in valid_types:
        raise IOError("Provided 'norm_type' %s must be one of %s"%(norm_type, valid_types))
    
    if fmax is None:
        fmax = samplerate / 2

    wts = np.zeros((nfilts, nfft / 2 + 1))
    # Center freqs of each FFT bin
    fftfreqs = np.arange(nfft / 2 + 1, dtype=np.double) / nfft * samplerate

    # 'Center freqs' of mel bands - uniformly spaced between limits
    minmel = hz_to_mel(fmin)
    maxmel = hz_to_mel(fmax)
    binfreqs = mel_to_hz(minmel
                          + np.arange((nfilts+2), dtype=np.double) / (nfilts+1)
                          * (maxmel - minmel))

    for i in xrange(nfilts):
        freqs = binfreqs[i + np.arange(3)]
        # scale by width
        freqs = freqs[1] + width * (freqs - freqs[1])
        # lower and upper slopes for all bins
        loslope = (fftfreqs - freqs[0]) / (freqs[1] - freqs[0])
        hislope = (freqs[2] - fftfreqs) / (freqs[2] - freqs[1])
        # .. then intersect them with each other and zero
        wts[i,:] = np.maximum(0, np.minimum(loslope, hislope))

    # Slaney-style mel is scaled to be approx constant E per channel
    if norm_type==2:
        enorm = 2.0 / (binfreqs[2:nfilts+2] - binfreqs[:nfilts])
        wts = np.dot(np.diag(enorm), wts)
    
    return wts

def dctfb(ndct, nrow):
    """Create a DCT (type 3) matrix.

    Parameters
    ----------
    ndct : int
        Number of DCT components.
    nrow : int
        Number of rows.
        
    coeffs : np.ndarray
        
    """
    coeffs = np.asarray([(np.cos(i*np.arange(1, 2*nrow, 2) / (2.0*nrow) * np.pi) * np.sqrt(2.0 / nrow)) for i in range(ndct)])
    coeffs[0] /= np.sqrt(2)
    return coeffs


# Gammatone Filterbank
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def gammafb(samplerate, nfft, M, downsample = 2):
    """
    Generate a gammatone coefficient matrix for the given
        parameters.

    Parameters
    ----------
    samplerate : int
        blah
    nfft: int
        blah 
    M: int
        blah
    
    Returns
    -------
    coeffs : 2-dim nd.array
       M x (nfft/2 + 1) matrix of gammatone coefficients 
        
    """
    
    coeffs = df_auditory_bank(M, samplerate)
    g_c = nfft / 2 / downsample + 1
    fbank = np.zeros([M, nfft / 2 + 1], dtype = complex)
    for b, a, m in zip(coeffs[0], coeffs[1], range(M)):
        x = DigitalFilter(b, a)
        y = x.filter(np.concatenate([np.ones(1), np.zeros(nfft - 1)]))
        fbank[m] = np.fft.rfft(y)
        
    fbank[:, g_c:] = 0.0
    return fbank




# Cosine Masks
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def cos_bank_freq(samplerate, nfft, note_range = [24, 108], beta_params = [1.25, 3]):
    """
    Parameters
    ----------
    samplerate : 
    
    nfft : 
    
    note_range : 
    
    beta_params : 
    
    Returns
    -------
    
    """
    npoints = nfft / 4 + 1
    T = 440.0 * np.power(2.0, (np.arange(note_range[0], note_range[1]) - 69) / 12.0) * nfft / float(samplerate)
    n = np.arange(npoints).reshape(1, npoints)
    C = np.cos(2 * np.pi * n / T.reshape(len(T), 1))
    rv = beta(beta_params[0], beta_params[1])
    # This isn't ideal... the alpha / beta should change as a function of T
    n = np.linspace(0, np.minimum(rv.dist.b, 3), npoints)
    for n in xrange(len(T)):
        C[n][:int(T[n] / 4) + 1] = 0.0
    return C

def cos_bank_time(samplerate, npoints, note_range = [24, 108], note_step = 1, beta_params = [1.25, 3]):
    """
    Parameters
    ------
    
    Returns
    -------
    """
    T = float(samplerate) / (440.0 * np.power(2.0, (np.arange(note_range[0], note_range[1], note_step) - 69) / 12.0)) 
    n = np.arange(npoints).reshape(1, npoints)
    C = np.cos(2 * np.pi * n / T.reshape(len(T), 1))
    rv = beta(beta_params[0], beta_params[1])
    # This isn't ideal... the alpha / beta should change as a function of T
    n = np.linspace(0, np.minimum(rv.dist.b, 3), npoints)
    for n in xrange(len(T)):
        C[n][:int(T[n] / 4) + 1] = 0.0
    return C


# --- Harmonic Functions --- 
def chroma(cqspec, bpo, fmin, tune_type=1, scale='l1'):
    """
    Parameters
    ------
    cqspec : np.ndarray
        constant-Q spectra, of either shape (pitch,) or (time, pitch)
    bpo : int
        number of bins per octave
    fmin : float
        frequency of the lowest CQ coefficient
    type : int
        toggle different tuning methods, only 1=decimation is 
        currently supported
    scale : string
        one of ['l1','l2','max']
    
    Returns
    -------
    c : np.ndarray
        chroma coefficients of the same rank as cqspec
    """
    if cqspec.ndim==1:
        cqspec = cqspec[np.newaxis,:]
        
    N = cqspec.shape[0]
    P = cqspec.shape[1]
    c = np.zeros([N,12])
    b = bpo / 12
    
    if b > 1:
        cqredux = np.zeros([N,P/b])
        for p in range(P/b):
            if tune_type==1:
                cqredux[:,p] = cqspec[:,p*b]
            else:
                NotImplementedError("Other types currently unsupported.")
        
        cqspec = cqredux

    for k in range(12):
        c[:,k] = np.mean(cqspec[:,k::12],axis=1)
    
    # Rotate to C=0
    nn_min = hz_to_midi(fmin, QUANTIZE=True)
    idx_out = (((nn_min)%12 + np.arange(12))%12).astype(int)
    c2 = np.zeros(c.shape)
    c2[:,idx_out] = c
    c = c2
    # Scale types
    if scale == 'l1':
        s = c.sum(axis=1)
    elif scale == 'l2':
        s = np.power(c,2.0).sum(axis=1)
    elif scale == 'max':
        s = c.max(axis=1)
    
    s = s[:,np.newaxis]
    s[s<kDIV_BY_ZERO_THRESH] = 1.0
    return c / s
    
def tonnetz(c):
    """
    Chroma to Tonnetz - Cartesian
    
    Translates an Nx12 chroma vector to a Nx6 Cartesian
      representation of the Tonnetz, as [x1,y1,x2,y2,x3,y3]
    
    Parameters
    ------
    c : np.ndarray
        chroma, of either shape (pitch class,) or (time, pitch class)
    
    Returns
    -------
    t : np.ndarray
        tonnetz coefficients of the same rank as c
      
    """
    c = np.asarray(c)
    FLATTEN = False
    if c.ndim==1:
        c = c[np.newaxis,:]
        FLATTEN = True
    
    if c.shape[1]==12:
        c = c.transpose()
    
    r = np.array([1.0, 1.0, 0.5])[:,np.newaxis]
    t = np.array([7*np.pi/6.0, 3*np.pi/2.0, 2*np.pi/3.0])[:,np.newaxis]
    l = np.arange(12)[np.newaxis,:]
    phi = np.zeros([6,12])
    phi[::2] = r*np.sin(l*t)
    phi[1::2] = r*np.cos(l*t)
    
    tn = np.dot(phi,c)
    scale = c.sum(axis=0)[:,np.newaxis]
    scale[scale==0] = 1.0
    tn = tn.T / scale
    if FLATTEN:
        tn = tn.flatten()
    
    return tn 

def tonnetz_complex(c):
    """
    Chroma to Tonnetz - Complex Cartesian
    
    Translates an Nx12 chroma vector to a Nx3 complex-valued
      representation of the Tonnetz, as [x1+jy1,x2+jy2,x3+jy3]
       
    Parameters
    ----------
    c : np.ndarray
        chroma, of either shape (pitch class,) or (time, pitch class)
    
    Returns
    -------
    t : np.ndarray
        tonnetz coefficients of the same rank as c
      
    """
    c = np.asarray(c)
    FLATTEN = False
    if c.ndim==1:
        c = c[np.newaxis,:]
        FLATTEN = True
    
    if c.shape[1]==12:
        c = c.transpose()
    
    r = np.array([1.0, 1.0, 0.5])[:,np.newaxis]
    t = np.array([7*np.pi/6.0, 3*np.pi/2.0, 2*np.pi/3.0])[:,np.newaxis]
    l = np.arange(12)[np.newaxis,:]
    phi = r*np.exp(1j*l*t)
    
    tn = np.dot(phi,c)
    scalar = c.sum(axis=0)[:,np.newaxis]
    scalar[scalar==0] = 1.0
    tn = tn.T / scalar
    if FLATTEN:
        tn = tn.flatten()
    
    return tn 

def difftonnetz(c):
    """
    Chroma to Displacement Tonnetz - Cartesian
    
    Translates an Nx12 chroma vector to a Nx6 Cartesian
      representation of the Displacement Tonnetz,
      as [dx1,dy1,dx2,dy2,dx3,dy3]
           
    Parameters
    ----------
    c : np.ndarray
        chroma, of either shape (pitch class,) or (time, pitch class)
    
    Returns
    -------
    dt : np.ndarray
        differential tonnetz coefficients of the same rank as c
       
    """
    tn = tonnetz(c)
    if tn.ndim!=2:
        raise AssertionError("Input array must have at least two rows.")
    N = tn.shape[0]
    
    dtheta = np.diff(np.angle(tn),axis=0) + 2*np.pi*(np.diff(np.angle(tn),axis=0)<0)
    dmag = np.abs(np.diff(tn,axis=0))
    
    dt = np.zeros([N-1,6])
    dt[:,::2] = (dmag*np.exp(1j*dtheta)).real
    dt[:,1::2] = (dmag*np.exp(1j*dtheta)).imag
    return dt


class CQSpectra(AF.AudioReader):
    """
    """
    def __init__(self, filename, **kwargs):
        self.params = {'framesize':16384,
                       'overlap':0.5,
                       'samplerate':44100,
                       'channels':1,
                       'freq_min':27.5,
                       'freq_max':4186.1,
                       'bins_per_octave':12,
                       'framemode':'center',
                       'std_scale':True,
                       'VERBOSE':False}
        
        self.update_params(**kwargs)
        AF.AudioReader.__init__(self, filename = filename, **self.params)
        
#        self._cq_matrix,fmin = cqfb(samplerate=self.samplerate(),
#                                     nfft=self.framesize(),
#                                     fmin=self.params.get('freq_min'),
#                                     fmax=self.params.get('freq_max'),
#                                     bpo=self.params.get('bins_per_octave'))
        
        self._cq_matrix, fmin = cqfb2(samplerate=self.samplerate(),
                                     nfft=self.framesize(),
                                     fmin=self.params.get('freq_min'),
                                     fmax=self.params.get('freq_max'),
                                     bpo=self.params.get('bins_per_octave'))
        
        self.update_params(freq_min=fmin)        
        self._features = None
        return

    def cqspectra(self):
        """
        Compute the constant-Q spectra over a audio file.
        
        Returns
        -------
        cqspec : np.ndarray
            magnitude constant-Q spectra
        """
        framelist = []
        while self.update_framebuffer():
            pitch = cq_warp(frame=self.framebuffer.mean(axis=-1)[:,np.newaxis],
                            w_n=self.window,
                            complexfb=self._cq_matrix)
            if self.params.get('std_scale'):
                s = pitch.std(axis=0)[np.newaxis,:]
                s[s==0]=1.0
                pitch = hwr(pitch-pitch.mean(axis=0)[np.newaxis,:])/s
            framelist.append(pitch.squeeze())
            
        self.reset()
        return np.asarray(framelist)
    
    def features(self):
        """
        Returns
        -------
        X : np.ndarray
            time-feature vector of this model.
        """
        if self._features is None:
            self._features = self.cqspectra()
        return self._features
    

class MelSpectra(AF.AudioReader):
    """
    """
    def __init__(self, filename, **kwargs):
        self.params = {'framesize':8192,
                       'overlap':0.5,
                       'samplerate':44100,
                       'channels':1,
                       'framemode':'center',
                       'freq_min':41.0,
                       'freq_max':3520.0,
                       'nfilts':40,
                       'type':1,
                       'width':1.0,
                       'VERBOSE':False}
        
        self.update_params(**kwargs)
        AF.AudioReader.__init__(self, filename = filename, **self.params)
        
        self._melfb = melfb(samplerate=self.samplerate(),
                          nfft=self.framesize(),
                          nfilts=self.params.get('nfilts'),
                          fmin=self.params.get('freq_min'),
                          fmax=self.params.get('freq_max'),
                          width=self.params.get('width'),
                          norm_type=self.params.get('type'))
        self._features = None
        return

    def melspectra(self):
        """
        Compute the mel spectra over a audio file.
        
        Returns
        -------
        melspec : np.ndarray
            magnitude constant-Q spectra
        """
        framelist = []
        while self.update_framebuffer():
            melspec = mel_warp(frame=self.framebuffer.mean(axis=-1)[:,np.newaxis],
                            w_n=self.window,
                            melfb=self._melfb)
            framelist.append(melspec.squeeze())
            
        self.reset()
        return np.asarray(framelist)
    
    def features(self):
        """
        Returns
        -------
        X : np.ndarray
            time-feature vector of this model.
        """
        if self._features is None:
            self._features = self.melspectra()
        return self._features
    
class MFCC(MelSpectra):
    """
    """
    def __init__(self, filename, **kwargs):
        self.params = {'VERBOSE':False,
                       'ndct':13}
        self.update_params(**kwargs)
        MelSpectra.__init__(self, filename = filename, **self.params)
        self.dct = dctfb(self.params['ndct'], self.params['nfilts'])
        
        return
    
    def features(self):
        """
        Returns
        -------
        X : np.ndarray
            time-feature vector of this model.
        """
        if self._features is None:
            X = np.maximum(np.log(self.melspectra()), kMFCC_MIN_VAL)
            self._features = np.dot(self.dct,X.T).T
        return self._features

class Chroma(CQSpectra):
    """
    """
    def __init__(self, filename, **kwargs):
        self.params = {"VERBOSE":False,
                       'scale':'l1'}
        self.update_params(**kwargs)
        CQSpectra.__init__(self, filename, **self.params)
        self._chroma = None
        
    def chroma(self):
        """
        """
        if not self._chroma is None:
            return self._chroma
        
        self._chroma = chroma(cqspec=self.cqspectra(),
                              bpo=self.params.get('bins_per_octave'),
                              fmin=self.params.get('freq_min'),
                              scale=self.params.get('scale'))
        
        return self._chroma
    
    def features(self):
        """
        Returns
        -------
        X : np.ndarray
            time-feature vector of this model.
        """
        if self._features is None:
            self._features = self.chroma()
        return self._features

class Tonnetz(Chroma):
    """
    """
    def __init__(self, filename, **kwargs):
        self.params = {}
        self.update_params(**kwargs)
        Chroma.__init__(self, filename, **self.params)
        self._tonnetz = None
    
    def tonnetz(self):
        """
        """
        if self._tonnetz is None:
            self._tonnetz = tonnetz(self.chroma())
        return self._tonnetz
    
    def features(self):
        """
        Returns
        -------
        X : np.ndarray
            time-feature vector of this model.
        """
        if self._features is None:
            self._features = self.tonnetz()
        return self._features


# Envelope Extraction
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class Envelope(AF.AudioReader):
    """
        
    
    """
    def __init__(self, filename, **kwargs):
        self.params = {'framesize':2048,
                       'framerate':100.0,
                       'samplerate':44100,
                       'channels':1,
                       'mode':'power',
                       'VERBOSE':False}
        
        self.update_params(**kwargs)
        AF.AudioReader.__init__(self, filename = filename, **self.params)

    def max_envelope(self):
        """
        Return the amplitude envelope of the target file.
        """
        framelist = np.zeros([self.numframes(),self.channels()])
        while self.update_framebuffer():
            framelist[self._read_pointer-1] = self.framebuffer.max(axis=0)
        
        self.reset()
        return framelist
    
    def power_envelope(self):
        """
        Return the amplitude envelope of the target file.
        """
        framelist = np.zeros([self.numframes(),self.channels()])
        while self.update_framebuffer():
            framelist[self._read_pointer-1] = np.sqrt(np.power(self.window*self.framebuffer,2.0).sum(axis=0))
        
        self.reset()
        return framelist
    
    def features(self,mode=None):
        """
        Returns
        -------
        X : np.ndarray
            time-feature vector of this model.
        """
        if mode is None:
            mode = self.params.get('mode')
            
        if mode == 'power':
            return self.power_envelope()
        elif mode == 'max':
            return self.max_envelope()
        else:
            raise ValueError("Mode '%s' unsupported!"%mode)


class CDOnsets(AF.AudioReader):
    """
        
    
    """
    def __init__(self, filename, **kwargs):
        self.params = {'framesize':2048,
                       'framerate':250.0,
                       'samplerate':44100,
                       'channels':1,
                       'VERBOSE':False}
        
        self.update_params(**kwargs)
        AF.AudioReader.__init__(self, filename = filename, **self.params)
        self.phi_past = np.zeros([self.channels(),2,self.framesize()/2+1])
        self.X_past = np.zeros([self.channels(),self.framesize()/2+1],dtype=np.complex)
        
    def novelty(self):
        """
        Return the amplitude envelope of the target file.
        """
        framelist = np.zeros([self.numframes(),self.channels()])
        while self.update_framebuffer():
            for c in range(self.channels()):
                X = np.fft.rfft(self.framebuffer[:,c]*self.window.flatten())
                phi_hat = princarg(2*self.phi_past[c,0] - self.phi_past[c,1])
                X_hat = np.abs(self.X_past[c])*np.exp(1j*phi_hat)
                framelist[self._read_pointer-1,c] = 2.0*np.sum(np.abs(X-X_hat))/self.framesize()
                
                # Save state
                self.phi_past[c,:] = np.array([np.angle(X), self.phi_past[c,0]])
                self.X_past[c] = X
                
        self.reset()
        return framelist
    
    def features(self,mode=None):
        """
        Returns
        -------
        X : np.ndarray
            time-feature vector of this model.
        """
        return self.novelty()
    
    
class Onsets(AF.AudioReader):
    """
        
    
    """
    def __init__(self, filename, **kwargs):
        self.params = {'framesize':256,
                       'framerate':250.0,
                       'samplerate':44100,
                       'channels':1,
                       'framemode':'center',
                       'onset_window':0.05,
                       'threshold':0.2,
                       'VERBOSE':False}
        
        self.update_params(**kwargs)
        AF.AudioReader.__init__(self, filename = filename, **self.params)
        fc = 20.0

        L = int(np.round(0.1*self.framerate()))
        t = np.arange(-L/2,L/2+1) / self.framerate()
        k = np.exp(-2j*np.pi*fc*t)
        g = gaussian(L+1,(L+1)/8.0)

        self.k_n = k*g
        self.k_n /= float(len(g))
        
        self.bins = [1,4,7,13,24,48,129]
        self.onset_filt = DigitalFilter(b=[self.k_n], rank = len(self.bins)-1)
        self._novelty = None
        self._features = None
    
    def novelty(self):
        if not self._novelty is None:
            return self._novelty
        
        X = np.zeros([self.numframes(),self.framesize()/2+1])
        C = 1000.0
        
        while self.update_framebuffer():
            X_m = np.fft.rfft((self.framebuffer*self.window).squeeze())
            X[self._read_pointer-1,:] = np.log10(1.0 + C*np.abs(X_m))
        
        K = len(self.bins)-1
        Y = np.zeros([X.shape[0],K])
        for i in range(K):
            # Mean
            # Y[:,i] = X[:,self.bins[i]:self.bins[i+1]].mean(axis=1)
            
            # Sum of Squares
            Y[:,i] = np.sqrt((X[:,self.bins[i]:self.bins[i+1]]**2.0).sum(axis=1))
        
        C = self.onset_filt(Y,axis=0, FULL=True)
        nf = np.sqrt((np.imag(C)*np.greater(np.imag(C),0))**2.0).sum(axis=1)
        n_0 = int(len(self.k_n)/2.0+0.5)
        self._novelty = nf[n_0:n_0+self.numframes()]
        return self._novelty
    
    def features(self):
        """
        Returns the onset times of the waveform.
        """
        if not self._features is None:
            return self._features
        L = int(0.5 + self.params.get('onset_window')*self.framerate()/2.0)
        x = self.novelty()
        y = max_peak_pick(x*(x>self.params.get('threshold')),L)
        self._features = y.nonzero()[0] / self.framerate()
        return self._features
        
        


# Online Digital Filter
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class DigitalFilter:
    def __init__(self, b, a = None, rank=None):
        '''
        Online digital filter
        
        Designed for processing arbitrarily long 1D signals, for a
        cascade of type-II digital filters, passed as lists.
        
        Parameters
        ------
        b : list
            numerator (x) coefficient arrays
        a : list (default None, FIR)
            denominator (y) coefficient arrays
        
        if len b != len a, we've got issues
        currently only built to handle 1D vectors
        '''
        
        if a is None:
            a = [np.ones(1)] * len(b)
        
        assert len(b) == len(a)
        
        self._b = b 
        self._a = a
        self._rank = rank
        self._sections = len(b)
        self.reset()
        return
        
    def __call__(self, x, axis = 0, FULL=False):
        """
        Expects (requires) non-overlapping observations of x
        """
        for n in xrange(self._sections):
            x, self._zi[n] = lfilter(b=self._b[n], a=self._a[n], x=x, axis=axis, zi=self._zi[n])
            
        if FULL:
            x = np.concatenate([x,self.delay_line()],axis=0)
        return x
    
    def reset(self):
        self._zi = []
        for b, a in zip(self._b, self._a):
            assert len(b) > 1 or len(a) > 1 
            if self._rank is None:
                self._zi.append(np.zeros(max(len(b), len(a)) - 1))
            else:
                self._zi.append(np.zeros([max(len(b), len(a)) - 1,self._rank]))
        
    def delay_line(self):
        dline = []
        for zi in self._zi:
            dline += list(zi)
        return np.asarray(dline)

    
class PhaseVocode(AF.AudioWriter):
    def __init__(self, filename,
                 framesize = 8192,
                 overlap = 0.875,
                 samplerate = 44100,
                 channels = 1):
        
        print "NB: Probably shouldn't use this just yet."
        
        AF.AudioWriter.__init__(self, filename,
                                framesize,
                                overlap,
                                samplerate,
                                channels)
        
        self.w_S = np.zeros(framesize)
        self.w_A = np.hanning(framesize)
        L_start = int(framesize/2.0 - framesize*(1-overlap))
        L_end = int(framesize*(1-overlap)*2)+L_start
        self.w_S[L_start:L_end] = np.hanning(L_end-L_start)
        self.omega_k = 2.0*np.pi*np.arange(framesize/2+1)/float(framesize)
        
        #Rs = N*O;
        #alpha = Rs/Ra;
        #LRI = -Ra+1;

        self.X_ang_last = np.zeros(framesize/2+1)
        self.Y_ang_last = self.X_ang_last

        
        return
    
    def warp_file(self, f_in, rate):
        overlap = 1-(1-self.overlap())/float(rate)
        
        ar = AF.AudioReader(f_in,framesize=self.framesize(),overlap=overlap)
        
        frame = ar.read_frame()
        while not frame is None:
            new_frame = self.warp_frame(frame, 1.0/float(rate))
            self.write_frame(new_frame)
            frame = ar.read_frame()
        
        self.destroy()
        return
    
    def warp_frame(self, frame, alpha):
        X_k = rfft(self.w_A * frame.flatten())
        Y_mag = np.abs(X_k)
        X_ang = np.angle(X_k)
        
        Rs = self.framesize()*(1 - self.overlap()) 
        Ra = round(Rs/alpha)
        
        dphi = (X_ang - (self.X_ang_last + Ra*self.omega_k)) % (2.0*np.pi)
        dphi = dphi - 2.0*np.pi*np.greater(dphi,np.pi).astype(float)
        w_k = self.omega_k + 1.0/float(Ra)*dphi
        Y_ang = self.Y_ang_last + Rs*w_k
        
        Y_k = Y_mag*np.exp(1j*Y_ang)
        self.X_ang_last = X_ang
        self.Y_ang_last = Y_ang
        y_out = self.w_S*np.fft.irfft(Y_k)
#        y_out = irfft(Y_k)*.5
#        plot(y_out);show()
        return y_out


# --- Procedural Implementations -----------------
def spectrogram(x, **kwargs):
    """
    TODO: Perhaps break out the params into an object, so that
    the methods survive whether the managing object is a proper 
    class or merely a procedural function ...
    
    """
    params = {'framesize':8192,
               'overlap':0.5,
               'framemode':'center',
               'window':None,
               'VERBOSE':False}
    
    params.update(**kwargs)
    buff = FrameBuffer(x, **params)
    
    framelist = []
    while buff.update_framebuffer():
        x_m = buff.framebuffer.mean(axis=-1)[:,np.newaxis]*buff.window
        X = np.fft.rfft(x_m.flatten())
        framelist.append(X.squeeze())
        
    return np.asarray(framelist)

def cqspec(x, **kwargs):
    """
    TODO: Perhaps break out the params into an object, so that
    the methods survive whether the managing object is a proper 
    class or merely a procedural function ...
    
    """
    params = {'framesize':16384,
               'overlap':0.5,
               'samplerate':44100,
               'channels':1,
               'freq_min':27.5,
               'freq_max':4186.1,
               'bins_per_octave':12,
               'framemode':'center',
               'std_scale':True,
               'VERBOSE':False}
        
    params.update(**kwargs)
    buff = FrameBuffer(x, **params)
    
    cq_coeffs, fmin = cqfb2(samplerate=buff.samplerate(),
                         nfft=buff.framesize(),
                         fmin=buff.params.get('freq_min'),
                         fmax=buff.params.get('freq_max'),
                         bpo=buff.params.get('bins_per_octave'))
        
    
    framelist = []
    while buff.update_framebuffer():
        X = cq_warp(frame=buff.framebuffer.mean(axis=-1)[:,np.newaxis],
                        w_n=buff.window,
                        complexfb=cq_coeffs)
        if params.get('std_scale'):
            s = X.std(axis=0)[np.newaxis,:]
            s[s==0]=1.0
            X = hwr(X-X.mean(axis=0)[np.newaxis,:])/s
        
        framelist.append(X.squeeze())
    
    return np.asarray(framelist)

def melspec(x, **kwargs):
    """
    TODO: Perhaps break out the params into an object, so that
    the methods survive whether the managing object is a proper 
    class or merely a procedural function ...
    
    """
    params = {'framesize':8192,
               'overlap':0.5,
               'samplerate':44100,
               'framemode':'center',
               'freq_min':41.0,
               'freq_max':3520.0,
               'nfilts':40,
               'type':1,
               'width':1.0,
               'VERBOSE':False}
    params.update(**kwargs)
    buff = FrameBuffer(x, **params)
    
    mel_coeffs = melfb(samplerate=params.get('samplerate'),
                  nfft=params.get('framesize'),
                  nfilts=params.get('nfilts'),
                  fmin=params.get('freq_min'),
                  fmax=params.get('freq_max'),
                  width=params.get('width'),
                  norm_type=params.get('type'))
    
    framelist = []
    while buff.update_framebuffer():
        X = mel_warp(frame=buff.framebuffer.mean(axis=-1)[:,np.newaxis],
                        w_n=buff.window,
                        melfb=mel_coeffs)
        framelist.append(X.squeeze())
        
    return np.asarray(framelist)
        

def mfcc(x, **kwargs):
    params = {'framesize':8192,
               'overlap':0.5,
               'samplerate':44100,
               'framemode':'center',
               'freq_min':41.0,
               'freq_max':3520.0,
               'lifter_exp':0.6,
               'nfilts':40,
               'type':1,
               'width':1.0,
               'VERBOSE':False,
               'ndct':13}
    
    params.update(**kwargs)
    
    return melspec_to_mfcc(melspec(x,**params),
                           ndct=params['ndct'],
                           nfilts=params['nfilts'],
                           lifter_exp=params['lifter_exp'])
    
def melspec_to_mfcc(X,ndct,nfilts,lifter_exp):
    X = np.maximum(np.log(X), kMFCC_MIN_VAL)
    dct_coeffs = dctfb(ndct, nfilts)
    Z = np.dot(dct_coeffs,X.T)
    lifter_coeffs = np.array([1.0]+(np.arange(1,ndct)**lifter_exp).tolist())
    return np.dot(np.diag(lifter_coeffs), Z).T
