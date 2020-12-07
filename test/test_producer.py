import producer
import json
from database import *


def test_add():
    ip = [127, 0, 0, 1]
    reach = ['abc']
    # reach_json = json.dumps({'ip': ip, 'paths': reach})
    # DB.redis.rpush('unfetch', reach_json)

    DB.redis.getset('last_ip', bytes[ip])


def test_redis():
    import redis
    print(redis.__version__)


def test_mongo():
    import pymongo
    print(pymongo.__version__)


if __name__ == '__main__':
    test_add()
    test_redis()
    test_mongo()
