#!/usr/bin/env python

import logging
import os
import sys

os.sys.path[0:0] = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
]

import mushroom

from example_utils import ExampleServer


SERVER_HOST = '127.0.0.1'
SERVER_PORT = 39288 # picked by random.randint(1024, 65535)


class PingServer(ExampleServer):

    def __init__(self, listener):
        super(PingServer, self).__init__(listener,
                'ping.html',
                mushroom.MethodDispatcher(self, 'rpc_'))

    def rpc_ping(self, request):
        return 'pong'


def runserver(listener):
    server = PingServer(listener)
    server.serve_forever()


if __name__ == '__main__':
    logging.basicConfig()
    listener = (SERVER_HOST, SERVER_PORT)
    print 'Server running at %s:%d' % listener
    runserver(listener)
