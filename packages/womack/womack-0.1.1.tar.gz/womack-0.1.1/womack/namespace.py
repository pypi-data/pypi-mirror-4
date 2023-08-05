from gevent import monkey; monkey.patch_all()

import logging

from json import loads

import redis
from socketio.namespace import BaseNamespace

from .config import config


class Namespace(BaseNamespace):
    """Default namespace handler

    Responds to 'subscribe' event by listening on requested redis
    channels for messages, which are emitted via socketio
    to the connected client on the appropriate channel.

    """
    _key = None # means look up from config

    @property
    def key(self):
        return self._key if self._key else config.key

    def qualified_channel_name(self, channel):
        return "%s:%s" % (self.key, channel)

    def listener(self, channels):
        r = redis.StrictRedis(
            config.redis_host, config.redis_port).pubsub()

        for chan in channels:
            key = self.qualified_channel_name(chan)
            r.subscribe(key)

        for m in r.listen():
            try:
                if m['type'] == 'message':
                    # de-qualify the channel name
                    channel = m['channel'].split(':')[-1]
                    data = loads(m['data'])
                    if channel in channels:
                        self.emit(channel, data)
            except Exception:
                logging.getLogger(__name__).exception(
                    "Received invalid message %s", m)

    def on_subscribe(self, data):
        channels = data.get('channels', data.get('channel', ''))
        if isinstance(channels, basestring):
            channels = [channels]
        channels = set(channels)
        self.spawn(self.listener, channels)


REGISTRY = {'': Namespace}

def register(namespace, cls):
    """Register a namespace handler"""
    REGISTRY[namespace] = cls
