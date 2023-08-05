import fudge
from nose2.compat import unittest

class TestNamespace(unittest.TestCase):

    def setUp(self):
        from gevent import monkey
        with fudge.patched_context(
            monkey, 'patch_all', fudge.Fake().expects_call()):
            import womack.namespace
            self.env = {'socketio': fudge.Fake().has_attr(session={})}
            self.ns = womack.namespace.Namespace(self.env, 'fake')

    @fudge.patch('socketio.namespace.BaseNamespace.spawn')
    def test_on_subscribe_spawns_listener(self, spawn):
        spawn.expects_call().with_args(self.ns.listener, set(['1', '2', '3']))
        self.ns.on_subscribe({'channels': ['1', '2', '3']})

    @fudge.patch('redis.StrictRedis')
    @fudge.patch('socketio.namespace.BaseNamespace.emit')
    def test_listener_listens_and_emits(self, Redis, emit):
        (Redis.expects_call().returns_fake()
         .expects('pubsub').returns_fake()
         .expects('subscribe').with_args('womack:ns:default:chan')
         .expects('listen').returns([{
                        'type': 'message',
                        'channel': 'womack:ns:default:chan',
                        'data': '{"a": 1}'}])
         )
        emit.expects_call().with_args('chan', {'a': 1})
        self.ns.listener(['chan'])
