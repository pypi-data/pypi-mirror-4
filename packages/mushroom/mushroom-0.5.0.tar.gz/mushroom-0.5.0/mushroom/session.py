from itertools import count
import random
import string
from time import time

import gevent
from gevent.event import Event
try:
    import simplejson as json
except ImportError:
    import json

from mushroom.rpc import Engine as RpcEngine


POLL_TIMEOUT = 40
SESSION_CLEANUP_INTERVAL = 30
SESSION_MAX_AGE = 60


def session_id_generator():
    alpha_numerics = string.ascii_letters + string.digits
    while True:
        '''A UUID has 16 bytes and therefore 256^16 possibilities. For the
        shortest possible id which consists only of URL safe characters we
        pick only alpha numeric characters (2*26+10) and make it 22
        characters long. This is at least as good as a hex encoded UUID
        which would require 32 characters.'''
        yield ''.join(random.choice(alpha_numerics) for _ in xrange(22))


class Session(object):

    def __init__(self, id, transport, rpc_handler):
        self.id = id
        self.transport = transport
        self.rpc_engine = RpcEngine(transport, rpc_handler)

    def notify(self, *args, **kwargs):
        '''
        Send a notification to the connected client.

        This method is just a wrapper for the
        :func:`mushroom.rpc.Engine.request` method and uses the
        same arguments.
        '''
        self.rpc_engine.notify(*args, **kwargs)

    def request(self, *args, **kwargs):
        '''
        Send a request to the connected client.

        This method is just a wrapper for the
        :func:`mushroom.rpc.Engine.notify` method and uses the
        same arguments.
        '''
        self.rpc_engine.request(*args, **kwargs)


class SessionList(object):

    def __init__(self):
        self.sessions = {}

    def add(self, session):
        if session.id in self.sessions:
            raise KeyError('Duplicate session id %r' % session.id)
        self.sessions[session.id] = session

    def remove(self, session):
        del self.sessions[session.id]

    def notify(self, method, data=None):
        for session in self.sessions.itervalues():
            session.notify(method, data)

    def __getitem__(self, sid):
        return self.sessions[sid]

    def __iter__(self):
        return self.sessions.itervalues()

    def __len__(self):
        return len(self.sessions)


class SessionHandler(object):

    def authenticate(self, session, auth):
        return True

    def connect(self, session):
        pass

    def disconnect(self, session):
        pass


class SessionHandlerAdapter(object):

    def __init__(self, obj, prefix='session_', suffix=''):
        self.obj = obj
        self.prefix = prefix
        self.suffix = suffix

    def __getattr__(self, name):
        return getattr(self.obj, self.prefix + name + self.suffix)
