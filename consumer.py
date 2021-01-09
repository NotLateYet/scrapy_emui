import json
import time
from database import *
from utils import *
from logger import *
from hashlib import md5


class ResultDAO(object):
    @staticmethod
    def put_item(item_json):
        md5_val = md5(str_2_bytes(item_json)).hexdigest()
        return DB.redis.sadd(RedisKey.RESULT_SET, md5_val) == 1


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
        return json.dumps(res)

    def __fetch(self, ip_str):
        # TODO Step1 mount

        # TODO Step2 list dir

        # TODO Step3 parst each dir

        return []
        # dirs = ['IT_VMP_SHA_%d_F', 'IT_VMP_WHU_%d_F', 'IT_VMP_SIA_%d_F', 'IT_VMP_PEK_%d_F', 'T_VMP_WHU_%d_F']
        # for dir in dirs:
        #     for num in range(1, 1000):
        #         path = dir % num
        #         parent_path = concat_ip_path(ip_str, path)
        #         dir_lists = list_dir(ip_str, path)
        #         if len(dir_lists) == 0:
        #             continue
        #         self.logger.info('Fetching path: %s ...' % parent_path)
        #         for file_name in dir_lists:
        #             if not file_name.startswith('BL'):
        #                 continue
        #             item_json = self.__parse_item(parent_path, file_name)
        #             self.logger.info('Find EMUI version: %s' % file_name)
        #             DB.redis.rpush(self.key_fetched, item_json)

    def do(self):
        while True:
            ip_str = UnFetchDAO.get_host()
            self.logger.info('Fetching ip: %s ...' % ip_str)
            item_json = self.__fetch(ip_str)
            # if ResultDAO.put_item(item_json):
            # TODO update to MongoDB
            self.logger.info('Update to MongoDB: ')


if __name__ == '__main__':
    ipc = IpConsumer()
    ipc.do()
