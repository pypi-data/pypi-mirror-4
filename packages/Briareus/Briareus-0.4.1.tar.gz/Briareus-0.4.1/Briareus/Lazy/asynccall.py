from gevent import monkey;monkey.patch_all()
import gevent

class AsyncResult(object):
    def __init__(self, greenlet):
        self.greenlet = greenlet

    def __getattr__(self, name):
        if name == "_result":
            self.greenlet.join()
            self.__dict__["_result"] = self.greenlet.value
            return self.__dict__["_result"]
        else:
            return getattr(self._result, name)


class AsyncCallable(object):
    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kargs):
        greenlet = gevent.spawn(self.f, *args, **kargs)
        return AsyncResult(greenlet)