import codecs
import os

from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketHandler

import mushroom
from mushroom.http import HttpResponse


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SELENIUM_JS = os.path.join(TESTS_DIR, 'selenium.js')
PROJECT_ROOT = os.path.dirname(os.path.dirname(TESTS_DIR))
MUSHROOM_JS = os.path.join(PROJECT_ROOT, 'js', 'mushroom.js')


class TestServer(WSGIServer):

    def __init__(self, listener, index_template, rpc_handler=None,
            session_handler=None, **kwargs):
        super(TestServer, self).__init__(listener,
                TestApplication(index_template, rpc_handler,
                    session_handler),
                handler_class=WebSocketHandler,
                **kwargs)

    @property
    def sessions(self):
        return self.application.sessions


class TestApplication(mushroom.Application):

    def __init__(self, index_template, rpc_handler=None,
            session_handler=None):
        self.index_template = index_template
        super(TestApplication, self).__init__(rpc_handler,
                session_handler)

    def load_file(self, filename):
        with codecs.open(filename) as fh:
            return fh.read()

    def request(self, request):
        if request.method == 'GET':
            if request.path == ['favicon.ico']:
                return HttpResponse('404 Not Found')
            if request.path == ['js', 'mushroom.js']:
                return HttpResponse('200 OK', self.load_file(MUSHROOM_JS),
                        extra_headers={'Content-Type': 'application/javascript'})
            if request.path == ['js', 'selenium.js']:
                return HttpResponse('200 OK', self.load_file(SELENIUM_JS),
                        extra_headers={'Content-Type': 'application/javascript'})
            if request.path == []:
                return HttpResponse('200 OK', self.load_file(self.index_template),
                        extra_headers={'Content-Type': 'text/html'})
        return super(TestApplication, self).request(request)

