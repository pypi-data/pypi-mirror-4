r#!/usr/bin/env python
"""Archangel: fast lazy webserver based off of TULIP/yield from
"""

def make_environ():
    uri_parts = urlsplit(info.uri)
    url_scheme = 'https' if self.is_ssl else 'http'
    
    environ = {
        'wsgi.input': payload,
        'wsgi.errors': sys.stderr,
        'wsgi.version': (1, 0),
        'wsgi.async': True,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'wsgi.file_wrapper': FileWrapper,
        'wsgi.url_scheme': url_scheme,
        'SERVER_SOFTWARE': tulip.http.HttpMessage.SERVER_SOFTWARE,
        'REQUEST_METHOD': info.method,
        'QUERY_STRING': uri_parts.query or '',
        'RAW_URI': info.uri,
        'SERVER_PROTOCOL': 'HTTP/%s.%s' % info.version
    }


from weakref import WeakValueDictionary
class ProcessManager:
    def __init__(self):
        self.processes = WeakValueDictionary()
        self.pid = 0
        self._next_pid = self.pid + 1
    
    def new_pid(self):
        pid = self._next_pid
        self._next_pid += 1
        
        return pid
    
    def register(self, obj):
        pid = self.new_pid()
        obj._archangel_pid = pid
        obj._archangel_manager = self
        self.processes[pid] = obj

        return obj
    
    def deregister(self, pid):
        del self.processes[pid]

class Process:
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        obj._at_exit = []
        # add a handler to signal the Process manager that we have exited
        obj.at_exit(lambda proc: proc._archangel_manager.deregister(proc._archangel_pid))
        
        return obj
        
    def _kill(self):
        try:
            self.kill()
        except:
            # ensure that we exit corectly even if an exception is raised
            self.exit()
            raise
        else:
            self.exit()
        
    def kill(self):
        """Function hook for implementations to catch a 'kill' signal and do some 
        cleanup work
        """
        pass
        
    def at_exit(self, func, *, **kwargs):
        """Register a function to be called when this process exits
        
        each function registered will be called with the process instance as the
        first argument
        """
        self._at_exit.append((func, **kwargs))
        
    def exit(self):
        """Notify the ProcessManager that we are done or will finish up shortly"""
        for func, kwargs in self._at_exit:
            try:
                func(self, **kwargs)
            except Exception as err:
                # TODO: log this as an exception
                pass
            
def kill(proc):
    """Send the exit signal to a process"""
    proc._kill()
    
from tulip.futures import Future
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
        
from tulip.protocols import Protocol
class BaseHTTPProtocol(Protocol):
    def connection_made(self, transport):
        self.transport = transport
        self.body = body = None #Buffer()
        self.handle_request('GET', '/', 'HTTP/1.1', {}, body)

    def data_recived(self, data):
        self.body.append_buffer(data)
        
    def eof_recived(self):
        pass
        
    def connection_lost(self, exc):
        pass
    
from tulip.tasks import task, sleep
class ArchangelServer(BaseHTTPProtocol, Process):
    def __init__(self):
        self.method = "GET"
        self.path = "/"
        self.http_version = "HTTP/1.1"
        self.headers = []
        self.body = None
        self.reply = None
    @task
    def handle_request(self, method, path, http_version, headers, body):
        # hmm, seems to be a shortcomming of the protocol. we have
        # to peak inside the transport object in its private space
        # to get the address of the other end
        peer = self.transport._sock.getpeername()
#        print("{peer[0]:>15}:{peer[1]:>5} {method:<5} {path}".format(peer=peer, method=method, path=path))
        # line = yield from body.read()
        yield from sleep(2)
        self.transport.write(b'200 OK\r\ncontent-length: 4\r\n\r\ntest')
        self.transport.close()
        self.exit()

def sigint_handler():
    import sys
    print("Recived SIGINT, Exiting gracefully")
    sys.exit(0)
    
def tulip_server():
    import tulip
    loop = tulip.get_event_loop()

    import signal
    loop.add_signal_handler(signal.SIGINT, sigint_handler)

    manager = ProcessManager()
    server = loop.start_serving(lambda: manager.register(ArchangelServer()), 'localhost', 8080)
    x = loop.run_until_complete(server)
    
    def list_procs():
        print ("--------")
        for pid, proc in manager.processes.items():
            print("{:>5}: {}".format(pid, proc))
    loop.call_repeatedly(1.0, list_procs)
    
    #import gc
    #loop.call_repeatedly(5.0, lambda: print('>>>'))
    #loop.call_repeatedly(5.0, lambda: gc.collect())

    print('Listening on {}:{}'.format(*x.getsockname()))
    loop.run_forever()
    
if __name__ == "__main__":
    tulip_server()
