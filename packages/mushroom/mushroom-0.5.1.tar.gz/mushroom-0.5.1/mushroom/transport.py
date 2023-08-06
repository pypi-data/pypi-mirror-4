from gevent.event import Event

from mushroom.rpc import Heartbeat
from mushroom.rpc import Disconnect
from mushroom.rpc import Message
from mushroom.utils import Observable


class UnreliableTransport(object):
    '''
    Base class for unreliable transports. Unreliable means that
    the underlying protocol does not guarantee message delivery
    by itself. This is typically the case for any protocol that
    does raw communication without a layer that guarantees message
    delivery by itself.
    '''

    def __init__(self):
        # Outbound messages not yet acknowledged by the remote side
        self.messages = []
        # Last received message id. This is used to drop messages
        # already received from the remote side.
        self.last_message_id = None
        # Handler for RPC messages
        self.rpc_engine = None
        # Remote ip address; set by the transport implementation.
        self.remote_addr = None
        # Transport state
        self.state = Observable('DISCONNECTED')

    def handle_message(self, message):
        if hasattr(message, 'message_id'):
            if message.message_id <= self.last_message_id:
                # Ignore messages that we have already received
                return
        if isinstance(message, Heartbeat):
            self.handle_heartbeat(message)
        elif isinstance(message, Disconnect):
            self.handle_disconnect()
        else:
            # All messages except for Heartbeat and Disconnect
            # are handled by the RPC engine.
            self.rpc_engine.handle_message(message)

    def handle_heartbeat(self, heartbeat):
        last_message_id = heartbeat.last_message_id
        index = 0
        for message in self.messages:
            if message.message_id <= last_message_id:
                index += 1
            else:
                break
        if index > 0:
            del self.messages[:index]

    def handle_connect(self):
        # The client managed to connect. Try resending messages which
        # have not been acknowledged, yet.
        self.state('CONNECTED')
        for message in self.messages:
            self.real_send(message)

    def handle_disconnect(self, reconnect=False):
        if reconnect:
            self.state('CONNECTING')
        else:
            self.state('DISCONNECTED')

    def connect(self):
        '''
        Start transport and connect to the remote side. This method
        is transport specific and must be overwriten.
        '''
        raise NotImplementedError

    def disconnect(self):
        '''
        Disconnect from the remote side and stop transport. This method
        is transport specific and must be overwritten.
        '''
        raise NotImplementedError

    def send(self, message):
        self.messages.append(message)
        if self.state() == 'CONNECTED':
            self.real_send(message)

    def real_send(self, message):
        '''
        Perform the actual send operation. This method is only called
        internally and should not be called from application code.
        This method is transport specific and must be overwritten.
        '''
        raise NotImplementedError
