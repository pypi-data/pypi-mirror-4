#!/usr/bin/env python
from .protocols import HTTPServerProtocol
from .process import ProcessManager
from tulip.tasks import task
import tulip
import sys


def start_server(app, addr, manager=None, transport=HTTPServerProtocol, **kwargs):
    """Returns the listening socket so we can do things like add more flags to it"""
    loop = tulip.get_event_loop()

    if manager:
        servlet = lambda: manager.register(transport(app))
    else:
        servlet = lambda: transport(app)
        
    server = loop.start_serving(servlet, *addr, **kwargs)
    loop.run_until_complete(server)

def add_shutdown_handler(manager=None):
    import signal

    def sigint_handler():
        print("Recived SIGINT, Exiting gracefully")
        if manager:
            manager.shutdown()
        sys.exit(0)
        
    loop = tulip.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, sigint_handler)


@task
def dummy_app(transport, method, path, protocol, headers, body):
    transport.write(b'HTTP/1.1 200 OK\r\ncontent-type: text/plain\r\n\r\n')
    method = method.decode('utf-8')
    path = path.decode('utf-8')
    protocol = protocol.decode('utf-8')
    transport.write("Protocol: {} {} {}:\n".format(method, path, protocol).encode('utf-8'))
    transport.write("Headers:\n".encode('utf-8'))
    for key, val in headers:
        key = key.decode('utf-8')
        val = val.decode('utf-8')
        line = "{:<20}{}\n".format(key + ":", val)
        transport.write(line.encode('utf-8'))
    transport.close()

def tulip_server(argv=sys.argv[1:]):
    loop = tulip.get_event_loop()

    manager = ProcessManager()
    start_server(dummy_app, ('localhost', 8080), manager)
    sock = add_shutdown_handler(manager)

#    print('Listening on {}:{}'.format(*sock.getsockname()))
    loop.run_forever()
    
if __name__ == "__main__":
    tulip_server()
