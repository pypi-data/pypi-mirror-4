import logging

from gevent.pywsgi import WSGIServer
from mushroom.exceptions import HttpError, HttpMethodNotAllowed, \
        HttpNotFound, HttpUnauthorized, HttpInternalServerError, \
        HttpNotImplemented
from mushroom.http import HttpRequest, HttpResponse, JsonResponse, \
        WebSocketTransport, PollTransport
from mushroom.rpc import Message, dummy_rpc_handler
from mushroom.session import session_id_generator, Session, SessionList


logger = logging.getLogger('mushroom.application')


class Application(object):

    def __init__(self, rpc_handler=None, auth_handler=None, disconnect_handler=None):
        self.sessions = SessionList()
        self.sid_generator = session_id_generator()
        self.rpc_handler = rpc_handler or dummy_rpc_handler
        self.auth_handler = auth_handler
        self.disconnect_handler = disconnect_handler

    def __call__(self, environ, start_response):
        try:
            try:
                request = HttpRequest(environ)
                response = self.request(request)
            except Exception, e:
                if isinstance(e, HttpError):
                    raise
                else:
                    logger.exception(e)
                    raise HttpInternalServerError
        except HttpError, e:
            response = HttpResponse(e.code, e.message, extra_headers=e.headers)
        # If the connection has switched to the WebSocket protocol no
        # response is expected. In this case the WSGI application simply
        # needs to returns None.
        if response:
            start_response(response.code, response.headers.iteritems())
            return [response.content]

    def request(self, request):
        # / -> Authentication and connection boostrapping
        if not request.path:
            return self.bootstrap(request)
        # /.*/
        if len(request.path) == 1:
            try:
                sid = request.path[0]
                session = self.sessions[sid]
            except KeyError:
                raise HttpNotFound
            return session.transport.handle_http_request(request, session)
        raise HttpNotFound

    def bootstrap(self, request):
        # Only allow POST requests for bootstrapping
        if request.method != 'POST':
            raise HttpMethodNotAllowed(['POST'])
        for transport in request.data['transports']:
            if transport == 'ws':
                return self.start_session(request, WebSocketTransport())
            if transport == 'poll':
                return self.start_session(request, PollTransport())
        # No suitable transport found
        raise HttpNotImplemented('No suitable transport found')

    def start_session(self, request, transport):
        session = Session(self.sid_generator.next(), transport, self.rpc_handler)
        if self.auth_handler:
            if not self.auth_handler(session, request.data.get('auth', None)):
                raise HttpUnauthorized
        self.sessions.add(session)
        return JsonResponse(session.get_handshake_data(request))
