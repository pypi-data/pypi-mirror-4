from gevent import monkey; monkey.patch_all()
from gevent.pool import Pool
import inspect
from ..config import config


pool = Pool(config.num_greenlet)

def pmap(f, l):
    return pool.map(f, l)

def export(ls):
    frame = inspect.getouterframes(inspect.currentframe())[1][0]
    for item in ls:
        frame.f_globals.update(item)

def product(*args):
    if len(args) == 1:
        return args[0]
    result = [[]]
    for arg in args:
        result = [x+[y] for x in result for y in arg]
    return result

def product2(iters, filters):
    result = [[]]
    for item, f in zip(iters, filters):
        if f:
            result = [x+[y] for x in result for y in item if f(x+[y])]
        else:
            result = [x+[y] for x in result for y in item]
    return result


if __name__ == '__main__':
    print product(range(10))



