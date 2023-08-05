from tests import LimitedTestCase, certificate_file, private_key_file
from tests import skip_if_no_ssl
from unittest import main
import eventlet
from eventlet import util, coros, greenio
import socket
import os

def listen_ssl_socket(address=('127.0.0.1', 0)):
    sock = util.wrap_ssl(socket.socket(), certificate_file,
          private_key_file, True)
    sock.bind(address)
    sock.listen(50)

    return sock
   

class SSLTest(LimitedTestCase):
    @skip_if_no_ssl
    def test_duplex_response(self):
        def serve(listener):
            sock, addr = listener.accept()
            stuff = sock.read(8192)
            sock.write('response')

        sock = listen_ssl_socket()

        server_coro = eventlet.spawn(serve, sock)
        
        client = util.wrap_ssl(eventlet.connect(('127.0.0.1', sock.getsockname()[1])))
        client.write('line 1\r\nline 2\r\n\r\n')
        self.assertEquals(client.read(8192), 'response')
        server_coro.wait()
        
    @skip_if_no_ssl
    def test_ssl_close(self):
        def serve(listener):
            sock, addr = listener.accept()
            stuff = sock.read(8192)
            try:
                self.assertEquals("", sock.read(8192))
            except greenio.SSL.ZeroReturnError:
                pass
  
        sock = listen_ssl_socket()

        server_coro = eventlet.spawn(serve, sock)
        
        raw_client = eventlet.connect(('127.0.0.1', sock.getsockname()[1]))
        client = util.wrap_ssl(raw_client)
        client.write('X')
        greenio.shutdown_safe(client)
        client.close()
        server_coro.wait()
        
    @skip_if_no_ssl
    def test_ssl_connect(self):
        def serve(listener):
            sock, addr = listener.accept()
            stuff = sock.read(8192)
        sock = listen_ssl_socket()
        server_coro = eventlet.spawn(serve, sock)
        
        raw_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_client = util.wrap_ssl(raw_client)
        ssl_client.connect(('127.0.0.1', sock.getsockname()[1]))
        ssl_client.write('abc')
        greenio.shutdown_safe(ssl_client)
        ssl_client.close()
        server_coro.wait()

    @skip_if_no_ssl
    def test_ssl_unwrap(self):
        def serve():
            sock, addr = listener.accept()
            self.assertEquals(sock.recv(6), 'before')
            sock_ssl = util.wrap_ssl(sock, certificate_file, private_key_file,
                                     server_side=True)
            sock_ssl.do_handshake()
            self.assertEquals(sock_ssl.read(6), 'during')
            sock2 = sock_ssl.unwrap()
            self.assertEquals(sock2.recv(5), 'after')
            sock2.close()

        listener = eventlet.listen(('127.0.0.1', 0))
        server_coro = eventlet.spawn(serve)
        client = eventlet.connect((listener.getsockname()))
        client.send('before')
        client_ssl = util.wrap_ssl(client)
        client_ssl.do_handshake()
        client_ssl.write('during')
        client2 = client_ssl.unwrap()
        client2.send('after')
        server_coro.wait()

class SocketSSLTest(LimitedTestCase):
    @skip_if_no_ssl
    def test_greensslobject(self):
        import warnings
        # disabling socket.ssl warnings because we're testing it here
        warnings.filterwarnings(action = 'ignore',
                        message='.*socket.ssl.*',
                        category=DeprecationWarning)

        def serve(listener):
            sock, addr = listener.accept()
            sock.write('content')
            greenio.shutdown_safe(sock)
            sock.close()
        listener = listen_ssl_socket(('', 0))
        killer = eventlet.spawn(serve, listener)
        from eventlet.green.socket import ssl
        client = ssl(eventlet.connect(('localhost', listener.getsockname()[1])))
        self.assertEquals(client.read(1024), 'content')
        self.assertEquals(client.read(1024), '')

        
if __name__ == '__main__':
    main()
