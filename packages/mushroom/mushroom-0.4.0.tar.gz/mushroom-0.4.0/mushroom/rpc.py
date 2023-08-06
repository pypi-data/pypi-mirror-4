from itertools import count
import logging

import gevent
from gevent.event import AsyncResult


logger = logging.getLogger('mushroom.rpc')


class RpcError(RuntimeError):
    '''
    Base class for all exceptions raised from by the RpcEngine.
    '''


class MethodNotFound(RpcError):
    '''
    This error is raised when a method for a `Request` or `Notification`
    message is not found. This can either happen when a connected client
    tries to call a server method or the server tries to call a method
    on the client side.
    '''
    pass


class RequestTimeout(RpcError):
    '''
    This error is raised when a `Request` message is not answered within
    a specified timeout value. By default the value is set to infinite
    can be set do a different value when making the request.
    '''
    pass


class RequestException(RpcError):
    '''
    This exception is raised when a `Request` message is answered with
    an `Error` message.
    '''

    def __init__(self, data):
        super(RequestException, self).__init__()
        self.data = data


class MethodDispatcher(object):
    '''
    Dispatcher implementation that calls methods on an object with a
    specific prefix and/or suffix. This makes it possible to define
    objects that provides a set of methods which can then be called by
    the client.

    Note: Using an empty prefix, '_' or '__' is highly discouraged as
    it allows the client to call methods like methods like `__del__`.
    The same holds true for the suffix. If you really want to dispatch
    methods without a prefix or suffix it is a good idea to write a
    custom dispatcher that implements some checks for this.
    '''

    def __init__(self, obj, prefix='rpc_', suffix=''):
        '''
        Constructor for the method dispatcher.

        Keyword arguments:
        obj -- object instance which is used for the method lookup
        prefix -- string prefix which is prepended to the method name
            when looking up the method
        suffix -- string suffix which is appended to the method name
            when looking up the method
        '''
        self.obj = obj
        self.prefix = prefix
        self.suffix = suffix

    def __call__(self, request):
        '''
        The `RpcEngine` calls the request handler like it was a function
        that takes the request as sole argument and returns the response.
        This function implements the adapter for this interface and makes
        it possible to use this class as `handler` for the `RpcEngine`.

        Keyword arguments:
        request -- request object
        '''
        method_name = self.prefix + request.method + self.suffix
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
    '''
    Transport neutral message factory and mapper between requests and
    responses. This is the heart of all RPC handling.
    '''

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
        '''
        Generate the next message id for outbound messages.

        Returns: the next message id
        '''
        return self.message_id_generator.next()

    def notify(self, method, data=None, **kwargs):
        '''Send a notification.

        Keyword arguments:
        method -- name of the method to be called
        data -- data for the method being called
        kwargs -- transport specific arguments
        '''
        message = Notification(self.next_message_id(), method, data)
        self.send(message, **kwargs)

    def request(self, method, data=None, timeout=None, **kwargs):
        '''
        Send a request and wait for the response or timeout. If no response
        for the given method is received within `timeout` seconds a
        `RequestTimeout` exception is raised.

        Keyword arguments:
        method -- name of the method to be called
        data -- data for the method being called
        timeout -- timeout in seconds for this request
        kwargs -- transport specific arguments
        '''
        request = Request(self.next_message_id(), method, data)
        self.requests[request.message_id] = request
        self.send(request, **kwargs)
        try:
            response = request.get_response(timeout=timeout)
        except gevent.Timeout:
            raise RequestTimeout
        if isinstance(response, Response):
            return response.data
        elif isinstance(response, Error):
            raise RequestException(response.data)
        else:
            raise RuntimeError('Unexpected type of response: %s' % type(response))

    def send(self, message, **kwargs):
        '''
        Hand message over to the transport.

        Keyword arguments:
        message -- message to be sent
        kwargs -- transport specific arguments
        '''
        self.transport.send(message, **kwargs)

    def handle_message(self, message):
        '''
        Handle message received from the transport.

        Keyword arguments:
        message -- message to be handled
        '''
        if isinstance(message, Heartbeat):
            # FIXME acknowledge messages
            pass
        elif isinstance(message, Notification):
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
                    self.send(Error.for_request(self.next_message_id(),
                        message, e.message))
                except RpcError, e:
                    logger.debug(e, exc_info=True)
                    self.send(Error.for_request(self.next_message_id(),
                        message, e.message))
                except Exception, e:
                    logger.exception(e)
                    self.send(Error.for_request(self.next_message_id(),
                        message, 'Internal server error'))
                else:
                    self.send(Response.for_request(self.next_message_id(),
                        message, response_data))
            gevent.spawn(worker)
        elif isinstance(message, (Response, Error)):
            # Find request according to response or log an error.
            try:
                message.request = self.requests.pop(message.request_message_id)
            except KeyError:
                logger.error('Response for unknown request message id: %r' %
                        message.request_message_id)
                return
            message.request.response = message
        elif isinstance(message, Disconnect):
            # FIXME handle disconnect
            pass
        else:
            raise RuntimeError('Unsupported message type: %s' % type(message))


class Message(object):
    '''
    Base class for all messages.
    '''

    @staticmethod
    def from_list(l):
        '''
        Parse a list as defined in the protocol into a message object.

        Keyword arguments:
        l -- list to be parsed
        '''
        if not isinstance(l, (list, tuple)):
            raise ValueError('Message is not encoded as list or tuple')
        try:
            message_class = MESSAGE_CLASS_BY_CODE[l[0]]
        except KeyError:
            raise ValueError('Unsupported message code: %r' % l[0])
        message = message_class.from_list(l)
        return message


class Heartbeat(Message):
    '''
    Heartbeat message
    '''
    code = 0

    def __init__(self, last_message_id):
        '''
        Constructur for heartbeat messages

        Keyword arguments:
        last_message_id -- the message id being acknowledged by this
            heartbeat message
        '''
        self.last_message_id = last_message_id

    @staticmethod
    def from_list(l):
        '''
        Parse list into a heartbeat message

        Keyword arguments:
        l -- list to be parsed
        '''
        return Heartbeat(l[1])

    def to_list():
        '''
        Serialize this message into a list
        '''
        return [self.code, self.last_message_id]


class Notification(Message):
    '''
    Notification message
    '''
    code = 1

    def __init__(self, message_id, method, data=None):
        '''
        Constructor for notification messages

        Keyword arguments:
        method -- name of the method being called
        data -- data for the method being called
        message_id -- id of this message
        '''
        self.message_id = message_id
        self.method = method
        self.data = data

    @staticmethod
    def from_list(l):
        '''
        Parse list into a notification message

        Keyword arguments:
        l -- list to be parsed
        '''
        return Notification(*l[1:])

    def to_list(self):
        '''
        Serialize this message into a list
        '''
        return [self.code, self.message_id, self.method, self.data]


class Request(Message):
    '''
    Request message
    '''
    code = 2

    def __init__(self, message_id, method, data=None):
        '''
        Constructor for request messages

        Keyword arguments:
        method -- name of the method being called
        data -- data for the method being called
        message_id -- id of this message
        '''
        self.message_id = message_id
        self.method = method
        self.data = data
        self._response = gevent.event.AsyncResult()

    def to_list(self):
        return [self.code, self.message_id, self.method, self.data]

    @staticmethod
    def from_list(l):
        '''
        Parse list into a request message

        Keyword arguments:
        l -- list to be parsed
        '''
        return Request(*l[1:])

    @property
    def response(self):
        return self.get_response()

    @response.setter
    def response(self, response):
        self._response.set(response)

    def get_response(self, block=True, timeout=None):
        return self._response.get(block=block, timeout=timeout)


class Response(Message):
    '''
    Response message
    '''
    code = 3

    def __init__(self, message_id, request_message_id, data=None):
        '''
        Constructor for response messages

        Keyword arguments:
        request_message_id -- the message id of the request which caused
                this response
        data -- response data of the method which was called
        message_id -- id of this message
        '''
        self.request_message_id = request_message_id
        self.message_id = message_id
        self.data = data
        self.request = None

    @staticmethod
    def for_request(message_id, request, data=None):
        '''
        Named constructor when the request is known. Some transports
        need the reference to the original request object when sending
        the reply for a request. Therefore the `RpcEngine` generates
        all responses using this method.

        Keyword arguments:
        request -- the request which caused this response
        data -- response data of the method which was called
        message_id -- id of this message
        '''
        response = Response(message_id, request.message_id, data)
        response.request = request
        return response

    @staticmethod
    def from_list(l):
        '''
        Parse list into a response message

        Keyword arguments:
        l -- list to be parsed
        '''
        return Response(*l[1:])

    def to_list(self):
        '''
        Serialize this message into a list
        '''
        if isinstance(self.request, Request):
            return [self.code, self.message_id, self.request.message_id, self.data]
        else:
            return [self.code, self.message_id, self.request, self.data]


class Error(Message):
    '''
    Error message

    This is the message class and not the exception. The `RpcEngine`
    will raise a `RequestException` upon receiving this message type.
    '''
    code = 4

    def __init__(self, message_id, request_message_id, data=None):
        '''
        Constructor for error messages

        Keyword arguments:
        request_message_id -- the message id of the request which caused
                this response
        data -- response data of the method which was called
        message_id -- id of this message
        '''
        self.request_message_id = request_message_id
        self.message_id = message_id
        self.data = data
        self.request = None

    @staticmethod
    def for_request(message_id, request, data=None):
        '''
        Named constructor when the request is known. Some transports
        need the reference to the original request object when sending
        the reply for a request. Therefore the `RpcEngine` generates
        all errors using this method.

        Keyword arguments:
        request -- the request which caused this response
        data -- response data of the method which was called
        message_id -- id of this message
        '''
        error = Error(message_id, request.message_id, data)
        error.request = request
        return error

    @staticmethod
    def from_list(l):
        '''
        Parse list into a error message

        Keyword arguments:
        l -- list to be parsed
        '''
        return Error(*l[1:])

    def to_list(self):
        '''
        Serialize this message into a list
        '''
        if isinstance(self.request, Request):
            return [self.code, self.message_id, self.request.message_id, self.data]
        else:
            return [self.code, self.message_id, self.request, self.data]


class Disconnect(Message):
    '''
    Disconnect message
    '''
    code = -1

    @staticmethod
    def from_list(l):
        '''
        Parse list into a disconnect message

        Keyword arguments:
        l -- list to be parsed
        '''
        return Disconnect()

    def to_list(self):
        '''
        Serialize this message into a list
        '''
        return [self.code]


# Dictionary which maps the message codes to the according classes.
# This is only used by the `Message` class in the static `from_list`
# method.
MESSAGE_CLASS_BY_CODE = {
    Heartbeat.code: Heartbeat,
    Notification.code: Notification,
    Request.code: Request,
    Response.code: Response,
    Error.code: Error,
    Disconnect.code: Disconnect
}
