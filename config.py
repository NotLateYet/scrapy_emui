# -*- coding: UTF-8 -*-
class RedisConfig(object):
    """
    Redis配置信息
    """
    NODES = [
        {'host': '127.0.0.1', 'port': 6379},
    ]
    # 生产者每次获取几个IP进行nmap探测连通性
    PRODUCER_GET_BATCH = 3
    # 当Redis中需要进行探测的ip不足时，则生产者会自动补充ip的个数。
    # 若超过设定的结束IP，则会从开始IP重新补充，以此实现循环爬取
    PRODUCER_PUT_BATCH = 255


class RedisKey(object):
    """
    Redis数据库的关键key
    """
    # 生产者未使用nmap扫描连通性的IP
    UNSCAN_IP = 'scrapy:ip:unscan'
    # 已经经过生产者连通性扫描，但是消费者尚未爬取的IP
    UNFEACH_IP = 'scrapy:ip:unfeach'
    # 消费者爬取完的IP后的结果经过MD5散列后的集合，用于循环爬取时的去重使用。
    RESULT_SET = 'scrapy:ip:set'
    # 分布式锁单独命名
    LOCK = 'scrapy:ip:lock'


class MongoDBConfig(object):
    """
    MongoDB配置信息
    """
    NODES = ['127.0.0.1:27017', ]


class MongDBName(object):
    """
    MongoDB数据库和集合名称
    """
    DB = 'scrapy'
    COLLECTION = 'emui'


class ScanConfig(object):
    """
    nmap扫描的配置信息
    """
    # nmap扫描ip连通性的并发数
    CONCURRENT = 100
