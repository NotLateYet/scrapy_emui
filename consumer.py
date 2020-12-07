import json
import time
from abc import ABCMeta, abstractmethod
from database import *
from utils import *
from logger import *


class BaseConsumer(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.__name = get_rand_name()
        self.logger = Logger('log/consumer_%s.log' % self.__name, level='debug')
        self.key_unfetch = 'unfetch'
        self.key_fetched = 'fetched'
        self.logger.info('Create a consumer(%s).' % self.__name)

    def start(self):
        self.logger.info('Start consume items ...')
        self.do()
        self.logger.info('Consume items end.')

    @abstractmethod
    def do(self):
        pass


class IpConsumer(BaseConsumer):
    def __init__(self):
        super(IpConsumer, self).__init__()

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

    def __do_fetch(self, ip_str):
        dirs = ['IT_VMP_SHA_%d_F', 'IT_VMP_WHU_%d_F', 'IT_VMP_SIA_%d_F', 'IT_VMP_PEK_%d_F', 'T_VMP_WHU_%d_F']
        for dir in dirs:
            for num in range(1, 1000):
                path = dir % num
                parent_path = concat_ip_path(ip_str, path)
                dir_lists = list_dir(ip_str, path)
                if len(dir_lists) == 0:
                    continue
                self.logger.info('Fetching path: %s ...' % parent_path)
                for file_name in dir_lists:
                    if not file_name.startswith('BL'):
                        continue
                    item_json = self.__parse_item(parent_path, file_name)
                    self.logger.info('Find EMUI version: %s' % file_name)
                    DB.redis.rpush(self.key_fetched, item_json)

    def do(self):
        is_sleep = False
        while True:
            ip_str = DB.redis.lpop(self.key_unfetch)
            if ip_str is None:
                if not is_sleep:
                    self.logger.debug('Task queue is empty. waiting ...')
                is_sleep = True
                time.sleep(1)
            else:
                ip_str = bytes_2_str(ip_str)
                self.logger.info('Fetching ip: %s ...' % ip_str)
                self.__do_fetch(ip_str)
                is_sleep = False


if __name__ == '__main__':
    ipp = IpConsumer()
    ipp.start()
