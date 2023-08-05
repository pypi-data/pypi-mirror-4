import fudge
from nose2.compat import unittest

import womack.publish


class TestPublisher(unittest.TestCase):

    @fudge.patch('redis.StrictRedis')
    def test_establishes_connection_based_on_config(self, Redis):
        Redis.expects_call().with_args(host='localhost', port=6379)
        womack.publish.Publisher()

    @fudge.patch('redis.StrictRedis')
    def test_accepts_redis_connection(self, Redis):
        # doesn't matter that this isn't real, not using it
        womack.publish.Publisher(object())

    @fudge.patch('redis.StrictRedis')
    def test_publishes_on_qualified_channels(self, Redis):
        Redis.expects_call().returns_fake().expects('publish').with_args(
            'womack:ns:default:channel', '{"data": {"a": 1}}')
        wm = womack.publish.Publisher()
        wm.publish('channel', {'a': 1})
