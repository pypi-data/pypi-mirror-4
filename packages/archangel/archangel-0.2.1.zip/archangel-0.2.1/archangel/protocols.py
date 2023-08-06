#!/usr/bin/env python
from tulip.protocols import Protocol
from tulip.tasks import task, sleep
from tulip import get_event_loop
from .process import Process
from io import BytesIO

class HTTPProtocolWarning(Exception): pass
class HTTPProtocolError(Exception): pass

class BaseHTTPProtocol(Protocol):
    def connection_made(self, transport):
        self.transport = transport
#        self.body = body = None #Buffer()
#        self.handle_request('GET', '/', 'HTTP/1.1', {}, body)

    def data_recived(self, data):
#        self.body.append_buffer(data)
        pass
                
    def eof_recived(self):
        pass
        
    def connection_lost(self, exc):
        pass
    
class HTTPServerProtocol(BaseHTTPProtocol, Process):
    def __init__(self, app):
        self.app = app
        self.headers = []
        self.body = BytesIO()
        self.state = 'parse protocol'
        self.buffer = b""
        
    def data_received(self, data):
        try:
            if self.state == 'parse protocol':
                # we check for a newline in data rather self.buffer
                # as it reduces the ammount of bytes we have to search
                # also means each byte is only checked once, where ase
                # searching self.buffer means the leading bytes could
                # be checked multiple times
                if b'\n' in data:
                    line, sep, new_buffer = data.partition(b'\n')
                    line = self.buffer + line.strip()
                    self.method, self.path, self.protocol = self.parse_protocol(line)
    
                    data = new_buffer
                    self.buffer = b""
                    
                    self.state = 'parse headers'
                else:
                    self.buffer += data
                    
            if self.state == 'parse headers':
                if b'\r\n\r\n' in data:
                    block, sep, new_buffer = data.partition(b'\r\n\r\n')
                    block = self.buffer + block
                    self.headers = self.parse_headers(block)
                    
                    self.body.seek(0)
                    self.body.write(new_buffer)
                    
                    self.state = 'body'

                    loop = get_event_loop()
                    loop.call_soon(self.app, self.transport, 
                                             self.method, 
                                             self.path, 
                                             self.protocol, 
                                             self.headers, 
                                             self.body)
                elif b'\n\n' in data:
                    block, sep, new_buffer = data.partition(b'\n\n')
                    block = self.buffer + block
                    self.headers = self.parse_headers(block)
                    
                    self.body.seek(0)
                    self.body.write(new_buffer)
                    
                    self.state = 'body'
                    
                    loop = get_event_loop()
                    loop.call_soon(self.app, self.transport, 
                                             self.method, 
                                             self.path, 
                                             self.protocol, 
                                             self.headers, 
                                             self.body)
                else:
                    self.buffer += data
                    
            if self.state == 'body':
                self.body.write(data)

        except HTTPProtocolWarning:
            # TODO: Log a warning
            pass
        except HTTPProtocolError:
            # Bad unrecoverable things have happened, commit Seppuku
            self.transport.close()
            
    @staticmethod
    def parse_protocol(line):
        components = line.split()
        if len(components) != 3:
            raise VeryBadError('malformed request, Protocol line: ' + line)
        
        return components
        
    @staticmethod
    def parse_headers(block):
        # can we cut down the ammount of allocations here?
        lines = block.split(b'\n')
        # [::2] will skip the middle element (sep) that we dont want
        headers = (line.partition(b':')[::2] for line in lines)
        headers = [(x.strip(), y.strip()) for x,y in headers]
        
        return headers

#    @task
#    def handle_request(self):
#        self.transport.write(b'200 OK\r\ncontent-length: 4\r\n\r\ntest')
#        self.transport.close()
#        self.exit()


class FCGIProtocol(BaseHTTPProtocol, Process):
    def __init__(self, app):
        self.app = app
        
    @task
    def handle_request(self):
        self.transport.write(b'200 OK\r\ncontent-length: 4\r\n\r\ntest')
        self.transport.close()
        self.exit()

