class Config(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def configure(self, items):
        self.update(items)

config = Config(
    host='0.0.0.0',
    port=8111,
    redis_host='localhost',
    redis_port=6379,
    key='womack:ns:default',
)
