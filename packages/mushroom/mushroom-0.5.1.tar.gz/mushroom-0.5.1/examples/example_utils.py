import codecs
import os

from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketHandler

import mushroom
from mushroom.http import HttpResponse


MUSHROOM_JS_FILENAME = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'js', 'mushroom.js')
JQUERY_JS_FILENAME = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'jquery-1.8.2.min.js')
KNOCKOUT_JS_FILENAME = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'knockout-2.2.0.min.js')
GAUGE_JS_FILENAME = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'gauge-1.2.min.js')


class ExampleServer(WSGIServer):

    def __init__(self, listener, index_template, rpc_handler=None,
            session_handler=None, **kwargs):
        super(ExampleServer, self).__init__(listener,
                ExampleApplication(index_template, rpc_handler,
                    session_handler),
                handler_class=WebSocketHandler,
                **kwargs)

    @property
    def sessions(self):
        return self.application.sessions


class ExampleApplication(mushroom.Application):

    def __init__(self, index_template, rpc_handler=None,
            session_handler=None):
        self.index_template = index_template
        super(ExampleApplication, self).__init__(rpc_handler,
                session_handler)

    def load_file(self, filename):
        with codecs.open(filename) as fh:
            return fh.read()

    def request(self, request):
        if request.method == 'GET':
            if request.path == ['favicon.ico']:
                return HttpResponse('404 Not Found')
            if request.path == ['js', 'mushroom.js']:
                return HttpResponse('200 OK', self.load_file(MUSHROOM_JS_FILENAME),
                        extra_headers={'Content-Type': 'application/javascript'})
            if request.path == ['js', 'jquery.js']:
                return HttpResponse('200 OK', self.load_file(JQUERY_JS_FILENAME),
                        extra_headers={'Content-Type': 'application/javascript'})
            if request.path == ['js', 'knockout.js']:
                return HttpResponse('200 OK', self.load_file(KNOCKOUT_JS_FILENAME),
                        extra_headers={'Content-Type': 'application/javascript'})
            if request.path == ['js', 'gauge.js']:
                return HttpResponse('200 OK', self.load_file(GAUGE_JS_FILENAME),
                        extra_headers={'Content-Type': 'application/javascript'})
            if request.path == []:
                return HttpResponse('200 OK', self.load_file(self.index_template),
                        extra_headers={'Content-Type': 'text/html'})
        return super(ExampleApplication, self).request(request)

