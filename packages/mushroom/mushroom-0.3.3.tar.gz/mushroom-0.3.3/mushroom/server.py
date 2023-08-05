from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from mushroom.application import Application


class Server(WSGIServer):

    def __init__(self, listener, rpc_handler=None,
            auth_handler=None, disconnect_handler=None):
        super(Server, self).__init__(listener,
                Application(rpc_handler, auth_handler, disconnect_handler),
                handler_class=WebSocketHandler)

    @property
    def sessions(self):
        return self.application.sessions
