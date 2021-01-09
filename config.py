class RedisConfig(object):
    NODES = [
        {'host': '127.0.0.1', 'port': 6379},
    ]
    PRODUCER_GET_BATCH = 1
    PRODUCER_PUT_BATCH = 255


class RedisKey(object):
    UNSCAN_IP = 'scrapy:ip:unscan'
    UNFEACH_IP = 'scrapy:ip:unfeach'
    RESULT_SET = 'scrapy:ip:set'
    LOCK = 'scrapy:ip:lock'


class MongoDBConfig(object):
    NODES = ['127.0.0.1:27017', ]


class MongDBName(object):
    DB = 'scrapy'
    COLLECTION = 'emui'


class ScanConfig(object):
    CONCURRENT = 100
