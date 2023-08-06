from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from mushroom.application import Application


class Server(WSGIServer):

    def __init__(self, listener, rpc_handler=None,
            session_handler=None):
        super(Server, self).__init__(listener,
                Application(rpc_handler, session_handler),
                handler_class=WebSocketHandler)

    @property
    def sessions(self):
        return self.application.sessions
