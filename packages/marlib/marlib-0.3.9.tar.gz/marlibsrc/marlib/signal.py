"""
Created on Apr 16, 2011

@author: humphreyadmin
"""

import numpy as np
from scipy.signal.filter_design import freqz
from scipy.signal.signaltools import lfilter, convolve2d
from marlib import eps, Hell
from scipy.signal.windows import gaussian

def threshlevel(x, nbins = 256, dtype = float, axis=None, NORM=False):
    """
    
    x : nd.array
        N-Dimensional array of values
    dtype : str
        Data type
    nbins : int
    """
    if axis is None:
        x = x.flatten()
    elif axis < x.ndim:
        
        x = x.mean(axis=axis).flatten()
        
    bins = np.histogram(x, bins=nbins)[0]
    
    p = bins / float(bins.sum())
    w = np.cumsum(p)
    m = np.cumsum(p * np.arange(nbins))
    s = np.power(m[-1] * w - m, 2.0) / (w * (1.0 - w) + np.power(2.0, -15))
    maxidx = s.argmax()
    idx = maxidx.mean()
    
    if(dtype == float):
        return x.max()*idx / float(nbins)
    elif(dtype == int):
        return idx
    else:
        raise ValueError("Invalid data type: %s"%dtype)

def athresh(x,axis=-1,BINARY=False):
    """
    Help! I'm an empty doc string!
    """
    offset = x.min()
    x -= offset
    t_level = threshlevel(x,axis=axis)
    if BINARY:
        return np.greater_equal(x,np.ones(x.shape)*t_level)
    else: 
        mask = np.greater_equal(x,np.ones(x.shape)*t_level)
        return np.asarray(mask,dtype=float)*x+offset

def athresh_filt(x,lag,axis):
    """
    Help! I'm an empty doc string!
    """
    offset = x.min()
    x -= offset
    
    if axis==1:
        x = x.transpose()
    
    buff = np.zeros([lag,x.shape[1]])
    y = []
    for x_m in x:
        buff[:-1] = buff[1:]
        buff[-1] = x_m
        t_level = threshlevel(buff,axis=-1)
        mask = np.greater_equal(x_m,np.ones(x_m.shape)*t_level)
        y += [np.asarray(mask,dtype=float)*x_m+offset]
    
    y = np.asarray(y)
    
    if axis==1:
        y.transpose()
    return y

def parabolic_interp(y):
    """
    Help! I'm an empty doc string!
    """
    a = 0.5 * (y[2] - 2 * y[1] + y[0])
    c = a + y[1] - (y[2] - y[0]) ** 2
    if a==0.0:
        dx = (y[2] - y[0]) / 4.0 / a
    else:
        dx=0
    return dx, c

def noise_scale(x,n,snr):
    """
    Help! I'm an empty doc string!
    """
    return rms(x) / rms(n) * np.power(10, -snr/20.0)

def awgn(x,snr):
    """
    Help! I'm an empty doc string!
    """
    n = np.random.standard_normal(x.shape)
    x = x + n*noise_scale(x, n, snr)
    if np.abs(x).max() > 1.0:
        x /= np.abs(x).max()
    return x 

def dBs(x):
    """
    Help! I'm an empty doc string!
    """
    return 20.0*np.log10(x + eps)

def rms(x):
    return np.sqrt(np.power(x,2.0).mean())

def adjust_dBgain(x,dblevel):
    """
    Help! I'm an empty doc string!
    """
    return (10**(dblevel/20.0))*x

def brickwall(wp, gstop = -60.0, knee = 0.025):
    """
    Generate the impulse response of a brickwall filter
        satisfying the given parameters

    Params
    ----------
    wp : float
        normalized passband frequency
    gstop: float (default = -60.0)
        stopband attenuation in dB 
    knee: float (default = 0.025)
        transition width in normalized freq
    
    Returns
    -------
    s : 1-dim array
        time-domain coefficients of the FIR filter  
    
    """
    N = 1
    DONE = False
    while not DONE and (N / wp + N) < 8192:
        kp = np.round(N)
        ks = np.round(N / wp) - kp
        S_k = np.concatenate([np.ones(kp), np.zeros(ks)])
        s_n = np.fft.fftshift(np.real(np.fft.ifft(np.concatenate([S_k, S_k[::-1]]))))
        w = freqz(s_n, 1.0)
        w = (20 * np.log10(np.abs(w[1])))
        idx = np.min([np.round((wp + knee) * len(w)), len(w)])
        if w[idx] < gstop:
            DONE = True 
        else:
            N += 1
    
    return s_n

def brickwall_complex(wp, gstop = -60.0, knee = 0.025):
    """
    Generate the impulse response of a brickwall filter
        satisfying the given parameters

    Params
    ----------
    wp : float
        normalized passband frequency
    gstop: float (default = -60.0)
        stopband attenuation in dB 
    knee: float (default = 0.025)
        transition width in normalized freq
    
    Returns
    -------
    s : 1-dim array
        time-domain coefficients of the FIR filter  
    
    """
    N = 8
    DONE = False
    while not DONE and (N / wp + N) < 4096:
        kp = np.round(N)
        ks = np.round(N / wp) - kp
        S_k = np.concatenate([np.ones(kp), np.zeros(ks), np.zeros(ks), np.zeros(kp)])
        s_n = np.fft.ifft(S_k)
        w = freqz(s_n, 1.0)
        w = (20 * np.log10(np.abs(w[1])))
        idx = np.min([np.round((wp + knee) * len(w)), len(w)])
        if w[idx] < gstop:
            DONE = True 
        else:
            N += 1
    
    return np.fft.fftshift(s_n)


# Bandlimited Interpolation
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def sinc_interp(signal, fs_in, fs_out):
    """
    Help! I'm an empty doc string!
    """
    precision = .005
    L_max = 100
    
    fs_in = float(fs_in)
    fs_out = float(fs_out)
    R = fs_out / fs_in
    N_in = len(signal)
    
    # Identify the best up/down ratio
    L = 2
    L_best = L
    L_score = 2.0
    while np.abs(L / R - np.round(L / R)) > precision and L < L_max:
        if L_score > np.abs(L / R - np.round(L / R)):
            L_score = np.abs(L / R - np.round(L / R))
            L_best = L
        L += 1
    
    if L == L_max: L_up = L_best
    else: L_up = L
    
    M_down = np.round(L_up / R)
    print("Closest ratio within %f, for %d:%d" % (np.abs(R - L_up / float(M_down)), L_up, M_down))
    fs_temp = fs_in * L_up
    fs_out = fs_temp / float(M_down)
    
    s_n = signal.brickwall(1 / float(L_up))
    y = np.zeros(N_in * L_up)
    
    # Zero Order Hold Upsampling
    for l in xrange(L_up):
        y[l::L_up] = signal
        
    y, zi = lfilter(b = s_n, a = np.ones(1), x = y, zi = np.zeros(len(s_n) - 1))
    y = np.concatenate((y, zi))[len(s_n) / 2:-len(s_n) / 2]

    return y[::M_down]


def gate(env, holdtime = 1.5, on_thresh = -45, off_thresh = -50, samplerate=8192.0):
    """
    Dynamics processing
    
    Params
    ----------
    env : np.ndarray 
        envelope signal to gate, in the range [0,1)
        
    holdtime : float (default=1.5)
        minimum active duration
        
    on_thresh : 
        level to open the gate (active), in dB
        
    off_thresh : 
        level to close the gate, in dB
        
    samplerate : 
        rate of the envelope signal
    
    """
    hold = int(holdtime * samplerate)
    x = dBs(env ** 2)
    
    x = np.asarray([x.min()] + list(x) + [x.min()])
    mask = np.zeros(x.shape)
    active = False
    counter = 0
    for n in xrange(len(x)):
        if active:
            if x[n] < off_thresh:
                if counter > hold:
                    # Probably a note
                    mask[n - int(counter):n] = 1.
                active = False
                counter = 0
            elif counter > hold:
                mask[n - int(counter):n] = 1.
                counter += 1.
            else:
                counter += 1.
        else:
            if x[n] >= on_thresh:
                active = True
                counter += 1.
    return mask[1:-1]


def local_max(x, thresh = 0.0):
    """
    Help! I'm an empty doc string!
    """
    y = np.concatenate([np.zeros(1), x, np.zeros(1)])
    peaks = np.greater(y[1:-1], y[:-2] + thresh) * np.greater_equal(y[1:-1], y[2:] + thresh)
    return x * peaks

def range_max(x, L, beta=0.5, BINARY=False):
    """
    Help! I'm an empty doc string!
    """
    L0 = int(np.round(L*beta))
    L1 = int(np.round(L*(1-beta)))
    y = np.concatenate([np.zeros(L0), x, np.zeros(L1*2)])
    mask = np.zeros(y.shape)
    for n in xrange(L0,L1+len(x)):
        lower = np.less(y[n-L0:n],np.zeros(L0)+y[n]).all()
        upper = np.less_equal(y[n+1:n+L1+1],np.zeros(L1)+y[n]).all()
        mask[n] = float(lower and upper)
    
    if BINARY:
        return mask[L0:-L1]
    else:
        return x*mask[L0:L0+len(x)]

def local_min(x, thresh = 0.0):
    """
    Help! I'm an empty doc string!
    """
    y = np.concatenate([np.zeros(1), x, np.zeros(1)])
    peaks = np.less(y[1:-1], y[:-2] - thresh) * np.less_equal(y[1:-1], y[2:] - thresh)
    return x * peaks

def canny(L, sig=2.0):
    """
    Help! I'm an empty doc string!
    """
    n = np.linspace(-20, 20, L)
    return (-n / np.power(sig, 2.)) * np.exp(-(n ** 2) / (2. * (sig ** 2)))

def hwr(x):
    """
    Help! I'm an empty doc string!
    """
    return 0.5*(x + np.abs(x))

def princarg(x):
    """
    Help! I'm an empty doc string!
    """
    return np.pi + (x + np.pi) % (-2*np.pi)

def sdnorm(x,L=9,sig=1.5):
    """
    Help! I'm an empty doc string!
    """
    g = gaussian(L, sig)
    
    w_g = g.reshape(L,1)*g.reshape(1,L)
    w_g /= w_g.sum()
    
    y = x - convolve2d(x, w_g, mode='same', boundary='wrap')
    return y

def minfilt(x, L):
    """
    Help! I'm an empty doc string!
    """
    y = np.asarray(list(np.zeros(L)) + list(x) + list(np.zeros(L)))
    res = np.zeros(y.shape)
    for n in xrange(L, len(y) - L):
        res[n] = y[n - L:n + L].min()
    
    return res[L:-L]

def maxfilt(x, L, axis=-1):
    """
    Help! I'm an empty doc string!
    """
    if axis==0:
        x = x.transpose()
    elif axis==0 and x.ndim==1:
        x = x.reshape(1,len(x))
    elif axis >= x.ndim:
        raise Hell("You can't do that!")
    
    X = []
    for r in x:
        y = np.asarray(list(np.zeros(L)) + list(r) + list(np.zeros(L)))
        res = np.zeros(y.shape)
        for n in xrange(L, len(y) - L):
            res[n] = y[n - L:n + L].max()
        
        X.append(res[L:-L])
    
    X = np.asarray(X)
    if axis==0:
        return X.transpose()
    elif axis==0 and x.ndim==1:
        return X.flatten()
    elif axis >= x.ndim:
        raise Hell("You can't do that!")
    

def max_peak_pick(x,L):
    """
    Return the peaks of of a vector 'x' along the first
    dimension.
    
    Parameters
    ----------
    x : array_like
        signal to peak pick, assumed to be non-negative.
    L : int
        length of sliding window
    
    Returns
    -------
    y : np.ndarray
        peaks of x; all other elements are zero. 
        
    """
    x = np.asarray(x)
    if x.ndim==1:
        x = x[:,np.newaxis]
    
    X = np.zeros(x.shape)
    pad = np.zeros(L)
    for r in range(x.shape[1]):
        y = np.concatenate([pad,x[:,r],pad],axis=0)
        res = np.zeros(y.shape)
        for n in range(L, len(y) - 2*L):
            z = y[n-L:n+L]
            if (z[L]>z[:L]).all() and (z[L]>=z[L:]).all():  
                res[n] = z[L]
        
        X[:,r] = res[L:-L]
    
    return X
    

def maxpeakfilt_array(x,L,axis=0):
    """
    Help! I'm an empty doc string!
    """
    if x.ndim != 2:
        raise Hell("You can't do that!")
    
    if axis == 1:
        x = x.transpose()
    
    X = []
    y = np.concatenate([np.zeros([L,x.shape[1]]), x, np.zeros([L,x.shape[1]])])
    for n in xrange(L, y.shape[0] - L):
        z = y[n - L:n + L]
        X.append(0)
        if (z[L].max()>z[:L]).all() and (z[L].max()>=z[L:]).all():  
            X[-1] = z[L].max()
        
    X = np.asarray(X).flatten()
    return X

def selfsim_L2(x):
    """
    Help! I'm an empty doc string!
    """
    d = np.power(x[np.newaxis,...] - x[:,np.newaxis,...],2.0).sum(axis=-1)
    return np.sqrt(d)

