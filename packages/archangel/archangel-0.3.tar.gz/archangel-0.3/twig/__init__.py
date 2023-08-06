#!/usr/bin/env python
"""TWIG: An collection of helper functions for implementing the tulip webservices interface gateway
"""
__author__ = "Da_Blitz"
__email__ = "code@pocketnix.org"
__url__ = "http://code.pocketnix.org/archangel"
__version__ = "0.3"
__license__ = "ISC"

from urllib.parse import quote_from_bytes as urlencode
import io

HTTP_REPLY_VERSION = b'HTTP/1.1'
LF = b"\r\n"

def split_version(raw_version):
    """Given a string representing a version as specified in RF3875, transform it into a tuple
    
    eg:
    >>> split_version(b'HTTP/1.1')
    (b'HTTP', (1, 1))
    
    This function does not have the limitation of the 2 version numbers being single digits
    
    :param bytes raw_version: A Byte string representing the version to be parsed
    :rtype tuple: The parsed version contisting of a tuple containg the protocol followed by a 2
                  tuple containg 2 integers representing the version number
    
    May raise a ValueError if the supplied version numbers are not integers
    """
    protocol, version = raw_version.split(b"/", 1)
    major, minor = version.split(b".")
    
    major, minor = int(major), int(minor)
    
    return (protocol, (major, minor))


class Request:
    def __init__(self, method, headers={}, body=None, script_name=b"", path_info=b"", query=b"", 
                 content_type=None, content_length=None, envrion={},
                 server_name=b"", server_addr=b"", server_port=80, 
                 server_protocol=(b"HTTP", (0, 9)), server_type=None,
                 remote_addr=b"", remote_host=b"", remote_port=0, remote_user=None,
                 ssl_protocol=None, auth_type=None, gateway_interface=(b"TWIG", (0, 1))):
        # method: All uppercase byte string, eg: [HEAD GET PUT POST DELETE PATCH]
        self.method = method
        # headers: dict
        self.headers = headers
        # body: a filelike object compatible with tulip (future from .read()) that is non-seekable
        self.body = body
        # script_name: byte string
        self.script_name = script_name
        # path_info: byte string
        self.path_info = path_info
        # query: byte string
        self.query = query
        # content_type: byte string
        self.content_type = content_type
        # content_length: None or int, None for no body methods such as GET, int otherwise
        #                 -1: No length specified (possible chuncked body encoding
        #                  0: Body has no content
        #                >=1: The length in bytes of the request body
        # TODO: Can we eliminate teh None state and make it '0', perhaps make -1 'None'
        if content_length:
            content_length = int(content_length)
        self.content_length = content_length
        # environ: dict
        self.envrion = environ
        
        # server_name: byte string
        self.server_name = server_name
        # server_addr: byte_string
        self.server_addr = server_addr
        # server_port: int
        self.server_port = int(server_port)
        # server_protocol: protocol version as specified by split_version()
        if isinstance(server_protocol, bytes):
            server_protocol = split_version(server_protocol)
        self.server_protocol = server_protocol
        # server_version: server version as specified by split_version()
        if isinstance(server_type, bytes):
            server_type = split_version(server_type)
        self.server_type = server_type
    
        # remote_addr: byte_string
        self.remote_addr = remote_addr
        # remote_host: byte_string
        self.remote_host = remote_host
        # remote_port: int
        self.remote_port = int(remote_port)
        # remote_user: byte_string
        self.remote_user = remote_user
        
        # ssl_protocol: ssl version as specified by split_version()
        if isinstance(ssl_protocol, bytes):
            ssl_protocol = split_vertion(ssl_protocol)
        self.ssl_protocol = ssl_protocol
        # auth_type: byte string, uppercase, eg: b'DIGEST' or b'SPENGO'
        self.auth_type = auth_type.upper()
        # gateway_interface: gateway interface version as specified by split_version()
        if isinstance(gateway_interface, bytes):
            gateway_interface = split_version(gateway_interface)
        self.gateway_interface = gateway_interface
    
    @property
    def path_translated(self):
        """A url encoded version of :py:attr:`.path_info`
        
        :rtype bytes: The url encoded path_info
        """
        return urlencode(self.path_info)
    
    @property
    def secure(self):
        """Returns True if using an encrypted connection to the client
        
        :rtype bool: is client connecting using an encrypted connection?
        """
        if self.ssl_protocol:
            return self.ssl_protocol[0] in ['TLS', 'SSL']
        return false
    
    https = secure

    @property
    def authenticated(self):
        """Resturns True if the remote user has authenticated to the server
        
        :rtype bool: has the client authenticated?
        """
        return self.remote_user is not None

    def __getitem__(self, key):
        return self.headers[key]

    def __contains__(self, key):
        return key in self.headers

    def clone(self):
        """Return a copy of ourselves that can be modified, then supplied to the next app in a middleware pipe
        
        :rtype Response: A clone of the current response object
        """
        obj = self.__new__(self.__class__)
        obj.__dict__ = self.__dict__.copy()
        
        return obj
        

class Response:
    def __init__(self, transport):
        self.transtport = transport
        self.clear()
        self._paused = True
        
    def add_header(self, key, val):
        self.headers.append((key, val))
        
    def start_response(self, status, headers, *, version=HTTP_REPLY_VERSION):
        """No data is sent until this function is called. all data will be buffered"""
        # Lots of small writes comming up, so collapse them into one larger write
        self.pause()
        self.write(version, status + LF)
        headers = self.headers + headers
        self.writelines(k + b": " + v + LF for k, v in headers)
        self.write(LF)
        self.unpause()
        
        # Stop buffering writes
        self._unpause()
        self._flush()
        
    def close(self):
        """Flush all remaining data and close the connection
        
        Applications should not normmaly need to call this as connections should
        be closed by your framework when the function returns
        """
        self.transport.close()
    
    def abort():
        """Close the connection to the other end immediately, don't flush data"""
        self.transport.abort()
    
    def pause(self):
        """Simmilar to TCP_CORK"""
        self.transport.pause()
        
    def resume(self):
        self.transport.resume()
        
    def _unpause(self):
        """Called by start_response to indicate that the headers have been written and that data can now
        be submitted for writing to the socket
        
        Note: this is diffrent to the pause and unpause methods that are useful for 'bunching' up lots
        of small write requests into one larger one to reduce overhead
        """
        self._paused = False
    
    def _flush(self):
        for obj in self._buffer:
            if isinstance(obj, bytes):
                self.transport.write(obj)
            elif isisntance(obj, io.IOBase):
                # _pause should be false by now, so sendfile whould do what we want
                self.sendfile(obj)
            else:
                raise ValueError("Unknown datatype in buffer (did you encode all text?): {}".format(obj))
        self._buffer = []
    
    def write(self, data):
        if self._paused:
            self._buffer.append(data)
        else:
            self.transport.write(data)
            
    def writelines(self, lines):
        if self._paused:
            self._buffer += lines
        else:
            self.transport.writelines(lines)
            
    def sendfile(self, file, chunk_size=io.DEFAULT_BUFFER_SIZE):
        if not isintance(file, file):
            file = open(file, 'rb')
        
        if self._paused:
            self._buffer.append(file)
        else:
            buf = file.read(chunk_size)
            while len(buf) != 0:
                self.transport.write(buf)
                buf = file.read(chunk_size)
                
        
    def clear(self):
        """clear the contents of the buffer and headers, for apps that do everything rather than rely on midleware
        allows them to zero the buffers contents before sending an error page if an exception was raised during
        rendering of the page
        """
        self.headers = []
        self._buffer = []
