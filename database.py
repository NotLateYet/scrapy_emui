from dbo.redis_db import *
from dbo.mongo_db import *
from config import RedisKey
from utils import str_2_bytes, bytes_2_str


class DB(object):
    __REDIS = RedisDB()
    __MONGO = MongoDB()

    redis = __REDIS.client
    redis_lock = __REDIS.lock
    mongo = __MONGO.client


class UnFetchDAO(object):
    @staticmethod
    def put_hosts(hosts):
        pipe = DB.redis.pipeline()
        for host in hosts:
            pipe.rpush(RedisKey.UNFEACH_IP, str_2_bytes(host))
        pipe.execute()

    @staticmethod
    def get_host():
        ip_str = DB.redis.blpop(RedisKey.UNFEACH_IP)
        if ip_str is None:
            return None
        ip_str = bytes_2_str(ip_str[1])
        return ip_str
