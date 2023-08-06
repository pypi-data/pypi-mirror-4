from redis import StrictRedis
import Husky
import snappy


def dumps(x):
    return snappy.compress(Husky.dumps(x))

def loads(x):
    return Husky.loads(snappy.decompress(x))


class KVStore(object):
    def __init__(self, name, host, port):
        self.name = ".".join([name, "KVStore"])
        self.redis = StrictRedis(host, port)

    def get(self, key):
        bytes = self.redis.hget(self.name, key)
        return loads(bytes)

    def put(self, key, value):
        self.redis.hset(self.name, key, dumps(value))
        return key

    def remove(self, key):
        pass
