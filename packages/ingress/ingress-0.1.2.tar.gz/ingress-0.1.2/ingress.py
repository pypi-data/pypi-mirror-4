#!/usr/bin/env python
'''A 'backdoor' shell for running servers (very much like Twisted manhole).

Once installed, you can 'telnet <host> <port>' and run Python commands on your
server environment. This is very helpful in debugging servers.

This one uses only modules found in the standard library.
'''

__author__ = 'Miki Tebeka <miki.tebeka@gmail.com>'
__version__ = '0.1.2'

from SocketServer import StreamRequestHandler, TCPServer, ThreadingMixIn
from threading import Thread
from traceback import print_exc
import socket

EOF = chr(4)

class PyHandler(StreamRequestHandler):
    password = None
    env = {}

    def handle(self):
        env = self.env.copy()
        self.wfile.write('Welcome to ingress (type "exit()" to exit)\n')

        if not self.login():
            return

        while True:
            try:
                self.wfile.write('>>> ')
                expr = self.rfile.readline().rstrip()
                if expr == EOF:
                    return
                try:
                    value = eval(expr, globals(), env)
                    self.wfile.write(format(value) + '\n')
                except:
                    exec expr in env
            except (EOFError, SystemExit, socket.error):
                return
            except Exception:
                print_exc(file=self.wfile)

    def finish(self):
        try:
            StreamRequestHandler.finish(self)
        except socket.error:
            pass

    def login(self):
        if not self.password:
            return True

        for i in range(3):
            self.wfile.write('Password: ')
            password = self.rfile.readline().strip()
            if password == self.password:
                return True
            self.wfile.write('Bad password\n')

        return False


class ThreadedServer(ThreadingMixIn, TCPServer):
    daemon_threads = True
    allow_reuse_address = True

def server_thread(env, port, password=None):
    # Create a new handler class for this with it's own env
    class Handler(PyHandler):
        pass
    Handler.env = env
    Handler.password = password

    server = ThreadedServer(('localhost', port), Handler)
    server.serve_forever()

DEFAULT_PORT = 9998
def install(env=None, port=DEFAULT_PORT, password=None):
    env = env or {}
    t = Thread(target=server_thread, args=(env, port, password))
    t.daemon = True
    t.start()

    return t

def main(argv=None):
    import sys
    from argparse import ArgumentParser

    argv = argv or sys.argv

    parser = ArgumentParser(description='Run demo server.')
    parser.add_argument('-p', '--port', help='port to listen',
                        default=DEFAULT_PORT)
    parser.add_argument('-l', '--login', help='login password',
                        default=None)
    args = parser.parse_args(argv[1:])

    t = install(port=args.port, password=args.login)
    print('Serving on port {0}'.format(args.port))
    t.join()


if __name__ == '__main__':
    main()

