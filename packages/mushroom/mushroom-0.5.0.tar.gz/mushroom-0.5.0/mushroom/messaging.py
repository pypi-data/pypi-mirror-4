import logging
import socket

import gevent
import gevent.queue
from kombu import pools
from kombu import BrokerConnection

from mushroom.rpc import Engine
from mushroom.rpc import Message
from mushroom.rpc import Notification


logger = logging.getLogger('mushroom.messaging')


class Transport(object):

    def __init__(self, broker_url, exchange, queue):
        '''
        Create a transport capable of receiving from one queue and sending to
        multiple exchanges.

        Arguments:
        broker_url -- URL for connecting to the broker
        queue      -- kombu.Queue object to read messages from
        exchange   -- kombu.Exchange object to send messages to
        '''
        self.producer_pool = pools.producers[BrokerConnection(broker_url)]
        self.connection_pool = pools.connections[BrokerConnection(broker_url)]
        self.greenlet = None
        self.exchange = exchange
        self.queue = queue
        self.rpc_engine = None

    def start(self):
        assert self.rpc_engine, 'rpc_engine not set'
        assert not self.greenlet, 'already running'
        self.keep_running = True
        self.greenlet = gevent.spawn(self.mainloop)

    def stop(self, join=True):
        self.keep_running = False
        if self.greenlet and join:
            self.greenlet.join()

    def mainloop(self):
        try:
            with self.connection_pool.acquire() as connection:
                self.queue(connection.channel()).declare()
                with connection.Consumer(self.queue, callbacks=[self.callback]) as consumer:
                    while self.keep_running:
                        try:
                            connection.drain_events(timeout=1)
                        except socket.timeout:
                            continue
        finally:
            self.greenlet = None

    def callback(self, body, message):
        try:
            rpc_message = Message.from_list(body)
        except ValueError, e:
            # Message is malformed.
            logger.exception(e)
            message.reject()
        else:
            rpc_message.reply_to = message.properties.get('reply_to', '')
            self.rpc_engine.handle_message(rpc_message)
            message.ack()

    def send(self, message, routing_key=None):
        if not routing_key:
            # No routing key means that we are sending a notification or
            # response. So we need to extract the reply_to information
            # from the request object.
            request = message.request
            routing_key = request.reply_to
        with self.producer_pool.acquire() as producer:
            producer.maybe_declare(self.exchange)
            producer.publish(message.to_list(), routing_key=routing_key,
                    reply_to=self.queue.routing_key)


class Client(Engine):

    def __init__(self, broker_url, exchange, queue, rpc_handler):
        super(Client, self).__init__(
                Transport(broker_url, exchange, queue),
                rpc_handler)

    def start(self):
        self.transport.start()

    def stop(self):
        self.transport.stop()
