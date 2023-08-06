try:
    import simplejson as json
except:
    import json

from gevent.event import Event

from mushroom.rpc import Disconnect
from mushroom.rpc import Message
from mushroom.rpc import Heartbeat
from mushroom.transport import UnreliableTransport


class HttpError(RuntimeError):
    code = ''
    message = ''
    headers = {}

    def __init__(self, message=None):
        self.message = message or self.message
        super(HttpError, self).__init__(self.message)


class HttpUnauthorized(HttpError):
    code = '401 Unauthorized'
    def __init__(self, auth_scheme=None):
        if not auth_scheme:
            auth_scheme = 'Mushroom'
        self.headers = [
            ('WWW-Authenticate', auth_scheme)
        ]
        super(HttpUnauthorized, self).__init__()


class HttpNotFound(HttpError):
    code = '404 Not Found'


class HttpMethodNotAllowed(HttpError):
    code = '405 Method Not Allowed'
    def __init__(self, allowed_methods):
        self.headers = [
            ('Allow', ', '.join(method.upper() for method in allowed_methods))
        ]
        super(HttpMethodNotAllowed, self).__init__()


class HttpInternalServerError(HttpError):
    code = '500 Internal Server Error'


class HttpNotImplemented(HttpError):
    code = '501 Not Implemented'


class HttpRequest(object):

    def __init__(self, environ):
        # FIXME add validation
        self.environ = environ
        self.method = environ['REQUEST_METHOD']
        self.raw_data = environ['wsgi.input'].read()
        if self.raw_data:
            self.data = json.loads(self.raw_data)
        else:
            self.data = None
        # Convert path to list of atoms
        self.path = filter(bool, environ['PATH_INFO'].split('/'))


class HttpResponse(object):

    def __init__(self, code='200 OK', content='', extra_headers=None):
        self.code = code
        self.content = content
        self.headers = {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'text/plain',
        }
        self.headers.update(extra_headers or {})


class JsonResponse(HttpResponse):

    def __init__(self, data):
        super(JsonResponse, self).__init__(
            content=json.dumps(data),
            extra_headers={
                'Content-Type': 'application/json',
            }
        )


class HttpTransport(UnreliableTransport):

    def get_url(self, protocol, request, session):
        host = request.environ['HTTP_HOST']
        return '%s://%s/%s/' % (protocol, host, session.id)

    def handle_http_request(self, request, session):
        self.remote_addr = request.environ.get('REMOTE_ADDR', None)


class PollTransport(HttpTransport):

    name = 'poll'
    timeout = 40

    def __init__(self):
        super(PollTransport, self).__init__()
        self.messages_ready = Event()

    def get_handshake_data(self, request, session):
        protocol = 'http' # XXX autodetect
        return {
            'transport': self.name,
            'url': self.get_url(protocol, request, session)
        }

    def handle_http_request(self, request, session):
        super(PollTransport, self).handle_http_request(request, session)
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

    def handle_disconnect(self, reconnect=False):
        if not reconnect:
            self.send(Disconnect())
        super(PollTransport, self).handle_disconnect(reconnect=reconnect)

    def real_send(self, message):
        self.messages_ready.set()


class WebSocketTransport(HttpTransport):

    name = 'ws'

    def __init__(self):
        super(WebSocketTransport, self).__init__()
        self.ws = None

    def get_handshake_data(self, request, session):
        protocol = 'ws' # XXX autodetect
        return {
            'transport': self.name,
            'url': self.get_url(protocol, request, session)
        }

    def handle_http_request(self, request, session):
        super(WebSocketTransport, self).handle_http_request(request, session)
        assert not self.ws
        self.ws = request.environ['wsgi.websocket']
        self.handle_connect()
        # Process incoming messages
        try:
            while self.ws is not None:
                frame = self.ws.receive()
                if frame is None:
                    # Disconnect
                    return
                message_data = json.loads(frame)
                message = Message.from_list(message_data)
                message.session = session
                self.handle_message(message)
        finally:
            if self.state() == 'CONNECTED':
                # WebSocket was closed unexpectedly.
                self.handle_disconnect()

    def handle_disconnect(self):
        self.ws = None
        super(WebSocketTransport, self).handle_disconnect()

    def real_send(self, message):
        message_data = message.to_list()
        frame = json.dumps(message_data)
        # FIXME this can fail if the websocket goes down
        self.ws.send(frame)
