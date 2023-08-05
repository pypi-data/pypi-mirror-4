import json

import redis

from .config import config


class Publisher(object):
    """Womack event publisher.

    Use instances of this class to publish events to Womack channels.

    :param redis_connection: Redis instance to publish events to. Default
                             is None, in which case a connection will be
                             to the made to the redis_host and redis_port
                             set in the :doc:`config`.

    :param key: The key prefix to use when qualifying channel names.
                Default is None, in which case they key used is the
                one set in the :doc:`config`.

    Contains code derived from juggernaut.py which is copyright 2012
    Armin Ronacher.

    """
    def __init__(self, redis_connection=None, key=None):
        if redis_connection is None:
            redis_connection = redis.StrictRedis(host=config.redis_host,
                                                 port=config.redis_port)
        self.redis = redis_connection
        self.key = key if key else config.key

    def publish(self, channels, data, **options):
        """Publish  data to one ore more channels.

        :param channels: Channel or list of channels.
        :param data: Data to publish. Must be json-encodable.
        :param \*\*options: Additional keys to set in the hash
                            passed to redis.publish().

        """
        if isinstance(channels, basestring):
            channels = [channels]
        d = {'data': data}
        d.update(options)
        data = json.dumps(d)
        for channel in channels:
            self.redis.publish("%s:%s" % (self.key, channel), data)
