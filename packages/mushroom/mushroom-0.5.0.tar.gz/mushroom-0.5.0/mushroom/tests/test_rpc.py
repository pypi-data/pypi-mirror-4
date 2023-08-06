import logging
import unittest

import gevent
from gevent.event import AsyncResult
from gevent import monkey
from gevent.pywsgi import WSGIServer

import mushroom
from mushroom import rpc


def setUpModule():
    logging.basicConfig()


class MockTransport(object):
    rpc_engine = None

    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(message)


class TestService(object):

    def __init__(self):
        self.recv_notify_ok = AsyncResult()
        self.recv_request_ok = AsyncResult()

    def rpc_recv_notify(self, request):
        self.recv_notify_ok.set(True)

    def rpc_recv_request(self, request):
        self.recv_request_ok.set(True)
        return 'recv_request_ok'

    def rpc_recv_error(self, request):
        self.recv_error_ok.set(True)
        return 'recv_request_ok'


class EngineTestCase(unittest.TestCase):

    def setUp(self):
        self.transport = MockTransport()
        self.service = TestService()
        self.engine = rpc.Engine(self.transport,
                rpc.MethodDispatcher(self.service))

    def tearDown(self):
        pass

    def test_recv_notify(self):
        self.engine.handle_message(rpc.Notification(
            message_id=1,
            method='recv_notify',
            data=None))
        self.assertTrue(self.service.recv_notify_ok.get(timeout=1))

    def test_recv_request(self):
        request = rpc.Request(message_id=1, method='recv_request', data=None)
        self.engine.handle_message(request)
        gevent.sleep()
        self.assertEqual(len(self.transport.messages), 1)
        response = self.transport.messages[0]
        self.assertIsInstance(response, rpc.Response)
        self.assertEqual(response.data, 'recv_request_ok')
        self.assertEqual(response.request_message_id, request.message_id)
        self.assertTrue(self.service.recv_request_ok.get(timeout=1))

    def test_recv_response(self):
        request = rpc.Request(message_id=1,
                method='recv_response',
                data=None)
        self.engine.requests[1] = request
        response = rpc.Response(message_id=1,
                request_message_id=request.message_id,
                data='recv_response_ok')
        self.engine.handle_message(response)
        self.assertIs(request.get_response(timeout=1), response)

    def test_recv_error(self):
        request = rpc.Request(message_id=1,
                method='recv_error',
                data=None)
        self.engine.requests[1] = request
        error = rpc.Error(message_id=1,
                request_message_id=request.message_id,
                data='recv_error_ok')
        self.engine.handle_message(error)
        self.assertIs(request.get_response(timeout=1), error)

    def test_send_notify(self):
        # FIXME implement
        self.skipTest('test incomplete')

    def test_send_request(self):
        # FIXME implement
        self.skipTest('test incomplete')

    def test_send_response(self):
        # FIXME implement
        self.skipTest('test incomplete')

    def test_send_error(self):
        # FIXME implement
        self.skipTest('test incomplete')
