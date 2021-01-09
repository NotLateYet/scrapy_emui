class RedisConfig(object):
    NODES = [
        {'host': '127.0.0.1', 'port': 6379},
    ]
    PRODUCER_GET_BATCH = 1
    PRODUCER_PUT_BATCH = 255


class MongoDBConfig(object):
    NODES = [
        {'host': '127.0.0.1'}
    ]


class ScanConfig(object):
    CONCURRENT = 100


class RedisKey(object):
    UNSCAN_IP = 'scrapy:ip:unscan'
    UNFEACH_IP = 'scrapy:ip:unfeach'
    RESULT_SET = 'scrapy:ip:set'
    LOCK = 'scrapy:ip:lock'
