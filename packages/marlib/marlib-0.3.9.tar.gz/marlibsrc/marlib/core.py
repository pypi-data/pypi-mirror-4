'''
Created on Sep 21, 2012

@author: ejhumphrey
'''
import numpy as np

class FrameBuffer(object):
    
    def __init__(self, x_in=None, read_idxs=None, **kwargs):
        self.params = {'framesize':4096,
                       'framemode':'left',
                       'frameoffset':0,
                       'hopsize':None,
                       'overlap':0.0,
                       'framerate':None,
                       'samplerate':None,
                       'window':None, # rectangular
                       'norm_win':False,
                       'is_time':False,
                       'VERBOSE':False}
        
        self.update_params(**kwargs)
        self.reset(x_in)
        
        if self.params.get('window') is None:
            self.window = np.ones([self.framesize(),1])
        else:
            if self.params.get('window').shape[0] != self.framesize():
                raise ValueError("Window length (%d) must equal framesize (%d)!"%(self.params.get('window').shape[0], self.framesize()))
            elif self.params.get('window').ndim==1:
                self.params['window'] = self.params.get('window')[:,np.newaxis]
            self.window = self.params.get('window')
        
        if self.params.get('norm_win'):
            self.window /= self.window.sum()/2.0
        
        self.set_read_indexes(read_idxs, is_time=self.params.get('is_time'))
        
            
    def update_params(self, **kwargs):
        """
        """
        self.params.update(kwargs)
        if not (self.params.get('framerate') is None) and not (self.params.get('samplerate') is None):
            self.params['hopsize'] = self.samplerate() / self.framerate()
        elif not (self.params.get('overlap') is None) and (not self.params.get('framesize') is None):
            self.params['hopsize'] = self.framesize()*(1.0 - self.params.get('overlap'))
        
        if self.verbose():
            for k in self.params:
                print k, self.params[k]
    
    def set_read_indexes(self, read_idxs, is_time=False):
        """
    Establish a vector of read times.
    
    Parameters
    ----------
    read_idxs : array_like
        vector of read times
        
    is_time : bool=False
        toggle between sample and time indices
        
    Returns
    -------
    None
    
        """
        if read_idxs is None:
            # if not given, default to fixed frames
            read_idxs = np.arange(self.numframes(),dtype=float)*self.hopsize() + self.frameoffset()
        else:
            read_idxs = np.asarray(read_idxs)
        
        if is_time:
            read_idxs *= self.samplerate()
        
        self._read_idxs = np.asarray(read_idxs,dtype=int)
        self._read_pointer = 0
    
    def reset(self, x_in=None):
        """
        Set the function's read pointer back to zero
        """
        self._EOF=False
        self.x_in = x_in
        if not self.x_in is None:
            self.x_in = np.asarray(self.x_in)
            if self.x_in.ndim==1:
                self.x_in = self.x_in[:,np.newaxis]
            self.framebuffer = np.zeros(self.frameshape())
    
    # --- Getters - During Call ---
    def channels(self):
        # Would need to override
        """
        Returns
        -------
        channels : int
            number of audio channels
        """
        if not self.x_in is None:
            return self.x_in.shape[1]
        else:
            raise ValueError("input vector 'x_in' not pre-assigned")
    
    def numsamples(self):
        # Would need to override
        """
        """
        if not self.x_in is None:
            return self.x_in.shape[0]
        else:
            raise ValueError("input vector 'x_in' not pre-assigned")
    
    # --- Getters ---
         
    def samplerate(self):
        """
        Returns
        -------
        samplerate : float
        """
        if self.params['samplerate']:
            return float(self.params['samplerate'])
        else:
            raise ValueError("samplerate not set - use update_params(samplerate=) to correct")
    
    def verbose(self):
        """
        """
        return self.params['VERBOSE']
    
    def numframes(self):
        """
        """
        return int(np.ceil((self.numsamples() - self.frameoffset()) / float(self.hopsize())))
    
    def framesize(self):
        """
        Returns
        -------
        """
        if self.params.get('framesize'):
            return int(self.params.get('framesize'))
        else:
            raise ValueError("Framesize is not set! Init with a framesize or use set_params(framesize=?) to correct.")
    
    def framerate(self):
        """
        """
        if self.params.get('framerate'):
            return float(self.params.get('framerate'))
        else: # Fallback to hopsize
            return self.samplerate() / float(self.hopsize())
    
    def frameshape(self):
        """
        tuple of (frame length, number of channels)
        """
        return [self.framesize(), self.channels()]
    
    def framemode(self):
        """
        alignment mode: ['left','center','right']
        
        """
        return self.params.get('framemode')
    
    def frameoffset(self):
        """
        phase offset, in samples
        """
        offset = 0
        if self.framemode() == 'center':
            offset = -0.5*self.framesize()
        elif self.framemode() == 'right':
            offset -= self.hopsize()
        
        return int(offset + self.params.get('frameoffset')) 
    
    def hopsize(self):
        """
        phase offset, in samples
        """
        return self.params.get('hopsize')
    
    def overlap(self):
        """
        overlap between frames, as a ratio of the framesize
        """
        return (self.framesize() - self.hopsize()) / float(self.framesize())
    
    def duration(self):
        """
        """
        return self.numsamples() / self.samplerate()
    
    def _data_fetch(self,idx,nsamp):
        # Would need to override
        return self.x_in[idx:idx+nsamp]
        
    def read_frame_at_index(self, sample_idx, framesize=None):
        """
        given a sample index and a frame length, read data directly from a 
        wave file.
        
        Returns a numpy array of shape (framesize,channels).
        In the absence of 'framesize' the default is used.
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
            
        newdata = self._data_fetch(sample_idx, framesize)
        N = newdata.shape[0]
        # Place new data within the frame
        frame[frame_idx:frame_idx+N] = newdata
        return frame
    
    def read_frame_at_time(self, time_idx, framesize=None):
        """
        """
        sample_idx = int(np.round(time_idx*self.samplerate()))
        return self.read_frame_at_index(sample_idx, framesize)
     
    def update_framebuffer(self):
        """
        updates the internal 'frame_buffer' data structure (a numpy array)
        
        Returns True if successful, False otherwise
        If unsuccessful, the framebuffer is cleared to prevent *really* bad 
        things from happening.
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
        fetch the next frame in a sequence, given a set of internal
        read indexes.
        
        updates / modifies:
            framebuffer
            _read_pointer
            _EOF
        """
        if self.update_framebuffer():
            return np.array(self.framebuffer)
    
    def __call__(self,x_in,read_idxs=None):
        self.reset(x_in)
        self.set_read_indexes(read_idxs, is_time=False)
        
        data = np.zeros([self.numframes()]+self.frameshape())
        while self.update_framebuffer():
            data[self._read_pointer-1] = self.framebuffer
        
        return data

        