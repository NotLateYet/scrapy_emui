from dbo.redis_db import *
from dbo.mongo_db import *


class DB(object):
    __REDIS = RedisDB()
    __MONGO = MongoDB()

    redis = __REDIS.client
    mongo = __MONGO
