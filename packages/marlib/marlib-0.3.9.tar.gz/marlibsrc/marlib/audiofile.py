# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#    audiofile.py
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

# Imports
import numpy as np
import struct
import wave
import os

import marlib.utils as utils
from numpy.fft.fftpack import rfft

kMAX_FULL_WAVEFORM_LENGTH = 10*60*44100     # 10 minute file at 44.1 kHz

# --- Helper methods --- 
def _rawdata_to_array(data, channels, bytedepth):
    """
    Convert packed byte string into numpy arrays
    
    Parameters
    ----------
    frame : string
        raw byte string
    channels : int
        number of channels to unpack from frame
    bytedepth : int
        byte-depth of audio data
    
    Returns
    -------
    frame : np.ndarray of floats
        array with shape (N,channels), bounded on [-1.0, 1.0)
    """
    
    N = len(data) / channels / bytedepth
    fmt = 'h' # Assume 2-byte
    if bytedepth==3:
        tmp = list(data)
        [tmp.insert(k*4+3,struct.pack('b',0)) for k in range(N)];
        data = "".join(tmp)
    if bytedepth in [3,4]:
        fmt = 'i'
    
    frame = np.array(struct.unpack('%d%s' % (N,fmt) * channels, data)) / (2.0 ** (8 * bytedepth - 1))
    return frame.reshape([N, channels])

def _array_to_rawdata(frame, channels, bytedepth):
    """
    Convert numpy arrays into writable raw byte strings
    
    Parameters
    ----------
    frame : np.ndarray
        array with shape (N,channels), bounded on [-1.0, 1.0)
    channels : int
        number of channels to interpret from frame; higher 
        priority over the 2nd dimension of 'frame'
    bytedepth : int
        byte-depth of audio data
    
    Returns
    -------
    data : str 
        raw byte string
    """
    
    N = len(frame) * channels
    frame = np.asarray(frame.flatten()*(2.0 ** (8 * bytedepth - 1)), dtype = int)
    frame = struct.pack('%dh' % N, *frame)
    return frame


# --------- Class Definitions ---------
class AudioFile(object):
    
    cname = "AudioFile"
    def __init__(self, filename, **kwargs):
        
        self.params = {'samplerate':44100.0,
                       'channels':1,
                       'bitdepth':16,
                       'VERBOSE':False}
        
        self._filename = filename
        self._wavefile = None
        self.update_params(**kwargs)
        
        try:
            assert utils.is_valid_format(filename, self.verbose())
        except AssertionError:
            utils.is_valid_format(filename, VERBOSE=True)
            raise AssertionError("Error: Unsupported audio file format.")
        
    def close(self):
        """
    Perform a thorough clean-up. Explict method called by built-in __del__()
            
    Returns
    -------
    None
         
        """
        if not self._wavefile is None:
            self._wavefile.close()
            if(self._CONVERT):
                os.remove(self._wavefile._abspath)
    
    def usage(self):
        """
    Display the keywords this object responds to and the respective 
    values.
        """
        
        msg = self.cname + "\n"
        for kv in self.params.items():
            msg += "\t%s = %s\n"%kv
        
        print msg
        
    def __del__(self):
        if not self._wavefile is None:
            self.close()
    
    # --- Setter ---
    def update_params(self, **kwargs):
        """
       Subclass me!
        """
        self.params.update(kwargs)
        if self.verbose():
            self.usage()
    
    # --- Getters --- 
    def samplerate(self):
        """
    Returns
    -------
    samplerate : float
        """
        if self.params['samplerate']:
            return float(self.params['samplerate'])
    
    def channels(self):
        """
    Returns
    -------
    channels : int
        number of audio channels
        """
        if self.params['channels']:
            return int(self.params['channels'])
    
    def bitdepth(self):
        """
    Returns
    -------
    bitdepth : int
        bits per sample
        """
        if self.params['bitdepth']:
            return int(self.params['bitdepth'])
    
    def verbose(self):
        """
    Returns
    -------
    verbose : bool
        """
        return self.params['VERBOSE']
    
        
class FramedAudioFile(AudioFile):
    
    cname = "FramedAudioFile"
    def __init__(self, filename, **kwargs):
        
        self.params = {'framesize':None,
                       'framemode':'left',
                       'frameoffset':0,
                       'hopsize':None,
                       'framerate':None,
                       'overlap':0.0,
                       'samplerate':None,
                       'channels':None,
                       'bitdepth':None,
                       'read_times':None,
                       'VERBOSE':False}
        
        self.update_params(**kwargs)
        AudioFile.__init__(self, filename, **self.params)
        
        # Default hanning window
        self.window = None
        if self.params.get('framesize'):
            self.window = np.hanning( self.framesize() )
            self.window /= self.window.sum()/2.0      
            self.window = self.window[:,np.newaxis]
        
        
    # --- Setter ---
    def update_params(self, **kwargs):
        """        
    Parameters
    ----------
    framerate : float
    
    framemode : string
        one of ['left', 'right', 'center']
    
    frameoffset : float
    
    channels : int 
    
    bitdepth : int
    
    framesize : int
    
    overlap : float
    
    hopsize : float
    
    read_times : array_like
    
        """
        self.params.update(kwargs)
        if not (self.params.get('framerate') is None) and not (self.params.get('samplerate') is None):
            self.params['hopsize'] = self.samplerate() / self.framerate()
        elif not (self.params.get('overlap') is None) and (not self.params.get('framesize') is None):
            self.params['hopsize'] = self.framesize()*(1.0 - self.params.get('overlap'))
        
        if self.verbose():
            print "%s : Current Parameters"%self.cname
            for k in self.params:
                print k, self.params[k]
        
        
    # --- Getters ---
    def numframes(self):
        """    
    Returns
    -------
    nframes : int
        number of frames in the audiofile
        """
        if self.params['read_times'] is None:
            return int(np.ceil((self.numsamples() - self.frameoffset()) / float(self.hopsize())))
        else:
            return len(self.params['read_times'])
    
    def framesize(self):
        """
    Returns
    -------
    framesize : int
        number of samples returned per frame
        """
        if self.params.get('framesize'):
            return int(self.params.get('framesize'))
        else:
            raise ValueError("Framesize is not set! Init with a framesize or use set_params(framesize=?) to correct.")
    
    def framerate(self):
        """        
    Returns
    -------
    framerate : float
        frequency of frames, in Hertz
        """
        if self.params.get('framerate'):
            return float(self.params.get('framerate'))
        
        else: # Fallback to hopsize
            return self.samplerate() / float(self.hopsize())
    
    def frameshape(self):
        """
    Returns
    -------
    shape : tuple
        tuple of (frame length, number of channels)

        """
        return (self.framesize(), self.channels())
    
    def framemode(self):
        """
    Returns
    -------
    mode : string
        alignment mode, one of ['left','center','right']
        """
        return self.params.get('framemode')
    
    def frameoffset(self):
        """
    Returns
    -------
    offset : int
        Frame offset, in samples
        """
        offset = 0
        if self.framemode() == 'center':
            offset -= 0.5*self.framesize()
        elif self.framemode() == 'right':
            offset -= self.framesize()
        
        return int(offset + self.params.get('frameoffset')) 
    
    def hopsize(self):
        """
    Returns
    -------
    hopsize : float
        Number of samples between adjacent frames.
        
        """
        return self.params.get('hopsize')
    
    def overlap(self):
        """
    Returns
    -------
    overlap : float
        Overlap between frames, as a ratio of the framesize
        
        """
        return (self.framesize() - self.hopsize()) / float(self.framesize())
    
    def duration(self):
        """
    Returns
    -------
    dur : float
        duration of the audiofile, in seconds
        
        """
        return self.numsamples() / self.samplerate()
    
    def numsamples(self):
        """
    Returns
    -------
    n : int
        number of samples in the file
        
        """
        samps = self._wavefile.getnframes()
        if samps > 0:
            return samps
        else:
            raise ValueError("Number of samples not contained in file header!")

class AudioReader(FramedAudioFile):
    """
    """
    
    cname = "AudioReader"
    
    def __init__(self, filename, **kwargs):
        
        self.params = {'framesize':4096,
                       'framemode':'left',
                       'frameoffset':0,
                       'hopsize':None,
                       'overlap':0.0,
                       'framerate':None,
                       'samplerate':None,
                       'channels':None,
                       'bitdepth':None,
                       'read_indexes':None,
                       'VERBOSE':False}
        
        self.update_params(**kwargs)
        FramedAudioFile.__init__(self, filename, **self.params)
        
        # See if we need to SoX this
        self._CONVERT = False    
        try:
            self._wavefile = wave.open(self._filename, 'r')
            if((self._wavefile.getsampwidth()*8 != self.bitdepth() ) & (self.bitdepth() is not None)):
                self._CONVERT = True
            if((self._wavefile.getframerate() != self.samplerate()) & (self.samplerate() is not None)):
                self._CONVERT = True
            if((self._wavefile.getnchannels() != self.channels()) & (self.channels() is not None)):
                self._CONVERT = True
        except wave.Error:
            self._CONVERT = True
         
        # File format conversion check
        if(self._CONVERT):
            self._wavefile = utils.convert(self._filename,
                                               samplerate=self.samplerate(),
                                               bitdepth=self.bitdepth(),
                                               channels=self.channels())
        # - - - - END.if - - - -  
        
        # Overwrite with actual params
        self.update_params(channels = self._wavefile.getnchannels(),
                           bitdepth = self._wavefile.getsampwidth() * 8,
                           samplerate = self._wavefile.getframerate())
        
        if self.verbose():
            print("AudioReader Parameters:")
            print("  Conversion Necessary: %s"%self._CONVERT)
            if self._CONVERT:
                print("  Temp File: %s."%self._wavefile._abspath)
                
        self.reset()
        
    def reset(self):
        """
    Set the file's read pointer back to zero & take care of
    initialization.
    
    Returns
    -------
    None
        """
        self._EOF=False
        self.set_read_indexes(self.params.get('read_times'),True)
        self.framebuffer = np.zeros(self.frameshape())
    
    def set_read_indexes(self, read_ptrs, is_time=False):
        """
    Establish a vector of read times for pulling from an audiofile.
    
    Parameters
    ----------
    read_ptrs : array_like
        vector of read times or indexes
        
    is_time : bool=False
        toggle between sample and time indices
        
    Returns
    -------
    None
    
        """
        if read_ptrs is None:
            # if not given, default to fixed frames
            is_time = False
            read_ptrs = np.arange(self.numframes(),dtype=float)*self.hopsize() + self.frameoffset()
        else:
            read_ptrs = np.asarray(read_ptrs)
        
        if is_time:
            read_ptrs *= self.samplerate()
        
        self._read_idxs = np.asarray(read_ptrs,dtype=int)
        self._read_pointer = 0
    
    # --- Read Methods ---
    def read_frame_at_index(self, sample_idx, framesize=None):
        """
    Given a sample index and a frame length, read data directly from a 
    wave file. 
    
    Parameters
    ----------
    sample_idx : int
        starting sample index to read from
        
    framesize : int=None
        number of samples to return, if None uses the current default
        
    
    Returns
    -------
    x : np.ndarray
        signal array with shape (time, channels)
        
        """
        if framesize is None:
            framesize = self.framesize()
        
        frame_idx = 0
        frame = np.zeros([framesize,self.channels()])
        
        # Check boundary conditions
        if sample_idx < 0 and sample_idx + framesize > 0:
            framesize = framesize - np.abs(sample_idx)
            frame_idx = np.abs(sample_idx)
            sample_idx = 0
        elif sample_idx > self.numsamples():
            return frame
        elif (sample_idx + framesize) < 0:
            return frame
            
        self._wavefile.setpos(sample_idx)
        newdata = _rawdata_to_array(self._wavefile.readframes(int(framesize)),
                                    self.channels(),
                                    self._wavefile.getsampwidth())
        N = newdata.shape[0]
        # Place new data within the frame
        frame[frame_idx:frame_idx+N] = newdata
        return frame
    
    def read_frame_at_time(self, time_idx, framesize=None):
        """
    Read a frame of data at an arbitrary time point in the file.
    
    Parameters
    ----------
    time_idx : float
        start read time, in seconds
        
    framesize : int=None
        number of samples to return, if None uses the current default
    
    Returns
    -------
    x : np.ndarray
        signal array with shape (time, channels)
    
        """
        sample_idx = int(np.round(time_idx*self.samplerate()))
        return self.read_frame_at_index(sample_idx, framesize)
     
    def update_framebuffer(self):
        """
    Updates the internal 'frame_buffer' data structure (a numpy array)
    
    Returns
    -------
    status : bool
        True if successful, False otherwise. If unsuccessful, the 
        framebuffer is cleared to prevent *really* bad things 
        from happening.
    
        """
        if not self._EOF:
            sample_idx = self._read_idxs[self._read_pointer]
            self._read_pointer += 1
            if self._read_pointer >= len(self._read_idxs):
                self._EOF = True
            self.framebuffer[:,:] = self.read_frame_at_index(sample_idx)
            return True
        
        self.framebuffer[:,:] = 0.0
        return False
        
    
    def next_frame(self):
        """
    Fetch the next frame in a sequence, given a set of internal
    read indexes.
    
    Internally updates / modifies:
        framebuffer
        _read_pointer
        _EOF
    
    Returns
    -------
    frame : np.ndarray
        Next sequential frame of data, with shape (framesize, channels)
        """
        if self.update_framebuffer():
            return np.array(self.framebuffer)
        
    
    def full_waveform(self, FORCE=False):
        """
    Read the entire waveform as a non-overlapping signal.
    
    Parameters
    ----------
    FORCE :  bool=False
        Over-ride the filesize safety check that prevents reading in too 
        much data into memory.
         
    Returns
    -------
    x : np.ndarray
        full signal read from the audiofile, bounded on [-1.0, 1.0)
        
        """
        if self.numsamples() < kMAX_FULL_WAVEFORM_LENGTH or FORCE:
            return self.read_frame_at_index(0, self.numsamples())
        else:
            raise ValueError("""Yikes! This file is longer than you might think ...
    Use 'FORCE=True' to over-ride this safety net.""")
    
    def spectrogram(self,N=None):
        """
    Compute the spectrogram of the initialized audiofile.
    
    Parameters
    ----------
    N : int=None
        optional N-length fft to compute
        
    Returns
    -------
    X : np.ndarray
        complex-valued spectrogram of the provided file
        
        """
        if N is None:
            N = self.framesize()
            
        K = N/2 + 1
        X = np.zeros([self.numframes(),K],dtype=np.complex)
        for m in range(self.numframes()):
            X[m] = rfft(self.next_frame().mean(axis=-1)*self.window.flatten(), N)

        self.reset()
        return X 
    
    def buffered(self):
        """
    Buffer the audiofile into a single matrix.
    
    Returns
    -------
    x : np.ndarray
        array of the audiofile, buffered with the provided framesize 
        and overlap parameters, with shape (M x framesize x channels) 
        
        """
        X = np.zeros([self.numframes(),self.framesize(),self.channels()])
        for m in range(self.numframes()):
            X[m] = self.next_frame()

        self.reset()
        return X

        

class AudioWriter(FramedAudioFile):
    """
    AudioWriter(filename, framesize=2048, overlap=0.0, samplerate=44100.0,
        channels=1, bitdepth=16, VERBOSE=False):

    Create an AudioWriter object for arbitrary soundfile creation. Depends
    on SoX (and the necessary codecs) for creating files other than wav's.
    
    Parameters
    ----------
    filename : str
        filepath to access
    framesize : int
        samples per frame, defaults = 2048
        ** Note: Passing None allows for arbitrary frame writing
    overlap : float
        overlap ratio in the range [0.0, 1), default = 0
    samplerate : float
        desired sample rate, defaults to 44100 Hz
    channels : int
        desired channel count, defaults to one
    bitdepth : int
        desired bit depth, defaults to 16
    VERBOSE : bool
        control print-outs for debugging purposes
    
    TODO: Examples
    --------
    >>> writer = AudioReader(file) 
    
    Writing a file
    >>>     ...
        
    """
    
    cname = "AudioWriter"
    def __init__(self, filename, **kwargs):
        
        self.params = {'framesize':None,
                       'framemode':'left',
                       'frameoffset':0,
                       'hopsize':None,
                       'framerate':None,
                       'samplerate':44100.0,
                       'channels':1,
                       'bitdepth':16,
                       'write_indexes':None,
                       'VERBOSE':False}
        
        self.update_params(**kwargs)
        FramedAudioFile.__init__(self, filename, **self.params)
                
        # Let's see if we'll need to SoX this
        self._CONVERT = False
        try:
            self._wavefile = wave.open(self._filename, 'w')
        except:
            self._CONVERT = True
        
        # Set file parameters
        self._wavefile.setframerate(self.samplerate())
        self._wavefile.setsampwidth(int(self.bitdepth()/8+.5))
        self._wavefile.setnchannels(self.channels())
        if self._CONVERT:
            self._wavefile._abspath = utils.temp_wavfile() 
        
        if(self.verbose()):
            print "AudioWriter Parameters"
            print "Conversion Necessary: %s"%(self._CONVERT)
            if(self._CONVERT):
                print "\tTemp File: %s"%(self._wavefile._abspath)
            
        self._bucket_to_write = 0
        self._write_idx = 0
        return
    
    def close(self):
        """
    Perform a thorough clean-up, necessary for wave writing.

    Returns
    -------
    None    
        """
        
        self._wavefile.close()
        if(self._CONVERT):
            utils.convert(filename=self._wavefile._abspath,
                             fout=self._filename)
            os.remove(file=self._wavefile._abspath)

            
    # --- Write Methods --- 
    def write_frame(self, frame, CLIP=True):
        """
    Adds the next frame of audio samples to the file 
    as an np.ndarray with shape (framesize,channels).
    
    Parameters
    ----------
    frame : array_like
        chunk of data to write out to the file
    
    CLIP : bool=True
        flag to force clipping of values outside [-1.0,1.0)
        
    Returns
    -------
    None
        
        """
        frame = np.asarray(frame)
        if frame.ndim==1 and self.channels( )== 1:
            frame = frame[:,np.newaxis]
        
        if frame.shape[1] != self.channels():
            raise AssertionError("Frame to write has an unexpected shape %s, expected (:,%d)."%(frame.shape, self.channels()))
        
        
        if CLIP:
            pos_clip = frame>=1.0
            neg_clip = frame<-1.0
            frame[pos_clip]=1-np.power(2.0,-15.0)
            frame[neg_clip]=-1.0
            if self.verbose():
                print "Clipped %d samples!"%(pos_clip.sum()+neg_clip.sum())
        
        data = _array_to_rawdata(frame,
                             self.channels(),
                             self._wavefile.getsampwidth())
    
        self._wavefile.writeframes(data)
        
        
def wavread(f_in,Fs=None):
    """
    Given a sound file and a desired sampling rate, return the
    full waveform and the sampling rate of the signal.
    
    Note: This is slightly different from MATLab's wavread, in that
    the sampling rate can be changed and the sound file need not
    strictly be a wavefile.
    Parameters
    ----------
    f_in : string
        Path to sound file. Does not need to be wave format.
    
    Fs : float
        Desired samplerate of the returned signal. Does not need
        to be the samplerate of the file.
    
    Returns
    -------
    x : np.ndarray
        
    
    """
    ar = AudioReader(f_in,samplerate=Fs)
    return ar.full_waveform(), ar.samplerate()
    

def wavwrite(x,f_out,Fs):
    """
    Given a signal 'x', a sound file name, and a desired sampling rate, 
    write the waveform to disk.
    
    Note: This is slightly different from MATLab's wavwrite, in that
    the sound file need not strictly be a wavefile, based on the extension
    given.
    
    Parameters
    ----------
    x : array_like
        Audio to write to disk. If multichannel, the first dimension is 
        time, and the second dimension is channel.
    f_out : string
        Path to output file. Directory must exist. This really is for 
        the best.
    Fs : float
        samplerate of the signal 'x'
    
    Returns
    -------
    None
    """
    x = np.asarray(x)
    if x.ndim==1:
        x = x[:,np.newaxis]
    
    aw = AudioWriter(f_out,samplerate=Fs,channels=x.shape[1])
    aw.write_frame(x)
    aw.close()
