#!/usr/bin/env python
from tulip.tasks import coroutine
from tulip.locks import EventWaiter

class ROBuffer:
    def __init__(self, inital=b""):
        self._buffer = buffer
        self._future = None
        self._finialized = EventWaiter()
        self.finialized = False
        
    @coroutine
    def read(self, length=None):
        if length and length < len(self._buffer):
            buf = self._buffer[:length]
            self._buffer = self._buffer[length:]
            return buf
        elif length is None:
            yield from self._finalized.wait()
            buf = self._buffer
            self._buffer = b""
            return buf
        else:
            # waiting on more data to read
            while True:
                yield from self._append_event.wait()
                if length < len(self.buffer):
                    buf = self._buffer[:length]
                    self._buffer = self._buffer[length:]
                    return buf
                
        
    def append_buffer(self, data):
        self._buffer += buffer
        self._future.set_result(buffer)
        self._append_event.set()
    
    def finalize(self):
        """No more data to be read, buffer is 'finalized'"""
        self.finalized = True
        self._finalized.set()
        self._future.set_result()

class OutputStream:
    """A Buffer for outgoing data transmission on a file like object.
    
    this implementation can be 'paused', which when activated will buffer
    all writes internnaly and return instantly. when the buffer is 'unpaused'
    all pending writes will be commited in one go.
    
    this is mainly intended to prevent writing of an HTTP reply body before
    the headers have been written (ie start_response will write the headers 
    to the stream then unpause the buffer) but may also be used for coalescing
    writes together and sending them as one update
    """
    def __init__(self, stream):
        self._stream = stream
        
        self.is_paused = True
        self._buffer
    
    def sendfile(self, filename):
        pass
    
    def write(self, data):
        if self.is_paused:
            self._buffer += data
        
    def writelines(self, lines):
        if self.is_paused:
            self._buffer = b"".join([self._buffer] + lines)
        else:
            # selector based implementation, for a proactor
            # based implementation look at b"".join(lines)
            # and submitting that as one unit or using a
            # scatter/gather write mechanism
            for line in lines:
                self.write(line)
        
    def pause(self):
        self.is_paused = True
        
    def unpause(self):
        self.is_paused = False
        self._flush()
    
    def _flush(self):
        pass
        
