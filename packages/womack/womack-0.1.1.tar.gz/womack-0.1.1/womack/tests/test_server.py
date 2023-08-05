import bottle
import fudge
from nose2.compat import unittest


class TestServer(unittest.TestCase):

    def setUp(self):
        from gevent import monkey
        with fudge.patched_context(
            monkey, 'patch_all', fudge.Fake().expects_call()):
            import womack.server
            self.srv = womack.server
        bottle.request.environ = {}

    def tearDown(self):
        del bottle.request.environ

    def test_socketio_calls_socketio_manage(self):
        manage = fudge.Fake()
        with fudge.patched_context(
            self.srv, 'socketio_manage', manage):
            manage.expects_call()
            self.srv.socketio()

