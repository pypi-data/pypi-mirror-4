from redis import StrictRedis
import time
from gevent import sleep
import Husky
from uuid import uuid1
import snappy


class Task(object):

    result_prefix = "result"

    def __init__(self, url, method, args, running_timeout, uuid=None):
        self.url = url
        self.method = method
        self.args = args
        self.running_timeout = running_timeout
        self.uuid = uuid or uuid1().hex

    def pack(self):
        bytes = Husky.dumps([self.url, self.method, self.args, self.running_timeout, self.uuid])
        bytes = snappy.compress(bytes)
        return bytes

    def runwith(self, obj):
        f = getattr(obj, self.method, lambda *args: "No such method: %s" % self.method)
        try:
            self.result = f(*self.args)
        except Exception, e:
            self.result = str(e)

    def packresult(self):
        bytes = Husky.dumps(self.result)
        bytes = snappy.compress(bytes)
        return bytes

    @classmethod
    def unpack(cls, dumped):
        dumped = snappy.decompress(dumped)
        return cls(*Husky.loads(dumped))

    @classmethod
    def unpackresult(self, res):
        return Husky.loads(snappy.decompress(res))

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

    def __init__(self, host, port):
        self.redis = StrictRedis(host, port)

    def PUT_TASK(self, task):
        self.redis.rpush(task.url, task.pack())
        self.redis.rpush(task.uuid, 0)

    def GET_TASK(self, url):
        task = Task.unpack(self.redis.blpop(url, 0)[1])
        expire_time = time.time() + task.running_timeout
        self.redis.zadd(self.running_set_name, expire_time, task.pack())
        return task

    def PUT_RESULT(self, task):
        self.redis.rpush(task.uuid, task.packresult())
        self.redis.expire(task.uuid, self.result_ttl)
        self.redis.zrem(self.running_set_name, task.pack())

    def GET_RESULT(self, task, async):
        if not self.redis.lpop(task.uuid):
            raise ResultAlreadyExpired
        if async:
            def getvalue():
                dumped_result = self.redis.rpop(task.uuid)
                if not dumped_result:
                    return ResultNotReady()
                else:
                    return Task.unpackresult(dumped_result)
            return getvalue
        else:
            dumped_result = self.redis.blpop(task.uuid, 0)[1]
            return Task.unpackresult(dumped_result)

    def call(self, url, method, args, **kargs):
        running_timeout = kargs.get("running_timeout", self.default_running_time)
        async = kargs.get("async", False)
        task = Task(url, method, args, running_timeout)
        self.PUT_TASK(task)
        return self.GET_RESULT(task, async)

    def pop_and_eval(self, url, obj):
        task = self.GET_TASK(url)
        task.runwith(obj)
        self.PUT_RESULT(task)

    def maintain(self, interval=60):
        while True:
            current_time = time.time()
            last_time = current_time - interval
            tasks = self.redis.zrangebyscore(self.running_set_name, last_time, current_time)
            for task in tasks:
                original = Task.unpack(task)
                self.redis.rpush(original.url, task)
                self.redis.zrem(self.running_set_name, task)
            sleep(interval)


class Worker(object):
    def __init__(self, host, port, url):
        self.queue = TaskQueue(host, port)
        self.url = url

    def run(self, cls, *args):
        instance = cls(*args)
        instance.worker = self
        while True:
            self.queue.pop_and_eval(self.url, instance)
            

class Client(object):
    def __init__(self, host, port, url, **kargs):
        self.queue = TaskQueue(host, port)
        self.url = url
        self.kargs = kargs

    def __getattr__(self, method):
        return lambda *args: self.queue.call(self.url, method, args, **self.kargs)

