#coding:utf-8
from hashlib import sha1
from zorm.config import redis


def redis_script(func):
    doc = func.__doc__
    sha = sha1(doc).hexdigest()
    if not redis.script_exists(sha)[0]:
        sha = redis.script_load(doc)
    def _(*args):
        return redis.evalsha(sha, 0, *args)
    _.__doc__ = doc
    return _ 

if __name__ == '__main__':
    redis.delete('test')
    @redis_script
    def test(a, b):
        """
KEYS[1] = "zzzzzzzzzzzzzzzzz"
redis.call('zadd', "test", 1, "z", 2, KEYS[1])
return 1
        """
    print test("z", "zb")
    print redis.zrange('test', 0, -1)
    redis.delete('test')
    redis.script_flush()
    print redis.zrange('test', 0, -1)
