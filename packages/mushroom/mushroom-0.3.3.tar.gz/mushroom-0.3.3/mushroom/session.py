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

from mushroom.http import JsonResponse
from mushroom.rpc import Engine as RpcEngine
from mushroom.rpc import Message
from mushroom.rpc import Heartbeat
from mushroom.rpc import Request
from mushroom.rpc import Notification
from mushroom.transport import UnreliableTransport


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


class Session(RpcEngine):

    def __init__(self, id, transport, rpc_handler):
        self.id = id
        super(Session, self).__init__(transport, rpc_handler)

    def get_handshake_data(self, request):
        return self.transport.get_handshake_data(request)

    def handle_disconnect(self):
        # FIXME make sure the session is removed from the session list
        pass



class HttpTransport(UnreliableTransport):

    def get_url(self, request, protocol):
        host = request.environ['HTTP_HOST']
        return '%s://%s/%s/' % (protocol, host, self.rpc_engine.id)


class PollTransport(HttpTransport):

    timeout = 40

    def __init__(self):
        super(PollTransport, self).__init__()
        self.messages_ready = Event()

    def get_handshake_data(self, request):
        protocol = 'http' # XXX autodetect
        return {
            'transport': 'poll',
            'url': self.get_url(request, protocol)
        }

    def handle_http_request(self, request, session):
        # Only allow POST requests for polling
        if request.method != 'POST':
            raise HttpMethodNotAllowed(['POST'])
        assert isinstance(request.data, list)
        heartbeat = None
        for message_data in request.data:
            message = Message.from_list(message_data)
            message.session = session
            self.handle_message(message)
            if isinstance(message, Heartbeat):
                heartbeat = message
        if heartbeat:
            self.handle_connect()
            self.messages_ready.wait(self.timeout)
            self.messages_ready.clear()
            self.handle_disconnect(reconnect=True)
            return JsonResponse([
                message.to_list()
                for message in self.messages
            ])
        else:
            return JsonResponse(None)

    def real_send(self, message):
        self.messages_ready.set()


class WebSocketTransport(HttpTransport):

    def __init__(self):
        super(WebSocketTransport, self).__init__()
        self.ws = None

    def get_handshake_data(self, request):
        protocol = 'ws' # XXX autodetect
        return {
            'transport': 'ws',
            'url': self.get_url(request, protocol)
        }

    def handle_http_request(self, request, session):
        assert not self.ws
        self.ws = request.environ['wsgi.websocket']
        self.handle_connect()
        # Process incoming messages
        try:
            while True:
                frame = self.ws.receive()
                if frame is None:
                    # Disconnect
                    return
                message_data = json.loads(frame)
                message = Message.from_list(message_data)
                message.session = session
                self.handle_message(message)
        finally:
            self.handle_disconnect()

    def handle_disconnect(self):
        self.ws = None
        super(WebSocketTransport, self).handle_disconnect()

    def real_send(self, message):
        message_data = message.to_list()
        frame = json.dumps(message_data)
        # FIXME this can fail if the websocket goes down
        self.ws.send(frame)


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
