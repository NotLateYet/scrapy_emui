import producer
import json
from database import *


def test_add():
    ip = [127, 0, 0, 1]
    reach = ['abc']
    reach_json = json.dumps({'ip': ip, 'paths': reach})
    DB.redis.rpush('unfetch', reach_json)


if __name__ == '__main__':
    test_add()
