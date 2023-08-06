'''
Usage: sslexport CERTFILE BIND_IP PORT [PORT...]
'''
import sys
import gevent.server
import gevent.socket

def main():
    certfile = sys.argv[1]
    bind_ip = sys.argv[2]
    ports_to_forward = map(int, sys.argv[3:])
    for port in ports_to_forward:
        print 'Forward %s:%s to localhost:%s' % (bind_ip, port, port)
        server = gevent.server.StreamServer(
            (bind_ip, port),
            Forwarder(port),
            certfile=certfile)
        server.start()
    while True:
        gevent.sleep(10)
        print '--- mark ---'

class Forwarder(object):

    def __init__(self, port):
        self.port = port

    def __call__(self, socket, addr):
        local_sock = gevent.socket.socket()
        local_sock.connect(('127.0.0.1', self.port))
        gevent.spawn(forward_data, socket, local_sock)
        gevent.spawn(forward_data, local_sock, socket)

def forward_data(s0, s1):
    while True:
        buf = s0.recv(4096)
        if not buf: break
        s1.sendall(buf)
        
        

if __name__ == '__main__':
    main()
