from Corellia import client
print client
import ujson as json
import msgpack
setattr(msgpack, "dumps", msgpack.packb)
setattr(msgpack, "loads", msgpack.unpackb)

c = client.Client("localhost", "test", serialize=True, pickler=msgpack)

size_block = 0.1
co = 20
a = "0" * int(size_block*1000)

print len(msgpack.dumps((1, "length", a)))
print len(json.dumps((1, "length", a)))
# exit(0)

def test_pt():
    for i in xrange(int(co*1000)):
        c.put_task("length", (a,), str(i))
    c.finish()

# import time
# time.sleep(10)

import gevent
from gevent.pool import Pool
pool = Pool(1000*co)
def test_gr():
    # for i in xrange(int(co*1000)):
    #     assert c.get_result(i) == size_block*1000
    pool.map(lambda i:c.get_result(str(i))==100, xrange(int(co*1000)))

# import cProfile as profile
# profile.run("test()", "prof.txt")
# import pstats
# p = pstats.Stats("prof.txt")
# p.sort_stats("cumulative").print_stats()

import timeit
import numpy as np

t = timeit.Timer("test_pt()", "from __main__ import test_pt")
d = np.mean(t.repeat(10, 1))
print co/d, d

# t = timeit.Timer("test_gr()", "from __main__ import test_gr")
# d = np.mean(t.repeat(10, 1))
# print co/d, d


# import cProfile as profile
# profile.run("test_pt()", "prof.txt")
# import pstats
# p = pstats.Stats("prof.txt")
# p.sort_stats("cumulative").print_stats()

