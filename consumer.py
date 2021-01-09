import json
from config import RedisKey, MongDBName
from database import DB, UnFetchDAO
from utils import *
from logger import *
from hashlib import md5


class ResultDAO(object):
    @staticmethod
    def put_item(item_json):
        md5_val = md5(str_2_bytes(item_json)).hexdigest()
        return DB.redis.sadd(RedisKey.RESULT_SET, md5_val) == 1

    @staticmethod
    def save_db(items):
        if items is None or len(items) == 0:
            return
        collection = DB.mongo[MongDBName.DB][MongDBName.COLLECTION]
        for item in items:
            collection.update_one({'key': item['key']}, {'$set': item}, upsert=True)


class IpConsumer(object):
    def __init__(self):
        self.__name = get_rand_name()
        self.logger = Logger('log/consumer_%s.log' % self.__name, level='debug')
        self.logger.info('Create a consumer(%s).' % self.__name)

    def __parse_item(self, parent_path, file_name):
        full_path = os.path.join(parent_path, file_name)
        modify_time = file_create_time(full_path)

        split_nos = file_name.split('_')
        down_no = split_nos[0].replace('BL', '')
        split_brands = split_nos[1].split(' ')
        brand = split_brands[0]
        emui_ver = split_brands[1]
        res = {
            'key': file_name,
            'modify_time': modify_time,
            'down_no': down_no,
            'brand': brand,
            'emui': emui_ver,
            'path': parent_path,
        }
        return res

    def __fetch(self, ip_str):
        # TODO Step1 mount
        mount_path = ''
        items = []
        if len(mount_path) == 0:
            return
        for file_name in os.listdir(mount_path):
            if not file_name.startswith('BL'):
                continue
            item = self.__parse_item(mount_path, file_name)
            self.logger.info('Find EMUI version: %s' % file_name)
            items.append(item)
        return items

    def do(self):
        while True:
            ip_str = UnFetchDAO.get_host()
            self.logger.info('Fetching ip: %s ...' % ip_str)
            items = self.__fetch(ip_str)
            self.logger.info('Update to MongoDB: ')
            ResultDAO.save_db(items)


if __name__ == '__main__':
    ipc = IpConsumer()
    ipc.do()
