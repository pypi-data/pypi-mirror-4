from gevent import monkey; monkey.patch_all()
from utils import CachedData
from Corellia.taskqueue import TaskQueue
import time

class Worker(object):
    def __init__(self, addr, path, **kargs):
        self.tq = TaskQueue(addr, path, **kargs)

    def run(self, cls, *args, **kargs):
        ins = cls(*args, **kargs)
        while 1:
            print 0, time.clock()
            task =  self.tq.GET_TASK()
            print 1, time.clock()
            key, method, args = task
            func = getattr(ins, method, None)
            if func:
                # try:
                print 2, time.clock()
                result = func(*args)
                print 3, time.clock()
                # except Exception, e:
                #   result = str(e)
            else:
                result = "No Such Method!"
            self.tq.PUT_RESULT(key, result)
            print 4, time.clock()


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
    Worker(config.host, "Briareus", pickler=Husky, serialize=True).run(Runtime)


