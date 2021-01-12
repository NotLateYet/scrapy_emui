# -*- coding: UTF-8 -*-
from hashlib import md5
from ipaddress import ip_address
from dbo.redis_db import *
from dbo.mongo_db import *
from config import *
from utils import str_2_bytes, bytes_2_str, ip_2_str


class DB(object):
    __REDIS = RedisDB(RedisConfig.NODES)
    __MONGO = MongoDB(MongoDBConfig.NODES)

    redis = __REDIS.client
    redis_lock = __REDIS.lock
    mongo = __MONGO.client


class UnFetchDAO(object):
    @staticmethod
    def put_hosts(hosts):
        """
        把生产者扫描到的IP地址存放到Redis的未爬取Key中
        :param hosts: 扫描到的可连通IP
        """
        pipe = DB.redis.pipeline()
        for host in hosts:
            pipe.rpush(RedisKey.UNFEACH_IP, str_2_bytes(host))
        pipe.execute()

    @staticmethod
    def get_host():
        """
        消费者获取未爬取的IP地址
        """
        ip_str = DB.redis.blpop(RedisKey.UNFEACH_IP)
        if ip_str is None:
            return None
        ip_str = bytes_2_str(ip_str[1])
        return ip_str


class ResultDAO(object):
    @staticmethod
    def put_item(item_json):
        """
        消费者爬取结果的MD5散列值存放，用于去重，暂未使用，直接用了MongoDB的upsert特性
        :param item_json: 爬取结果json dump结果
        """
        md5_val = md5(str_2_bytes(item_json)).hexdigest()
        return DB.redis.sadd(RedisKey.RESULT_SET, md5_val) == 1

    @staticmethod
    def check_index():
        """
        检查MongoDB数据库的集合中是否有名为'key'的主键，且是唯一的。若没有则直接退出，且提示用户手动创建唯一主键key
        :return:
        """
        collection = DB.mongo[MongDBName.DB][MongDBName.COLLECTION]
        indexes = collection.index_information()
        if 'key_1' in indexes.keys() and 'unique' in indexes['key_1'] and indexes['key_1']['unique']:
            return True
        else:
            message = 'Please add unique key index for {0}.{1} with: use {0}; db.{1}.'.format(MongDBName.DB,
                                                                                              MongDBName.COLLECTION)
            print(message + 'createIndex({"key": 1}, {"unique": true})')
            return False

    @staticmethod
    def save_db(items):
        """
        消费者爬取结果保存到MongoDB，利用upsert=True特性，若不存在则创建，否则更新。
        :param items: 爬取结果
        """
        if items is None or len(items) == 0:
            return
        collection = DB.mongo[MongDBName.DB][MongDBName.COLLECTION]
        for item in items:
            collection.update_one({'key': item['key']}, {'$set': item}, upsert=True)


class UnScanDAO(object):
    @staticmethod
    def ip_range(start_str, end_str, length):
        """
        根据指定的原始的开始结束IP地址，生成指定个数的具体IP地址列表
        :param start_str: 开始IP地址前三段的字符串
        :param end_str: 结束IP地址前三段的字符串
        :param length: IP地址个数
        :return: 计算出具体的IP地址列表
        """
        start_int = int(ip_address(start_str).packed.hex(), 16)
        end_int = int(ip_address(end_str).packed.hex(), 16)
        range_end_int = min(end_int, start_int + length)
        return [ip_address(ip).exploded for ip in range(start_int, range_end_int)]

    @staticmethod
    def emtpy():
        """
        未扫描IP列表是否为空
        """
        return DB.redis.llen(RedisKey.UNSCAN_IP) == 0

    @staticmethod
    def get_range(length):
        """
        从Redis中获取指定个数的未扫描IP
        :param length: 未扫描IP的个数
        :return: 指定个数的未扫描IP地址
        """
        pipe = DB.redis.pipeline()
        pipe.lrange(RedisKey.UNSCAN_IP, 0, length - 1)
        pipe.ltrim(RedisKey.UNSCAN_IP, length, -1)
        result = pipe.execute()
        if result is None:
            return None
        return [bytes_2_str(ip) for ip in result[0]]

    @staticmethod
    def put_range(start, end, length):
        """
        把生成的未扫描IP地址批量推到Redis
        :param start: 开始IP地址前三段
        :param end: 结束IP地址前三段
        :param length: 生成IP地址个数
        """
        start_str = '0.' + ip_2_str(start[:3])
        end_str = '0.' + ip_2_str(end[:3])
        if start_str == end_str:
            range_strs = [start_str]
        else:
            range_strs = UnScanDAO.ip_range(start_str, end_str, length)
        if len(range_strs) == 0:
            return
        ip3_range_list = [str(ip_str).lstrip('0.') for ip_str in range_strs]
        pipe = DB.redis.pipeline()
        for ip3_str in ip3_range_list:
            pipe.rpush(RedisKey.UNSCAN_IP, str_2_bytes(ip3_str))
        pipe.execute()
