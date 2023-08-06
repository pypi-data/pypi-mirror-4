#!/usr/bin/env python

from __future__ import absolute_import

import os
import sys

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 39288 # picked by random.randint(1024, 65535)

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(TESTS_DIR))
SELENIUM_HTML = os.path.join(TESTS_DIR, 'selenium.html')

if __name__ == '__main__':
    del sys.path[0]
    sys.path[0:0] = [PROJECT_ROOT]

import gevent
from gevent.event import Event
import json
import logging
from selenium import webdriver
import signal
import subprocess
import threading
import time
import unittest

import mushroom
from mushroom.geventfd import GeventFD
from mushroom.tests.utils import TestServer



class AsyncDict(object):
    '''
    Dictionary like container that supports waiting for keys.
    '''

    def __init__(self):
        self.d = {}
        self.events = []

    def _notify_all(self):
        for event in self.events:
            event.set()

    def update(self, d):
        self.d.update(d)
        self._notify_all()

    def __setitem__(self, name):
        self.d['name'] = value
        self._notify_all()

    def __getitem__(self, name):
        return self.d['name']

    def get(self, name, timeout=None, clear=False):
        event = Event()
        try:
            self.events.append(event)
            with gevent.Timeout(timeout):
                while True:
                    try:
                        if clear:
                            return self.d.pop(name)
                        else:
                            return self.d[name]
                    except KeyError:
                        event.wait()
                        event.clear()
        finally:
            self.events.remove(event)



class ServerControl(object):
    '''
    Wrapper around the server subprocess which provides a way to receive
    updates of the async state_dict via stdout. The updates are JSON
    serialized and every line on stdout contains exactly one dictionary
    that is used to update the state_dict.
    '''

    def __init__(self):
        self.state_dict = AsyncDict()

    def start(self):
        self.proc = subprocess.Popen(
                [sys.executable, os.path.abspath(__file__)],
                stdout=subprocess.PIPE,
                env={
                    'PYTHONDONTWRITEBYTECODE': '1'
                })
        gevent.spawn(self.read_from_stdout)
        # wait for server to be online
        self.get('online')

    def stop(self):
        self.proc.terminate()
        self.proc.wait()

    def read_from_stdout(self):
        for line in GeventFD(self.proc.stdout).readlines():
            d = json.loads(line)
            self.state_dict.update(d)

    def get(self, name, timeout=None, clear=False):
        '''
        Retrieve state variable from state dict. If the variable
        is not set wait for it `timeout` seconds.
        '''
        return self.state_dict.get(name, timeout=timeout, clear=clear)


class SeleniumTestServer(TestServer):
    '''
    Server which is being controlled by the ServerControl. This class
    provides a `set` method which produces output on stdout which is
    then parsed in the ServerControl class to update the state_dict.
    This is used by the test cases to report if the expected methods
    were called in the correct way.
    '''

    def __init__(self, listener):
        super(SeleniumTestServer, self).__init__(listener,
                SELENIUM_HTML,
                rpc_handler=mushroom.MethodDispatcher(self, 'rpc_'),
                session_handler=mushroom.SessionHandlerAdapter(self, 'session_'),
                log=None)
        self.set_sessions()

    def set(self, name, value):
        sys.stdout.write(json.dumps({ name: value }))
        sys.stdout.write('\n')
        sys.stdout.flush()

    def set_sessions(self):
        self.set('sessions', [
            {
                'id': session.id
            }
            for session in self.sessions
        ])

    def session_authenticate(self, session, auth):
        return True

    def session_connect(self, session):
        self.set_sessions()

    def session_disconnect(self, session):
        self.set_sessions()

    def rpc_message(self, request):
        self.sessions.notify('message', request.data)

    def rpc_test_request(self, request):
        self.set('request_received', True)
        return 42

    def rpc_test_notification(self, request):
        self.set('notification_received', True)


class SeleniumTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # remove http(s)_proxy environment variables as they can
        # screw up the tests.
        cls.env_backup = {
            'http_proxy': os.environ.pop('http_proxy', None),
            'https_proxy': os.environ.pop('https_proxy', None)
        }
        cls.server_url = 'http://%s:%s/' % (SERVER_HOST, SERVER_PORT)
        cls.browser = webdriver.Firefox()
        cls.browser.set_window_position(0, 0);
        cls.browser.set_window_size(400, 400);
        cls.browser.set_script_timeout(1)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'browser'):
            cls.browser.close()
        # restore environment variables
        for name, value in cls.env_backup.iteritems():
            if value:
                os.environ[name] = value

    def setUp(self):
        self.server = ServerControl()
        self.server.start()
        self.browser.get(self.server_url)

    def tearDown(self):
        self.server.stop()

    def browser_exec(self, func):
        func_type = self.browser.execute_script('return typeof(%s)' % func);
        if (func_type == 'undefined'):
            raise RuntimeError('typeof(%s) === undefined' % func)
        try:
            js = '%s(arguments[arguments.length-1])' % func;
            return self.browser.execute_async_script(js)
        except Exception as e:
            js_error = self.browser.execute_script(
                    'return jsError;');
            raise RuntimeError('JavaScript error: %s' % js_error)

    def test_connect(self):
        self.assertTrue(self.browser_exec('test_connect'));

    def test_connect_server_offline(self):
        # This test assumes that no service is running at the highest
        # available port number (65535). If you are running a service
        # at this port number this test will fail.
        self.assertTrue(self.browser_exec('test_connect_server_offline'));

    def test_send_request(self):
        self.assertIs(self.browser_exec('test_send_request'), True);
        self.assertTrue(self.server.get('request_received', timeout=1))

    def test_send_notification(self):
        self.assertIs(self.browser_exec('test_send_notification'), True);
        self.assertTrue(self.server.get('notification_received', timeout=1))

    def test_send_disconnect(self):
        self.assertEquals(len(self.server.get('sessions', timeout=1, clear=True)), 0)
        self.assertIs(self.browser_exec('test_disconnect_1'), True)
        self.assertEquals(len(self.server.get('sessions', timeout=1, clear=True)), 1)
        self.assertIs(self.browser_exec('test_disconnect_2'), True)
        self.assertEquals(len(self.server.get('sessions', timeout=1, clear=True)), 0)


if __name__ == '__main__':
    logging.basicConfig()
    server = SeleniumTestServer((SERVER_HOST, SERVER_PORT))
    server.start()
    server.set('online', True)
    server.serve_forever()
