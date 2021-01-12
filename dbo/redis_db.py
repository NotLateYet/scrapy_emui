# -*- coding: UTF-8 -*-
from redis import ConnectionPool, Redis
from redlock import RedLockFactory


class RedisDB(object):
    """
    Redis数据库连接池和Redis分布式锁统一获取入口，当前Redis只支持单节点，可以通过简单修改支持Redis集群
    """
    def __init__(self, nodes):
        assert len(nodes) > 0
        self.__nodes = nodes
        self.__redis_pool = ConnectionPool(host=nodes[0]['host'], port=nodes[0]['port'])
        self.__redis_lock = RedLockFactory(connection_details=nodes)

    @property
    def client(self):
        """
        从Redis连接池中获取Redis客户端实例
        :return: Redis客户端实例
        """
        return Redis(connection_pool=self.__redis_pool)

    @property
    def lock(self):
        """
        从Redis分布式锁工厂中获取实例，用于对并发处理的资源进行安全操作
        :return: Redis分布式锁实例
        """
        return self.__redis_lock

    @property
    def nodes(self):
        """
        获取Redis节点信息
        :return: Redis节点信息
        """
        return self.__nodes


if __name__ == '__main__':
    NODES = [
        {'host': '127.0.0.1', 'port': 6379},
    ]

    redisDB = RedisDB(NODES)
    redisDB.client.rpush('a1', 'bbb')
    redisDB.client.hset('a2', 'ip', bytes([127, 0, 0, 1]))
    import json

    redisDB.client.hset('a3', 'ips', json.dumps({'ip': [127, 0, 0, 1]}))
    res = redisDB.client.sadd('s1', 5)
    print(res)
    redisDB.client.flushall()
