#!/usr/bin/env python

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
