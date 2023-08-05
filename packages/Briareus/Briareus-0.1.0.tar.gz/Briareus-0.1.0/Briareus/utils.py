from gevent import monkey; monkey.patch_all()
from Corellia.RedisQueue import Client
from Corellia.RedisStore import KVStore
from gevent.pool import Pool
from uuid import uuid1
import Husky
from config import config

pool = Pool(config.num_greenlet)

class Cloud(object):
    def __init__(self, f):
        self.f = f

    def __call__(self, *args):
        return Client(config.host, config.port, config.queue_name).eval(self.f, args)

    def __getstate__(self):
        return Husky.dumps(self.f)

    def __setstate__(self, state):
        self.f = Husky.loads(state) 

# def cloud(f):
#     def wrapped(*args):
#         # client = Client("192.168.70.150", 6379, "Runtime")
#         client = Client(HOST, PORT, "Runtime")
#         return client.eval(f, args)
#     return wrapped

def pmap(f, l):
    return pool.map(f, l)


class CachedData(object):

    name = "CachedData"

    def __init__(self, var):
        self.value = var
        self.id = self.put(self.value)

    def __getstate__(self):
        return self.id

    def __setstate__(self, state):
        self.id = state

    def __getattr__(self, name):
        if name == "value":
            self.__dict__["value"] = self.get(self.id)
            return self.__dict__["value"]
        else:
            return None

    def put(self, value):
        return KVStore(self.name, config.host, config.port).put(uuid1().hex, value)

    def get(self, key):
        return KVStore(self.name, config.host, config.port).get(key)

    def __del__(self):
        pass

