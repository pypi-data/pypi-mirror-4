from gevent import monkey; monkey.patch_all()
from utils import CachedData
from Corellia.taskqueue import TaskQueue

class Worker(object):
    def __init__(self, addr, path, **kargs):
        self.tq = TaskQueue(addr, path, **kargs)

    def run(self, cls, *args, **kargs):
        ins = cls(*args, **kargs)
        while 1:
            task =  self.tq.GET_TASK()
            if not task:
                continue
            key, method, args = task
            func = getattr(ins, method, None)
            if func:
                # try:
                result = func(*args)
                # except Exception, e:
                #   result = str(e)
            else:
                result = "No Such Method!"
            self.tq.PUT_RESULT(key, result) 


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
    Worker(config.host, "Briareus", pickler=Husky, serialize=False).run(Runtime)


