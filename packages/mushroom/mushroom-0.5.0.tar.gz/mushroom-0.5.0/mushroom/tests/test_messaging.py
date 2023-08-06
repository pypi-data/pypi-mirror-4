import logging
import unittest

import gevent
from gevent.event import Event
from gevent import monkey
from gevent.pywsgi import WSGIServer
from kombu import BrokerConnection
from kombu import Exchange, Queue
from kombu import pools

import mushroom
from mushroom import messaging
from mushroom import rpc


SERVER_HOST = '127.0.0.1'
SERVER_PORT = 39288 # picked by random.randint(1024, 65535)

BROKER_URL = 'amqp://mushroom:mushroom@localhost//mushroom'

# During tests the time until a message arrives should never exceed
# one second.
TIMEOUT = 1


class MessagingTestService(object):

    def __init__(self):
        self.success = False
        self.test_done = Event()

    def rpc_ping(self, request):
        self.success = True
        self.test_done.set()

    def rpc_get_answer(self, request):
        return 42

    def rpc_get_fail(self, request):
        raise rpc.RequestException('FAIL!')


class MessagingTestCase(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        monkey.patch_socket()
        # prepare exchange and queue
        self.exchange = Exchange('test', type='direct')
        self.monolog_queue = Queue('monolog', self.exchange, routing_key='monolog')
        self.a_queue = Queue('a', self.exchange, routing_key='a')
        self.b_queue = Queue('b', self.exchange, routing_key='b')
        # purge queue so we start with a fresh test
        self.purge(self.monolog_queue, self.a_queue, self.b_queue)

    def tearDown(self):
        self.purge(self.monolog_queue, self.a_queue, self.b_queue)

    def purge(self, *queues):
        self.connection_pool = pools.connections[BrokerConnection(BROKER_URL)]
        with self.connection_pool.acquire() as connection:
            for queue in queues:
                queue(connection.channel()).declare()
                with connection.Consumer(queue) as consumer:
                    consumer.purge()

    def test_rpc_notify(self):
        test_service = MessagingTestService()
        transport = messaging.Transport(BROKER_URL, self.exchange, self.monolog_queue)
        engine = rpc.Engine(transport, mushroom.MethodDispatcher(test_service, prefix='rpc_'))
        try:
            transport.start()
            engine.notify('ping', routing_key='monolog')
            if not test_service.test_done.wait(1):
                self.fail('Timeout')
            self.assertTrue(test_service.success)
        finally:
            transport.stop()

    def test_rpc_request(self):
        test_service = MessagingTestService()
        transport = messaging.Transport(BROKER_URL, self.exchange, self.monolog_queue)
        engine = rpc.Engine(transport, mushroom.MethodDispatcher(test_service, prefix='rpc_'))
        try:
            transport.start()
            answer = engine.request('get_answer', routing_key='monolog', timeout=TIMEOUT)
            self.assertEqual(answer, 42)
        finally:
            transport.stop()

    def test_rpc_request_error(self):
        test_service = MessagingTestService()
        transport = messaging.Transport(BROKER_URL, self.exchange, self.monolog_queue)
        engine = rpc.Engine(transport, mushroom.MethodDispatcher(test_service, prefix='rpc_'))
        try:
            transport.start()
            self.assertRaises(rpc.RequestException, engine.request,
                    'get_fail', routing_key='monolog', timeout=TIMEOUT)
        finally:
            transport.stop()
