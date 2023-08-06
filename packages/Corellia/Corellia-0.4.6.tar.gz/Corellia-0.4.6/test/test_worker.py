import sys
sys.path.append("..")
from Corellia import worker

class NonWorker(object):
    def length(self, a):
        return len(a)

if __name__ == '__main__':
    import msgpack
    setattr(msgpack, "dumps", msgpack.packb)
    setattr(msgpack, "loads", msgpack.unpackb)
    import czjson
    worker.WorkerPool("localhost", "test", pickler=msgpack).run(NonWorker, num=2)