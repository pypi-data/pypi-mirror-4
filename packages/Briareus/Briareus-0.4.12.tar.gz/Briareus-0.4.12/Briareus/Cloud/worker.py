from gevent import monkey; monkey.patch_all()
from utils import CachedData

class Runtime(object):
    def __init__(self):
        self.cache = {}

    def getvalue(self, v):
        if isinstance(v, CachedData):
            if v.id in self.cache:
                return self.cache[v.id]
            else:
                self.cache[v.id] = v.value
                return v.value
        else:
            return v

    def eval(self, f, args):
        f = self.getvalue(f)
        return f(*map(self.getvalue, args))

def run():
    from Corellia.worker import WorkerPool
    import Husky
    from ..config import config
    WorkerPool(config.host, "Briareus", pickler=Husky, serialize=False, mass=False, num=1).run(Runtime)