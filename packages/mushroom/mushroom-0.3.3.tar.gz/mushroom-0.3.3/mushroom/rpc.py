from itertools import count
import logging

import gevent
from gevent.event import Event


logger = logging.getLogger('mushroom.rpc')


class RpcError(RuntimeError):
    pass


class MethodNotFound(RpcError):
    pass


class RequestTimeout(RpcError):
    pass


class RequestException(RpcError):

    def __init__(self, data):
        super(RequestException, self).__init__()
        self.data = data


class MethodDispatcher(object):

    def __init__(self, obj, prefix='rpc_'):
        self.obj = obj
        self.prefix = prefix

    def __call__(self, request):
        method_name = self.prefix + request.method
        try:
            method = getattr(self.obj, method_name)
        except AttributeError:
            raise MethodNotFound(method_name)
        return method(request)


def dummy_rpc_handler(request):
    '''
    Dummy RPC handler that raises a MethodNotFound exception for
    all calls. This is useful for applications that do not need do
    receive any data from the client but only publish data.
    '''
    raise MethodNotFound(request.method)


class Engine(object):
    '''Transport neutral message factory and mapper between requests and
    responses.'''

    def __init__(self, transport, rpc_handler):
        # Transport for sending and receiving messages
        self.transport = transport
        # Bind transport to the engine
        assert transport.rpc_engine is None, \
                'transport already bound to another rpc engine'
        transport.rpc_engine = self
        # Handler for inbound requests and notifications
        self.rpc_handler = rpc_handler
        # Generator for outbount message ids
        self.message_id_generator = count()
        # Dictionary for mapping outbound requests to inbound responses
        self.requests = {}

    def next_message_id(self):
        '''Generate the next message id for outbound messages.'''
        return self.message_id_generator.next()

    def notify(self, method, data=None, **kwargs):
        '''Send a notification.'''
        message = Notification(method, data, message_id=self.next_message_id())
        self.send(message, **kwargs)

    def request(self, method, data=None, timeout=None, **kwargs):
        '''Send a request and wait for the response or timeout.'''
        request = Request(method, data, message_id=self.next_message_id())
        self.requests[request.message_id] = request
        self.send(request, **kwargs)
        response = request.get_response(timeout)
        if isinstance(response, Response):
            return response.data
        elif isinstance(response, Error):
            raise RequestException(response.data)

    def send(self, message, **kwargs):
        '''Hand message over to the transport.'''
        self.transport.send(message, **kwargs)

    def handle_message(self, message):
        '''Handle message received from the transport.'''
        if isinstance(message, Notification):
            # Spawn worker to process the notification. The response of
            # the worker is ignored.
            def worker():
                try:
                    self.rpc_handler(message)
                except MethodNotFound, e:
                    logger.warning('MethodNotFound: %s' % e.message)
                except RpcError, e:
                    logger.debug(e, exc_info=True)
                except Exception, e:
                    logger.exception(e)
            gevent.spawn(worker)
        elif isinstance(message, Request):
            # Spawn worker which waits for the response of the rpc handler
            # and sends the response message.
            def worker():
                try:
                    response_data = self.rpc_handler(message)
                except MethodNotFound, e:
                    logger.warning('MethodNotFound: %s' % e.message)
                    self.send(Error(message, e.message,
                        message_id=self.next_message_id()))
                except RpcError, e:
                    logger.debug(e, exc_info=True)
                    self.send(Error(message, e.message,
                        message_id=self.next_message_id()))
                except Exception, e:
                    logger.exception(e)
                    self.send(Error(message, 'Internal server error',
                        message_id=self.next_message_id()))
                else:
                    self.send(Response(message, response_data,
                        message_id=self.next_message_id()))
            gevent.spawn(worker)
        elif isinstance(message, (Response, Error)):
            # Find request according to response or error.
            try:
                request = self.requests.pop(message.request)
            except KeyError:
                logger.error('Response for unknown request message id: %r' %
                        message.request)
                return
            request.response = message
        else:
            raise RuntimeError('Unsupported message type: %s' % type(message))


class Message(object):

    @staticmethod
    def from_list(l):
        if not isinstance(l, (list, tuple)):
            raise ValueError('Message is not encoded as list or tuple')
        try:
            message_class = MESSAGE_CLASS_BY_CODE[l[0]]
        except KeyError:
            raise ValueError('Unsupported message code: %r' % l[0])
        message = message_class.from_list(l)
        return message


class Heartbeat(Message):
    code = 0

    def __init__(self, last_message_id):
        self.last_message_id = last_message_id

    @staticmethod
    def from_list(l):
        self = Heartbeat(l[1])
        return self


class Notification(Message):
    code = 1
    message_id = None

    def __init__(self, method, data=None, message_id=None):
        self.method = method
        self.data = data
        self.message_id = message_id

    @staticmethod
    def from_list(l):
        self = Notification(l[2], l[3], message_id=l[1])
        return self

    def to_list(self):
        return [self.code, self.message_id, self.method, self.data]


class Request(Message):
    code = 2
    message_id = None

    def __init__(self, method, data=None, message_id=None):
        self.method = method
        self.data = data
        self.message_id = message_id
        self._response = None
        self.complete = Event()

    def to_list(self):
        return [self.code, self.message_id, self.method, self.data]

    @staticmethod
    def from_list(l):
        self = Request(l[2], l[3], message_id=l[1])
        return self

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, response):
        assert not self._response
        self._response = response
        self.complete.set()

    def get_response(self, timeout=None):
        if self.complete.wait(timeout):
            return self.response
        else:
            raise RequestTimeout


class Response(Message):
    code = 3
    message_id = None

    def __init__(self, request, data, message_id=None):
        self.request = request
        self.data = data
        self.message_id = message_id

    @staticmethod
    def from_list(l):
        self = Response(l[2], l[3], message_id=l[1])
        return self

    def to_list(self):
        return [self.code, self.message_id, self.request.message_id, self.data]


class Error(Message):
    code = 4
    message_id = None

    def __init__(self, request, data, message_id=None):
        self.request = request
        self.data = data
        self.message_id = message_id

    @staticmethod
    def from_list(l):
        self = Error(l[2], l[3], message_id=l[1])
        return self

    def to_list(self):
        return [self.code, self.message_id, self.request.message_id, self.data]


class Disconnect(Message):
    code = -1

    @staticmethod
    def from_list(l):
        self = Disconnect()
        return self


MESSAGE_CLASS_BY_CODE = {
    Heartbeat.code: Heartbeat,
    Notification.code: Notification,
    Request.code: Request,
    Response.code: Response,
    Error.code: Error,
    Disconnect.code: Disconnect
}
