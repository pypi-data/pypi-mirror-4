#!/usr/bin/env python

from __future__ import print_function

import cmd
import logging
import os
import shlex
import sys

from gevent import monkey

os.sys.path[0:0] = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
]

import mushroom
from mushroom.geventfd import GeventFD

#sys.stdout = geventfd.GeventFD(sys.stdout)
#sys.stderr = geventfd.GeventFD(sys.stderr)
sys.stdin = GeventFD(sys.stdin)

from example_utils import ExampleServer


class RemoteControlCmd(cmd.Cmd):

    prompt = 'remote-control> '
    intro = 'Interactive browser remote control\nType "help" for more information.'
    use_rawinput = False

    def __init__(self, server):
        cmd.Cmd.__init__(self)
        self.server = server

    def postcmd(self, stop, line):
        if stop == 'EOF':
            print('^D')
        if stop:
            print('May the maltron be with you!')
            return True

    def do_help(self, args):
        '''Type "help" for the list of available commands and help <command>" for details about a specific command.'''
        cmd.Cmd.do_help(self, args)

    def do_exit(self, args):
        '''Exit the console.'''
        return 'exit'

    def do_eval(self, args):
        '''Call eval() on the browser.'''
        self.server.sessions.notify('eval', args)

    def do_print(self, args):
        '''Call print() on the browser.'''
        self.server.sessions.notify('print', args)

    def do_alert(self, args):
        '''Call alert() on the browser.'''
        self.server.sessions.notify('alert', args)

    def do_EOF(self, args):
        '''You can exit the console by typing Ctrl+D.'''
        return 'EOF'

    def do_who(self, args):
        '''Show connected users'''
        if not self.server.sessions:
            print('No sessions connected.')
            return
        print('%d session%s connected:' % (
            len(self.server.sessions),
            's' if len(self.server.sessions) != 1 else ''))
        print('SESSION ID              IP ADDRESS       TRANSPORT')
        print('--------------------------------------------------')
        #####('xxxxxxxxxxxxxxxxxxxxxx  000.000.000.000  ws/poll  ')
        for session in self.server.sessions:
            print('%-22s  %-15s  %-9s' % (session.id,
                session.transport.remote_addr, session.transport.name))

    def do_gauge(self, args):
        '''Set gauge value'''
        self.server.sessions.notify('gauge', args)


SERVER_HOST = '127.0.0.1'
SERVER_PORT = 39288 # picked by random.randint(1024, 65535)


class RemoteControlServer(ExampleServer):

    def __init__(self, listener):
        super(RemoteControlServer, self).__init__(listener,
                'remote-control.html',
                mushroom.MethodDispatcher(self, 'rpc_'),
                log=None)


if __name__ == '__main__':
    logging.basicConfig(filename='remote-control.log', level=logging.DEBUG)
    listener = (SERVER_HOST, SERVER_PORT)
    print('Server running at %s:%d' % listener)
    server = RemoteControlServer(listener)
    server.start()
    rccmd = RemoteControlCmd(server)
    rccmd.cmdloop()
    # XXX how to shutdown cleanly?
