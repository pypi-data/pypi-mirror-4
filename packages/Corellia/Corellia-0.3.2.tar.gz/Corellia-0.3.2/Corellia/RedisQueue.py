import redis
import time
try:
    import Husky as Serialib
except ImportError:
    import yajl as Serialib
from uuid import uuid1
import snappy


class Task(object):

    result_prefix = "result"

    def __init__(self, url, method, args, running_timeout, uuid=None, pickler=Serialib):
        self.url = url
        self.method = method
        self.args = args
        self.running_timeout = running_timeout
        self.uuid = uuid or uuid1().hex
        self.pickler = pickler

    def pack(self):
        bytes = self.pickler.dumps([self.url, self.method, self.args, self.running_timeout, self.uuid])
        bytes = snappy.compress(bytes)
        return bytes

    def runwith(self, obj):
        f = getattr(obj, self.method, lambda *args: "No such method: %s" % self.method)
        try:
            self.result = f(*self.args)
        except Exception, e:
            self.result = str(e)

    def packresult(self):
        bytes = self.pickler.dumps(self.result)
        bytes = snappy.compress(bytes)
        return bytes

    @classmethod
    def unpack(cls, dumped, pickler=Serialib):
        dumped = snappy.decompress(dumped)
        return cls(*pickler.loads(dumped), pickler=pickler)

    @classmethod
    def unpackresult(self, res, pickler=Serialib):
        return pickler.loads(snappy.decompress(res))

    def __repr__(self):
        return "%s, %s, %s" % (self.url, self.method, self.uuid)


class ResultAlreadyExpired(Exception):
    pass


class ResultNotReady(object):
    pass


class TaskQueue(object):

    result_ttl=3600
    running_set_name = "running"
    default_running_time = 600

    def __init__(self, host, port, pickler=Serialib):
        # self.redis_pool = redis.ConnectionPool(host=host, port=port, db=0)
        self.redis = redis.StrictRedis(host=host, port=port)
        self.pickler = pickler

    def PUT_TASK(self, task):
        # r = redis.Redis(connection_pool=self.redis_pool)
        p = self.redis.pipeline()
        p.rpush(task.uuid, 0)
        p.rpush(task.url, task.pack())
        p.execute()

    def GET_TASK(self, url):
        # r = redis.Redis(connection_pool=self.redis_pool)
        task = Task.unpack(self.redis.blpop(url, 0)[1], pickler=self.pickler)
        expire_time = time.time() + task.running_timeout
        self.redis.zadd(self.running_set_name, expire_time, task.pack())
        return task

    def PUT_RESULT(self, task):
        # r = redis.Redis(connection_pool=self.redis_pool)
        p = self.redis.pipeline()
        p.rpush(task.uuid, task.packresult())
        p.expire(task.uuid, self.result_ttl)
        p.zrem(self.running_set_name, task.pack())
        p.execute()

    def GET_RESULT(self, task, async):
        if async:
            return task.uuid
        else:
            # r = redis.Redis(connection_pool=self.redis_pool)
            if not self.redis.lpop(task.uuid):
                raise ResultAlreadyExpired
            dumped_result = self.redis.blpop(task.uuid, 0)
            return Task.unpackresult(dumped_result[1], pickler=self.pickler)

    def call(self, url, method, args, **kargs):
        running_timeout = kargs.get("running_timeout", self.default_running_time)
        async = kargs.get("async", False)
        task = Task(url, method, args, running_timeout, pickler=self.pickler)
        self.PUT_TASK(task)
        return self.GET_RESULT(task, async)

    def pop_and_eval(self, url, obj):
        task = self.GET_TASK(url)
        task.runwith(obj)
        self.PUT_RESULT(task)

    def maintain(self, interval=60):
        # r = redis.Redis(connection_pool=self.redis_pool)
        while True:
            current_time = time.time()
            last_time = current_time - interval
            tasks = self.redis.zrangebyscore(self.running_set_name, last_time, current_time)
            for task in tasks:
                original = Task.unpack(task, pickler=self.pickler)
                self.redis.rpush(original.url, task)
                self.redis.zrem(self.running_set_name, task)
            time.sleep(interval)

    def fetch_async_result(self, uuid):
        if not self.redis.lpop(uuid):
            raise ResultAlreadyExpired
        dumped_result = self.redis.blpop(uuid, 0)
        if not dumped_result:
            return ResultNotReady()
        else:
            return Task.unpackresult(dumped_result[1], pickler=self.pickler)

class Worker(object):
    def __init__(self, host, port, url, pickler=Serialib):
        self.queue = TaskQueue(host, port, pickler)
        self.url = url

    def run(self, cls, *args):
        instance = cls(*args)
        instance.worker = self
        while True:
            self.queue.pop_and_eval(self.url, instance)
            

class Client(object):
    def __init__(self, host, port, url, **kargs):
        pickler = kargs.get("pickler", Serialib)
        self.queue = TaskQueue(host, port, pickler)
        self.url = url
        self.kargs = kargs
        if kargs.get("async", False):
            self.fetch_result = lambda uuid: self.queue.fetch_async_result(uuid)

    def __getattr__(self, method):
        return lambda *args: self.queue.call(self.url, method, args, **self.kargs)

