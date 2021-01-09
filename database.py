from dbo.redis_db import *
from dbo.mongo_db import *
from config import RedisKey


class DB(object):
    __REDIS = RedisDB()
    __MONGO = MongoDB()

    redis = __REDIS.client
    redis_lock = __REDIS.lock
    mongo = __MONGO


class UnFetchDAO(object):
    @staticmethod
    def put_hosts(hosts):
        pipe = DB.redis.pipeline()
        for host in hosts:
            pipe.rpush(RedisKey.UNFEACH_IP, bytes(host, encoding='utf8'))
        pipe.execute()

    @staticmethod
    def get_hosts():
        # TODO
        return []
