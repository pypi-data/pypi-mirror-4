'''
Usage: sslexport configfile
'''
import sys
import gevent.server
import gevent.socket
from ConfigParser import ConfigParser

def main():
    cp = ConfigParser()
    cp.read(sys.argv[1])
    certfile = cp.get('sslexport', 'pemfile')
    external = cp.get('sslexport', 'external')
    internal = '127.0.0.1'

    # External (SSL) listeners
    for ext_port in cp.options('sslexport.server'):
        ipport = cp.get('sslexport.server', ext_port)
        ip,port = ipport.split(':')
        server = gevent.server.StreamServer(
            (external, int(ext_port)),
            Forwarder(ip, port, gevent.socket.socket),
            certfile=certfile)
        server.start()
        print 'ssl(%s:%s) => clear(%s:%s)' % (
            external, ext_port, ip, port)

    # Internal (non-SSL) listeners
    for int_port in cp.options('sslexport.client'):
        ipport = cp.get('sslexport.client', int_port)
        ip,port = ipport.split(':')
        server = gevent.server.StreamServer(
            (internal, int(int_port)),
            Forwarder(ip, port, lambda:gevent.ssl.SSLSocket(gevent.socket.socket())),
            certfile=certfile)
        server.start()
        print 'clear(%s:%s) => ssl(%s:%s)' % (
            internal, int_port, ip, port)

    while True:
        gevent.sleep(10)
        print '--- mark ---'

class Forwarder(object):

    def __init__(self, ip, port, socket_factory):
        self.ip = ip
        self.port = int(port)
        self.socket_factory = socket_factory

    def __call__(self, socket, addr):
        local_sock = self.socket_factory()
        local_sock.connect((self.ip, self.port))
        gevent.spawn(forward_data, socket, local_sock)
        gevent.spawn(forward_data, local_sock, socket)

def forward_data(s0, s1):
    while True:
        buf = s0.recv(4096)
        if not buf: break
        s1.sendall(buf)
        
        

if __name__ == '__main__':
    main()
