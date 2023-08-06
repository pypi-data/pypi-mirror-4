from gevent import monkey; monkey.patch_all()
from Corellia.client import Client
from Corellia.kvstore import KVStore
from ..config import config
from uuid import uuid1
import Husky

client = Client(config.host, "Briareus", pickler=Husky, serialize=True, interval=0.1)


class Cloud(object):
    def __init__(self, f):
        self.f = f

    def __call__(self, *args):
        res = Client(config.host, "Briareus", pickler=Husky, serialize=True, interval=0.1).eval(self.f, args)
        print "res:", res
        # return Husky.loads(res)

    def __getstate__(self):
        return Husky.dumps(self.f)

    def __setstate__(self, state):
        self.f = Husky.loads(state) 

class CachedData(object):

    name = "CachedData"

    def __init__(self, var):
        self.value = var
        self.put(self.value)

    def __getstate__(self):
        return self.id

    def __setstate__(self, state):
        self.id = state

    def __getattr__(self, name):
        if name == "value":
            self.__dict__["value"] = self.get(self.id)
            return self.__dict__["value"]
        else:
            return getattr(self.value, name)

    def put(self, value):
        self.id = uuid1().hex
        KVStore(config.host, self.name).set(self.id, value)

    def get(self, key):
        return KVStore(config.host, self.name).get(key)

    def __del__(self):
        pass