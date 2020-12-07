import json
import time
from abc import ABC, abstractmethod
from database import *
from utils import *
from logger import *


class BaseConsumer(ABC):
    def __init__(self):
        self.__name = get_rand_name()
        self.logger = Logger('consumer.log', level='debug')
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


class IpConsumer(BaseConsumer, ABC):
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

    def __do_fetch(self, values):
        if 'ip' not in values or 'paths' not in values:
            self.logger.error('Not found ip or paths in %s' % json.dumps(values))
            return False
        ip_str = values['ip']
        paths = values['paths']
        for path in paths:
            parent_path = concat_ip_path(ip_str, path)
            for file_name in list_dir(ip_str, path):
                if not file_name.startswith('BL'):
                    continue
                item_json = self.__parse_item(parent_path, file_name)
                DB.redis.rpush(self.key_fetched, item_json)

    def do(self):
        is_sleep = False
        while True:
            value = DB.redis.lpop(self.key_unfetch)
            if value is None:
                if not is_sleep:
                    self.logger.debug('Task queue is empty. waiting ...')
                is_sleep = True
                time.sleep(1)

            else:
                value = bytes_2_str(value)
                self.logger.info('Feaching path %s' % value)
                values = json.loads(value)
                self.__do_fetch(values)
                is_sleep = False


if __name__ == '__main__':
    ipp = IpConsumer()
    ipp.start()
